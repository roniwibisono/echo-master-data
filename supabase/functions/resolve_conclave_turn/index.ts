import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

type JsonMap = Record<string, unknown>;

type MatchRow = {
  id: string;
  season_id: number;
  mode: "duel" | "strategic";
  queue_type: "ranked" | "casual";
  status: "forming" | "active" | "resolving" | "finished" | "cancelled";
  round: number;
  turn_deadline: string | null;
  rng_seed: string;
  state: JsonMap;
};

type PlayerRow = {
  match_id: string;
  uid: string;
  side: 1 | 2;
  faction_id: number;
  cr_snapshot: number;
  locked_round: number;
  is_echo?: boolean;
  team_snapshot: JsonMap[] | null;
};

type ActionRow = {
  match_id: string;
  round: number;
  uid: string;
  actor_id: string;
  action: JsonMap;
  locked: boolean;
};

type SkillRow = {
  id: string;
  name: string;
  mp_cost: number;
  damage_formula: string | null;
  target_attack: string | null;
  target_effect: string | null;
  special_effects: JsonMap[] | null;
  skill_description: string | null;
  effect: string | null;
};

type Actor = {
  actor_id: string;
  owner_uid: string;
  side: 1 | 2;
  name: string;
  level: number;
  current_hp: number;
  max_hp: number;
  current_mp: number;
  max_mp: number;
  atk: number;
  def: number;
  agi: number;
  per: number;
  skill_ids: string[];
  defending?: boolean;
};

type BattleEvent = {
  event_type: string;
  payload: JsonMap;
};

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!supabaseUrl || !anonKey || !serviceKey) {
      throw new HttpError(500, "missing_supabase_env");
    }

    const authHeader = req.headers.get("Authorization") ?? "";
    const userClient = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: authHeader } },
    });
    const admin = createClient(supabaseUrl, serviceKey);

    const { data: userData, error: userError } = await userClient.auth.getUser();
    if (userError || !userData.user) throw new HttpError(401, "not_authenticated");

    const body = await req.json().catch(() => ({}));
    const matchId = String(body.match_id ?? body.matchId ?? "");
    if (!isUuidLike(matchId)) throw new HttpError(400, "invalid_match_id");

    const { data: match, error: matchError } = await admin
      .from("conclave_matches")
      .select("*")
      .eq("id", matchId)
      .returns<MatchRow>()
      .maybeSingle();
    if (matchError) throw matchError;
    if (!match) throw new HttpError(404, "match_not_found");
    if (match.status === "finished" || match.status === "cancelled") {
      return json({ ok: true, status: match.status, already_terminal: true });
    }

    const { data: players, error: playersError } = await admin
      .from("conclave_match_players")
      .select("*")
      .eq("match_id", matchId)
      .returns<PlayerRow[]>();
    if (playersError) throw playersError;
    const participantRows = players ?? [];
    if (!participantRows.some((p) => p.uid === userData.user.id)) {
      throw new HttpError(403, "not_match_participant");
    }
    if (participantRows.length < 2) throw new HttpError(409, "match_not_ready");

    const deadlineExpired = match.turn_deadline
      ? Date.now() >= new Date(match.turn_deadline).getTime()
      : false;
    const bothLocked = participantRows.every((p) => p.locked_round >= match.round);
    if (!bothLocked && !deadlineExpired) {
      return json({ ok: true, status: "waiting_for_actions" }, 202);
    }

    const previousResolved = Number((match.state ?? {}).last_resolved_round ?? 0);
    if (previousResolved >= match.round) {
      return json({ ok: true, status: "already_resolved", round: match.round });
    }

    const { data: actionRows, error: actionsError } = await admin
      .from("conclave_turn_actions")
      .select("*")
      .eq("match_id", matchId)
      .eq("round", match.round)
      .returns<ActionRow[]>();
    if (actionsError) throw actionsError;

    const actors = loadActors(match, participantRows);
    if (actors.length === 0) throw new HttpError(422, "empty_team_snapshot");

    const skillIds = [
      ...new Set(
        actionRows
          ?.map((row) => row.action?.skill_id)
          .filter((id): id is string => typeof id === "string" && id.length > 0) ??
          [],
      ),
    ];
    const skillMap = await loadSkills(admin, skillIds);

    const events: BattleEvent[] = [];
    const actionsByActor = normalizeActions(
      actors,
      participantRows,
      actionRows ?? [],
      deadlineExpired,
      events,
    );

    resetTurnFlags(actors);
    const rng = seededRandom(`${match.rng_seed}:${match.round}`);
    const initiative = new Map(
      actors
        .filter((actor) => actor.current_hp > 0)
        .map((actor) => [actor.actor_id, actor.agi + Math.floor(rng() * 21)]),
    );
    const order = actors
      .filter((actor) => actor.current_hp > 0)
      .sort((a, b) => {
        const priority = actionPriority(actionsByActor, skillMap, b) -
          actionPriority(actionsByActor, skillMap, a);
        if (priority !== 0) return priority;
        return (initiative.get(b.actor_id) ?? 0) -
          (initiative.get(a.actor_id) ?? 0);
      });

    for (const actor of order) {
      if (actor.current_hp <= 0) continue;
      if (sideDefeated(actors, enemySide(actor.side))) break;
      const action = actionsByActor.get(actor.actor_id) ?? { type: "defend" };
      resolveAction(match, actors, actor, action, skillMap, rng, events);
    }

    const winnerSide = sideDefeated(actors, 1)
      ? 2
      : sideDefeated(actors, 2)
      ? 1
      : null;
    const winnerUid = winnerSide
      ? participantRows.find((p) => p.side === winnerSide)?.uid ?? null
      : null;

    if (winnerUid && match.queue_type === "ranked") {
      await updateRatings(admin, match, participantRows, winnerUid, events);
    }

    const nextState: JsonMap = {
      ...(match.state ?? {}),
      teams: {
        "1": actors.filter((a) => a.side === 1).map(serializeActor),
        "2": actors.filter((a) => a.side === 2).map(serializeActor),
      },
      turn_locks: {},
      last_resolved_round: match.round,
      last_resolved_at: new Date().toISOString(),
      winner_uid: winnerUid,
    };

    await admin
      .from("conclave_match_events")
      .delete()
      .eq("match_id", matchId)
      .eq("round", match.round);

    const eventRows = events.map((event, index) => ({
      match_id: matchId,
      round: match.round,
      seq: index + 1,
      event_type: event.event_type,
      payload: event.payload,
    }));
    eventRows.push({
      match_id: matchId,
      round: match.round,
      seq: eventRows.length + 1,
      event_type: "round_resolved",
      payload: {
        text: winnerUid
          ? `Match finished. Winner: side ${winnerSide}.`
          : `Round ${match.round} resolved.`,
        winner_uid: winnerUid,
      },
    });

    const { error: insertEventsError } = await admin
      .from("conclave_match_events")
      .insert(eventRows);
    if (insertEventsError) throw insertEventsError;

    const nextRound = winnerUid ? match.round : match.round + 1;
    const { error: updateMatchError } = await admin
      .from("conclave_matches")
      .update({
        status: winnerUid ? "finished" : "active",
        winner_uid: winnerUid,
        finished_at: winnerUid ? new Date().toISOString() : null,
        round: nextRound,
        turn_deadline: winnerUid
          ? null
          : new Date(Date.now() + 30_000).toISOString(),
        state: nextState,
      })
      .eq("id", matchId);
    if (updateMatchError) throw updateMatchError;

    return json({
      ok: true,
      status: winnerUid ? "finished" : "active",
      resolved_round: match.round,
      next_round: nextRound,
      winner_uid: winnerUid,
    });
  } catch (error) {
    const status = error instanceof HttpError ? error.status : 500;
    const message = error instanceof Error ? error.message : String(error);
    return json({ ok: false, error: message }, status);
  }
});

function json(payload: JsonMap, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

function loadActors(match: MatchRow, players: PlayerRow[]): Actor[] {
  const stateTeams = match.state?.teams as JsonMap | undefined;
  const actors: Actor[] = [];
  if (stateTeams && typeof stateTeams === "object") {
    for (const side of [1, 2] as const) {
      const rows = stateTeams[String(side)];
      if (!Array.isArray(rows)) continue;
      const ownerUid = players.find((p) => p.side === side)?.uid ?? "";
      rows.forEach((row, index) => {
        actors.push(normalizeActor(row as JsonMap, ownerUid, side, index));
      });
    }
    if (actors.length > 0) return actors;
  }

  for (const player of players) {
    const snapshot = Array.isArray(player.team_snapshot)
      ? player.team_snapshot
      : [];
    snapshot.forEach((row, index) => {
      actors.push(normalizeActor(row, player.uid, player.side, index));
    });
  }
  return actors;
}

function normalizeActor(
  raw: JsonMap,
  ownerUid: string,
  side: 1 | 2,
  index: number,
): Actor {
  const stats = (raw.stats ?? raw.effective_stats ?? raw.base_stats ?? {}) as JsonMap;
  const maxHp = intValue(raw.max_hp ?? raw.maxHp ?? raw.hp ?? stats.hp, 100);
  const maxMp = intValue(raw.max_mp ?? raw.maxMp ?? raw.mp ?? stats.mp, 30);
  return {
    actor_id: String(raw.actor_id ?? raw.id ?? `${ownerUid}:${index}`),
    owner_uid: String(raw.owner_uid ?? ownerUid),
    side,
    name: String(raw.name ?? `Actor ${index + 1}`),
    level: intValue(raw.level, 1),
    current_hp: clampInt(intValue(raw.current_hp ?? raw.currentHp, maxHp), 0, maxHp),
    max_hp: maxHp,
    current_mp: clampInt(intValue(raw.current_mp ?? raw.currentMp, maxMp), 0, maxMp),
    max_mp: maxMp,
    atk: intValue(raw.atk ?? stats.atk, 10),
    def: intValue(raw.def ?? stats.def, 8),
    agi: intValue(raw.agi ?? stats.agi, 8),
    per: intValue(raw.per ?? stats.per, 8),
    skill_ids: stringArray(raw.skill_ids ?? raw.skillIds ?? raw.skills),
    defending: Boolean(raw.defending),
  };
}

function normalizeActions(
  actors: Actor[],
  players: PlayerRow[],
  rows: ActionRow[],
  deadlineExpired: boolean,
  events: BattleEvent[],
): Map<string, JsonMap> {
  const result = new Map<string, JsonMap>();
  const playerMap = new Map(players.map((p) => [p.uid, p]));
  for (const row of rows) {
    const player = playerMap.get(row.uid);
    const actor = actors.find((a) => a.actor_id === row.actor_id);
    if (!player || !actor || actor.owner_uid !== row.uid) {
      events.push(logEvent("action_rejected", "Invalid actor ownership.", {
        actor_id: row.actor_id,
        uid: row.uid,
      }));
      continue;
    }
    result.set(actor.actor_id, row.action);
  }

  for (const actor of actors) {
    if (actor.current_hp <= 0 || result.has(actor.actor_id)) continue;
    const owner = playerMap.get(actor.owner_uid);
    if (owner?.is_echo) {
      const target = actors.find((targetActor) =>
        targetActor.side !== actor.side && targetActor.current_hp > 0
      );
      result.set(actor.actor_id, {
        type: "attack",
        target_id: target?.actor_id,
        ai: true,
      });
      events.push(logEvent("ai_action", `${actor.name} commits an attack.`));
    } else {
      result.set(actor.actor_id, { type: "defend", auto: true });
      events.push(
        logEvent(
          "auto_defend",
          deadlineExpired
            ? `${actor.name} auto-defends after timeout.`
            : `${actor.name} auto-defends missing action.`,
        ),
      );
    }
  }
  return result;
}

async function loadSkills(
  admin: ReturnType<typeof createClient>,
  skillIds: string[],
): Promise<Map<string, SkillRow>> {
  if (skillIds.length === 0) return new Map();
  const { data, error } = await admin
    .from("skills")
    .select(
      "id,name,mp_cost,damage_formula,target_attack,target_effect,special_effects,skill_description,effect",
    )
    .in("id", skillIds)
    .returns<SkillRow[]>();
  if (error) throw error;
  return new Map((data ?? []).map((skill) => [skill.id, skill]));
}

function resolveAction(
  match: MatchRow,
  actors: Actor[],
  actor: Actor,
  action: JsonMap,
  skillMap: Map<string, SkillRow>,
  rng: () => number,
  events: BattleEvent[],
) {
  const type = String(action.type ?? "defend");
  if (type === "defend") {
    defend(actor, events);
    return;
  }

  if (type === "item") {
    defend(actor, events);
    events.push(
      logEvent(
        "item_blocked",
        `${actor.name}'s item action was blocked until server inventory validation is enabled.`,
        { actor_id: actor.actor_id, queue_type: match.queue_type },
      ),
    );
    return;
  }

  if (type === "skill") {
    const skillId = String(action.skill_id ?? "");
    const skill = skillMap.get(skillId);
    if (!skill || !actor.skill_ids.includes(skillId)) {
      events.push(
        logEvent("skill_rejected", `${actor.name} cannot use that skill.`, {
          actor_id: actor.actor_id,
          skill_id: skillId,
        }),
      );
      defend(actor, events);
      return;
    }
    if (actor.current_mp < skill.mp_cost) {
      events.push(logEvent("mp_failed", `${actor.name} lacks MP for ${skill.name}.`));
      defend(actor, events);
      return;
    }
    actor.current_mp -= skill.mp_cost;
    const targets = resolveTargets(actors, actor, action, skill);
    if (targets.length === 0) {
      events.push(logEvent("target_failed", `${actor.name} has no valid target.`));
      defend(actor, events);
      return;
    }
    const scale = formulaScale(skill.damage_formula, actor);
    const targetAttack = String(skill.target_attack ?? "").toLowerCase();
    events.push(logEvent("skill", `${actor.name} uses ${skill.name}.`, {
      actor_id: actor.actor_id,
      skill_id: skill.id,
    }));
    if (targetAttack === "none" || targetAttack === "self") {
      for (const target of targets) {
        const healed = heal(target, Math.max(1, Math.round(scale * 0.7)));
        events.push(logEvent("heal", `${target.name} restores ${healed} HP.`, {
          target_id: target.actor_id,
          amount: healed,
        }));
      }
      return;
    }
    for (const target of targets) {
      attack(actor, target, scale, rng, events, skill.id);
    }
    return;
  }

  const target = findTarget(actors, actor, String(action.target_id ?? ""));
  if (!target) {
    events.push(logEvent("target_failed", `${actor.name} has no valid target.`));
    defend(actor, events);
    return;
  }
  attack(actor, target, actor.atk, rng, events);
}

function attack(
  attacker: Actor,
  defender: Actor,
  basePower: number,
  rng: () => number,
  events: BattleEvent[],
  skillId?: string,
) {
  const hitChance = clamp(75 + (attacker.per - defender.agi) * 0.5, 15, 98);
  if (rng() * 100 > hitChance) {
    events.push(logEvent("miss", `${attacker.name} misses ${defender.name}.`, {
      source_id: attacker.actor_id,
      target_id: defender.actor_id,
      skill_id: skillId,
    }));
    return;
  }

  const dodgeChance = clamp(5 + (defender.agi - attacker.per) * 0.25, 0, 35);
  if (rng() * 100 < dodgeChance) {
    events.push(logEvent("dodge", `${defender.name} dodges ${attacker.name}.`, {
      source_id: attacker.actor_id,
      target_id: defender.actor_id,
      skill_id: skillId,
    }));
    return;
  }

  const critChance = clamp(5 + attacker.per * 0.03, 5, 30);
  const crit = rng() * 100 < critChance;
  const blockChance = clamp(3 + defender.def * 0.02, 3, 25);
  const block = rng() * 100 < blockChance;
  let damage = Math.max(1, Math.round(basePower - defender.def * 0.45));
  if (crit) damage = Math.round(damage * 1.5);
  if (defender.defending) damage = Math.round(damage * 0.7);
  if (block) damage = Math.max(1, Math.round(damage * 0.65));

  defender.current_hp = Math.max(0, defender.current_hp - damage);
  events.push(logEvent(crit ? "crit" : block ? "block" : "hit", `${attacker.name} hits ${defender.name} for ${damage}.`, {
    source_id: attacker.actor_id,
    target_id: defender.actor_id,
    skill_id: skillId,
    amount: damage,
    critical: crit,
    block,
    hp_after: defender.current_hp,
  }));
  if (defender.current_hp <= 0) {
    events.push(logEvent("down", `${defender.name} is down.`, {
      target_id: defender.actor_id,
    }));
  }
}

function defend(actor: Actor, events: BattleEvent[]) {
  actor.defending = true;
  const restored = Math.max(1, Math.ceil(actor.max_mp * 0.05));
  actor.current_mp = Math.min(actor.max_mp, actor.current_mp + restored);
  events.push(logEvent("defend", `${actor.name} defends. MP +${restored}.`, {
    actor_id: actor.actor_id,
    mp_restored: restored,
  }));
}

function resolveTargets(
  actors: Actor[],
  actor: Actor,
  action: JsonMap,
  skill: SkillRow,
): Actor[] {
  const targetAttack = String(skill.target_attack ?? "enemy").toLowerCase()
    .replaceAll(" ", "_");
  const targetId = String(action.target_id ?? "");
  const allies = actors.filter((a) => a.side === actor.side && a.current_hp > 0);
  const enemies = actors.filter((a) => a.side !== actor.side && a.current_hp > 0);
  if (targetAttack === "self") return [actor];
  if (targetAttack.includes("ally") && targetAttack.includes("all")) return allies;
  if (targetAttack.includes("enemy") && targetAttack.includes("all")) {
    return enemies;
  }
  if (targetAttack.includes("aoe")) return enemies;
  if (targetAttack.includes("ally")) {
    return [allies.find((a) => a.actor_id === targetId) ?? actor];
  }
  if (targetAttack === "none") {
    const targetEffect = String(skill.target_effect ?? "self").toLowerCase();
    if (targetEffect.includes("ally") && targetEffect.includes("all")) return allies;
    if (targetEffect.includes("ally")) {
      return [allies.find((a) => a.actor_id === targetId) ?? actor];
    }
    return [actor];
  }
  const target = findTarget(actors, actor, targetId);
  return target ? [target] : [];
}

function findTarget(actors: Actor[], actor: Actor, targetId: string): Actor | null {
  const enemies = actors.filter((a) => a.side !== actor.side && a.current_hp > 0);
  return enemies.find((a) => a.actor_id === targetId) ?? enemies[0] ?? null;
}

function actionPriority(
  actionsByActor: Map<string, JsonMap>,
  skillMap: Map<string, SkillRow>,
  actor: Actor,
): number {
  const action = actionsByActor.get(actor.actor_id);
  if (String(action?.type ?? "") !== "skill") return 0;
  const skill = skillMap.get(String(action?.skill_id ?? ""));
  if (!skill) return 0;
  const text = `${skill.skill_description ?? ""} ${skill.effect ?? ""}`
    .toLowerCase();
  const special = skill.special_effects ?? [];
  const tagged = special.some((effect) => {
    const type = String(effect.type ?? "").toLowerCase();
    return type.includes("first") || type.includes("initiative") ||
      type.includes("priority");
  });
  return tagged || text.includes("always first") || text.includes("acts first") ||
      text.includes("jalan pertama")
    ? 100
    : 0;
}

async function updateRatings(
  admin: ReturnType<typeof createClient>,
  match: MatchRow,
  players: PlayerRow[],
  winnerUid: string,
  events: BattleEvent[],
) {
  for (const player of players) {
    if (player.is_echo) continue;
    const won = player.uid === winnerUid;
    const { data: rating } = await admin
      .from("conclave_ratings")
      .select("*")
      .eq("uid", player.uid)
      .eq("season_id", match.season_id)
      .returns<JsonMap>()
      .maybeSingle();
    const currentCr = intValue(rating?.cr, 1000);
    const delta = currentCr >= 1800 ? (won ? 15 : -18) : currentCr >= 1400
      ? (won ? 18 : -18)
      : (won ? 22 : -18);
    const newCr = clampInt(currentCr + delta, 0, 9999);
    await admin.from("conclave_ratings").upsert({
      uid: player.uid,
      season_id: match.season_id,
      cr: newCr,
      tier: tierForCr(newCr),
      wins: intValue(rating?.wins, 0) + (won ? 1 : 0),
      losses: intValue(rating?.losses, 0) + (won ? 0 : 1),
      win_streak: won ? intValue(rating?.win_streak, 0) + 1 : 0,
      placement_matches: Math.min(5, intValue(rating?.placement_matches, 0) + 1),
      is_placed: intValue(rating?.placement_matches, 0) + 1 >= 5,
    });
    try {
      await admin.rpc("increment_conclave_influence", {
        p_faction_id: player.faction_id,
        p_season_id: match.season_id,
        p_amount: won ? 100 : 20,
      });
    } catch (_) {
      // Influence is secondary to match settlement; do not fail resolution.
    }
    events.push(logEvent("rating", `${won ? "Winner" : "Defeated player"} CR ${currentCr} -> ${newCr}.`, {
      uid: player.uid,
      delta,
      cr: newCr,
    }));
  }
}

function formulaScale(formula: string | null, actor: Actor): number {
  if (!formula) return actor.atk * 1.2;
  const normalized = formula.toUpperCase();
  const stat = normalized.includes("DEF")
    ? actor.def
    : normalized.includes("AGI")
    ? actor.agi
    : normalized.includes("PER")
    ? actor.per
    : actor.atk;
  const multiplierMatch = normalized.match(/\*\s*([0-9]+(?:\.[0-9]+)?)/);
  const plusMatch = normalized.match(/\+\s*([0-9]+)/);
  const multiplier = multiplierMatch ? Number(multiplierMatch[1]) : 1;
  const flat = plusMatch ? Number(plusMatch[1]) : 0;
  return stat * multiplier + flat;
}

function resetTurnFlags(actors: Actor[]) {
  for (const actor of actors) actor.defending = false;
}

function serializeActor(actor: Actor): JsonMap {
  return { ...actor };
}

function logEvent(event_type: string, text: string, extra: JsonMap = {}): BattleEvent {
  return { event_type, payload: { text, ...extra } };
}

function sideDefeated(actors: Actor[], side: 1 | 2): boolean {
  return actors.filter((a) => a.side === side).every((a) => a.current_hp <= 0);
}

function enemySide(side: 1 | 2): 1 | 2 {
  return side === 1 ? 2 : 1;
}

function heal(actor: Actor, amount: number): number {
  const before = actor.current_hp;
  actor.current_hp = Math.min(actor.max_hp, actor.current_hp + amount);
  return actor.current_hp - before;
}

function seededRandom(seed: string): () => number {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return () => {
    h += h << 13;
    h ^= h >>> 7;
    h += h << 3;
    h ^= h >>> 17;
    h += h << 5;
    return (h >>> 0) / 4294967296;
  };
}

function intValue(value: unknown, fallback: number): number {
  if (typeof value === "number" && Number.isFinite(value)) return Math.round(value);
  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return Math.round(parsed);
  }
  return fallback;
}

function stringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item)).filter((item) => item.length > 0);
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function clampInt(value: number, min: number, max: number): number {
  return Math.round(clamp(value, min, max));
}

function tierForCr(cr: number): string {
  if (cr >= 2000) return "Nexus Lord";
  if (cr >= 1800) return "Ascendant";
  if (cr >= 1600) return "Champion";
  if (cr >= 1400) return "Elite";
  if (cr >= 1200) return "Vanguard";
  return "Recruit";
}

function isUuidLike(value: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    .test(value);
}

class HttpError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}
