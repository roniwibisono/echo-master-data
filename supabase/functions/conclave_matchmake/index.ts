import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

type JsonMap = Record<string, unknown>;

type SaveRow = {
  profile: JsonMap | null;
  allies: JsonMap[] | null;
  party: JsonMap | null;
};

type RatingRow = {
  cr: number;
};

type QueueRow = {
  id: string;
  uid: string;
  season_id: number;
  mode: "duel" | "strategic";
  queue_type: "ranked" | "casual";
  cr: number;
  faction_id: number;
  team_snapshot: JsonMap[];
};

type BotRow = {
  bot_uid: string;
  code: string;
  display_name: string;
  rank_label: string;
  difficulty: string;
  cr: number;
  faction_id: number;
  team_snapshot: JsonMap[];
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
    const mode = normalizeMode(body.mode);
    const queueType = normalizeQueueType(body.queue_type ?? body.queueType);
    const seasonId = intValue(body.season_id ?? body.seasonId, 1);
    const allowEcho = body.allow_echo === true || body.allowEcho === true;
    const uid = userData.user.id;

    const { data: save, error: saveError } = await admin
      .from("player_saves")
      .select("profile,allies,party")
      .eq("uid", uid)
      .returns<SaveRow>()
      .maybeSingle();
    if (saveError) throw saveError;
    if (!save?.profile) throw new HttpError(422, "player_save_not_found");

    const { data: rating } = await admin
      .from("conclave_ratings")
      .select("cr")
      .eq("uid", uid)
      .eq("season_id", seasonId)
      .returns<RatingRow>()
      .maybeSingle();

    const cr = intValue(rating?.cr, 1000);
    const factionId = intValue(save.profile.faction_id, 0);
    const team = buildTeamSnapshot(uid, save, mode);
    if (team.length === 0) throw new HttpError(422, "empty_team_snapshot");

    await expireOldQueues(admin);

    const opponent = await claimOpponent(
      admin,
      uid,
      seasonId,
      mode,
      queueType,
      cr,
    );

    if (opponent) {
      const matchId = await createMatch(admin, {
        seasonId,
        mode,
        queueType,
        side1: {
          uid,
          cr,
          factionId,
          team,
          isEcho: false,
        },
        side2: {
          uid: opponent.uid,
          cr: opponent.cr,
          factionId: opponent.faction_id,
          team: opponent.team_snapshot,
          isEcho: false,
        },
      });

      await admin
        .from("conclave_match_queue")
        .update({ status: "matched", match_id: matchId })
        .in("id", [opponent.id]);

      return json({
        ok: true,
        status: "matched",
        match_id: matchId,
        echo: false,
        enemy_avg_cr: opponent.cr,
        enemy_faction_id: opponent.faction_id,
      });
    }

    if (allowEcho) {
      const bot = await selectBot(admin, mode, queueType, cr);
      const echoUid = bot?.bot_uid ?? crypto.randomUUID();
      const echoTeam = bot
        ? prepareBotTeam(bot, mode)
        : buildEchoTeam(echoUid, team, cr, mode);
      const enemyFactionId = bot?.faction_id ??
        (factionId === 7 ? 1 : Math.max(1, factionId + 1));
      const enemyCr = bot?.cr ?? cr;
      const matchId = await createMatch(admin, {
        seasonId,
        mode,
        queueType,
        side1: { uid, cr, factionId, team, isEcho: false },
        side2: {
          uid: echoUid,
          cr: enemyCr,
          factionId: enemyFactionId,
          team: echoTeam,
          isEcho: true,
        },
      });

      if (bot) {
        try {
          await admin
            .from("conclave_bots")
            .update({ last_used_at: new Date().toISOString() })
            .eq("bot_uid", bot.bot_uid);
        } catch (_) {
          // Non-critical telemetry; matchmaking should not fail if this write fails.
        }
      }

      return json({
        ok: true,
        status: "matched",
        match_id: matchId,
        echo: true,
        bot_code: bot?.code ?? null,
        bot_name: bot?.display_name ?? "Echo Rival",
        bot_rank: bot?.rank_label ?? null,
        bot_difficulty: bot?.difficulty ?? "normal",
        enemy_avg_cr: enemyCr,
        enemy_faction_id: enemyFactionId,
      });
    }

    const queuePayload = {
      uid,
      season_id: seasonId,
      mode,
      queue_type: queueType,
      status: "queued",
      cr,
      faction_id: factionId,
      team_snapshot: team,
      match_id: null,
      expires_at: new Date(Date.now() + 120_000).toISOString(),
    };
    const { data: updatedQueue, error: updateQueueError } = await admin
      .from("conclave_match_queue")
      .update(queuePayload)
      .eq("uid", uid)
      .eq("season_id", seasonId)
      .eq("mode", mode)
      .eq("queue_type", queueType)
      .eq("status", "queued")
      .select("id");
    if (updateQueueError) throw updateQueueError;
    if ((updatedQueue?.length ?? 0) === 0) {
      const { error: insertQueueError } = await admin
        .from("conclave_match_queue")
        .insert(queuePayload);
      if (insertQueueError) throw insertQueueError;
    }

    return json({ ok: true, status: "queued" }, 202);
  } catch (error) {
    const status = error instanceof HttpError ? error.status : 500;
    const message = errorToMessage(error);
    console.error("conclave_matchmake failed", message, error);
    return json({ ok: false, error: message }, status);
  }
});

async function claimOpponent(
  admin: ReturnType<typeof createClient>,
  uid: string,
  seasonId: number,
  mode: "duel" | "strategic",
  queueType: "ranked" | "casual",
  cr: number,
): Promise<QueueRow | null> {
  const crWindow = queueType === "ranked" ? 350 : 9999;
  const { data, error } = await admin
    .from("conclave_match_queue")
    .select("*")
    .eq("status", "queued")
    .eq("season_id", seasonId)
    .eq("mode", mode)
    .eq("queue_type", queueType)
    .neq("uid", uid)
    .gte("cr", cr - crWindow)
    .lte("cr", cr + crWindow)
    .gt("expires_at", new Date().toISOString())
    .order("created_at", { ascending: true })
    .limit(1)
    .returns<QueueRow[]>();
  if (error) throw error;
  const opponent = data?.[0];
  if (!opponent) return null;

  const { data: claimed, error: claimError } = await admin
    .from("conclave_match_queue")
    .update({ status: "matched" })
    .eq("id", opponent.id)
    .eq("status", "queued")
    .select("*")
    .returns<QueueRow[]>();
  if (claimError) throw claimError;
  return claimed?.[0] ?? null;
}

async function selectBot(
  admin: ReturnType<typeof createClient>,
  mode: "duel" | "strategic",
  queueType: "ranked" | "casual",
  cr: number,
): Promise<BotRow | null> {
  const { data, error } = await admin
    .from("conclave_bots")
    .select(
      "bot_uid,code,display_name,rank_label,difficulty,cr,faction_id,team_snapshot",
    )
    .eq("active", true)
    .in("mode", ["both", mode])
    .returns<BotRow[]>();
  if (error) return null;
  const bots = data ?? [];
  if (bots.length === 0) return null;

  const rankedWindow = 420;
  const candidates = queueType === "ranked"
    ? bots.filter((bot) => Math.abs(bot.cr - cr) <= rankedWindow)
    : bots;
  const pool = candidates.length > 0 ? candidates : bots;
  pool.sort((a, b) => {
    const diff = Math.abs(a.cr - cr) - Math.abs(b.cr - cr);
    if (diff !== 0) return diff;
    return a.code.localeCompare(b.code);
  });
  return pool[Math.floor(Math.random() * Math.min(5, pool.length))] ?? null;
}

async function createMatch(
  admin: ReturnType<typeof createClient>,
  args: {
    seasonId: number;
    mode: "duel" | "strategic";
    queueType: "ranked" | "casual";
    side1: MatchSide;
    side2: MatchSide;
  },
): Promise<string> {
  const { data: match, error: matchError } = await admin
    .from("conclave_matches")
    .insert({
      season_id: args.seasonId,
      mode: args.mode,
      queue_type: args.queueType,
      status: "active",
      round: 1,
      participant_a: args.side1.uid,
      participant_b: args.side2.uid,
      turn_deadline: new Date(Date.now() + 30_000).toISOString(),
      state: {
        teams: {
          "1": args.side1.team,
          "2": args.side2.team,
        },
        turn_locks: {},
        created_by: "conclave_matchmake",
      },
    })
    .select("id")
    .single();
  if (matchError) throw matchError;
  const matchId = String(match.id);

  const { error: playersError } = await admin
    .from("conclave_match_players")
    .insert([
      {
        match_id: matchId,
        uid: args.side1.uid,
        side: 1,
        faction_id: args.side1.factionId,
        cr_snapshot: args.side1.cr,
        team_snapshot: args.side1.team,
        is_echo: args.side1.isEcho,
      },
      {
        match_id: matchId,
        uid: args.side2.uid,
        side: 2,
        faction_id: args.side2.factionId,
        cr_snapshot: args.side2.cr,
        team_snapshot: args.side2.team,
        is_echo: args.side2.isEcho,
      },
    ]);
  if (playersError) throw playersError;

  await admin.from("conclave_match_events").insert({
    match_id: matchId,
    round: 1,
    seq: 1,
    event_type: "match_created",
    payload: {
      text: args.side2.isEcho
        ? "Echo Simulant opponent materialized."
        : "Conclave opponent found.",
    },
  });

  return matchId;
}

type MatchSide = {
  uid: string;
  cr: number;
  factionId: number;
  team: JsonMap[];
  isEcho: boolean;
};

function buildTeamSnapshot(
  uid: string,
  save: SaveRow,
  mode: "duel" | "strategic",
): JsonMap[] {
  const profile = save.profile ?? {};
  const team = [actorFromProfile(uid, profile)];
  if (mode === "duel") return team;

  const partyIds = Array.isArray(save.party?.member_ally_ids)
    ? save.party.member_ally_ids.map((id) => String(id))
    : [];
  const allies = Array.isArray(save.allies) ? save.allies : [];
  for (const allyId of partyIds.slice(0, 3)) {
    const ally = allies.find((row) => String(row.ally_id ?? "") === allyId);
    if (ally) team.push(actorFromAlly(uid, ally));
  }
  return team.slice(0, 4);
}

function actorFromProfile(uid: string, profile: JsonMap): JsonMap {
  const stats = (profile.effective_stats ?? profile.base_stats ?? {}) as JsonMap;
  const maxHp = intValue(profile.max_hp ?? stats.hp, 100);
  const maxMp = intValue(profile.max_mp ?? stats.mp, 30);
  return {
    actor_id: `player:${uid}`,
    owner_uid: uid,
    name: String(profile.username ?? "Conclave Pilot"),
    level: intValue(profile.level, 1),
    current_hp: clampInt(intValue(profile.current_hp, maxHp), 1, maxHp),
    max_hp: maxHp,
    current_mp: clampInt(intValue(profile.current_mp, maxMp), 0, maxMp),
    max_mp: maxMp,
    atk: clampInt(intValue(stats.atk, 10), 1, 9999),
    def: clampInt(intValue(stats.def, 8), 1, 9999),
    agi: clampInt(intValue(stats.agi, 8), 1, 9999),
    per: clampInt(intValue(stats.per, 8), 1, 9999),
    skill_ids: stringArray(profile.learned_skill_ids).slice(0, 24),
  };
}

function actorFromAlly(uid: string, ally: JsonMap): JsonMap {
  const stats = (ally.effective_stats ?? ally.base_stats ?? {}) as JsonMap;
  const maxHp = intValue(ally.max_hp ?? stats.hp, 80);
  const maxMp = intValue(ally.max_mp ?? stats.mp, 20);
  return {
    actor_id: `ally:${String(ally.ally_id ?? crypto.randomUUID())}`,
    owner_uid: uid,
    name: String(ally.name ?? "Ally"),
    level: intValue(ally.level, 1),
    current_hp: clampInt(intValue(ally.current_hp, maxHp), 1, maxHp),
    max_hp: maxHp,
    current_mp: clampInt(intValue(ally.current_mp, maxMp), 0, maxMp),
    max_mp: maxMp,
    atk: clampInt(intValue(stats.atk, 8), 1, 9999),
    def: clampInt(intValue(stats.def, 8), 1, 9999),
    agi: clampInt(intValue(stats.agi, 8), 1, 9999),
    per: clampInt(intValue(stats.per, 8), 1, 9999),
    skill_ids: stringArray(
      Array.isArray(ally.equipped_skill_ids) && ally.equipped_skill_ids.length > 0
        ? ally.equipped_skill_ids
        : ally.learned_skill_ids,
    ).slice(0, 12),
  };
}

function buildEchoTeam(
  echoUid: string,
  sourceTeam: JsonMap[],
  cr: number,
  mode: "duel" | "strategic",
): JsonMap[] {
  const scale = clamp(0.92 + (cr - 1000) / 10000, 0.9, 1.08);
  const count = mode === "duel" ? 1 : Math.max(1, sourceTeam.length);
  return sourceTeam.slice(0, count).map((source, index) => {
    const name = index === 0 ? "Echo Rival" : `Echo Ally ${index + 1}`;
    return {
      ...source,
      actor_id: `echo:${index}`,
      owner_uid: echoUid,
      name,
      current_hp: Math.max(1, Math.round(intValue(source.current_hp, 80) * scale)),
      max_hp: Math.max(1, Math.round(intValue(source.max_hp, 80) * scale)),
      current_mp: Math.max(0, Math.round(intValue(source.current_mp, 20) * scale)),
      max_mp: Math.max(0, Math.round(intValue(source.max_mp, 20) * scale)),
      atk: Math.max(1, Math.round(intValue(source.atk, 8) * scale)),
      def: Math.max(1, Math.round(intValue(source.def, 8) * scale)),
      agi: Math.max(1, Math.round(intValue(source.agi, 8) * scale)),
      per: Math.max(1, Math.round(intValue(source.per, 8) * scale)),
    };
  });
}

function prepareBotTeam(bot: BotRow, mode: "duel" | "strategic"): JsonMap[] {
  const team = Array.isArray(bot.team_snapshot) ? bot.team_snapshot : [];
  const count = mode === "duel" ? 1 : 4;
  return team.slice(0, count).map((actor, index) => ({
    ...actor,
    actor_id: String(actor.actor_id ?? `bot:${bot.code}:${index}`),
    name: String(actor.name ?? `${bot.display_name} ${index + 1}`),
  }));
}

async function expireOldQueues(admin: ReturnType<typeof createClient>) {
  await admin
    .from("conclave_match_queue")
    .update({ status: "expired" })
    .eq("status", "queued")
    .lte("expires_at", new Date().toISOString());
}

function normalizeMode(value: unknown): "duel" | "strategic" {
  return value === "strategic" ? "strategic" : "duel";
}

function normalizeQueueType(value: unknown): "ranked" | "casual" {
  return value === "casual" ? "casual" : "ranked";
}

function json(payload: JsonMap, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

function errorToMessage(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  if (typeof error === "string") return error;
  if (error && typeof error === "object") {
    try {
      return JSON.stringify(error);
    } catch (_) {
      return String(error);
    }
  }
  return String(error);
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

class HttpError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}
