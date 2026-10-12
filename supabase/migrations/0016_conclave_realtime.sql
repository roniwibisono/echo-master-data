-- Realtime Conclave PvP foundation.
-- Client submits action intents only. Authoritative combat resolution, RNG,
-- item validation, cooldown validation, and rating updates must be performed
-- by a trusted server process / Edge Function with service-role access.

create extension if not exists pgcrypto;

create table if not exists public.conclave_matches (
  id uuid primary key default gen_random_uuid(),
  season_id int not null default 1,
  mode text not null check (mode in ('duel', 'strategic')),
  queue_type text not null check (queue_type in ('ranked', 'casual')),
  status text not null default 'forming'
    check (status in ('forming', 'active', 'resolving', 'finished', 'cancelled')),
  round int not null default 1 check (round > 0),
  turn_deadline timestamptz,
  rng_seed text not null default encode(gen_random_bytes(32), 'hex'),
  participant_a uuid,
  participant_b uuid,
  winner_uid uuid,
  state jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  finished_at timestamptz
);

-- Compatibility for projects that already had an older/incomplete
-- conclave_matches table. `create table if not exists` does not add missing
-- columns, so make the parent table safe before child FKs reference `id`.
alter table public.conclave_matches add column if not exists id uuid;
update public.conclave_matches set id = gen_random_uuid() where id is null;
alter table public.conclave_matches alter column id set default gen_random_uuid();
alter table public.conclave_matches alter column id set not null;
alter table public.conclave_matches add column if not exists season_id int not null default 1;
alter table public.conclave_matches add column if not exists mode text not null default 'duel';
alter table public.conclave_matches add column if not exists queue_type text not null default 'casual';
alter table public.conclave_matches add column if not exists status text not null default 'forming';
alter table public.conclave_matches add column if not exists round int not null default 1;
alter table public.conclave_matches add column if not exists turn_deadline timestamptz;
alter table public.conclave_matches add column if not exists rng_seed text not null default encode(gen_random_bytes(32), 'hex');
alter table public.conclave_matches add column if not exists participant_a uuid;
alter table public.conclave_matches add column if not exists participant_b uuid;
alter table public.conclave_matches add column if not exists winner_uid uuid;
alter table public.conclave_matches add column if not exists state jsonb not null default '{}'::jsonb;
alter table public.conclave_matches add column if not exists created_at timestamptz not null default now();
alter table public.conclave_matches add column if not exists updated_at timestamptz not null default now();
alter table public.conclave_matches add column if not exists finished_at timestamptz;

do $$
begin
  if exists (
    select 1
    from information_schema.columns
    where table_schema = 'public'
      and table_name = 'conclave_matches'
      and column_name = 'winner_team'
  ) then
    alter table public.conclave_matches
      alter column winner_team drop not null;
  end if;
end;
$$;

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conrelid = 'public.conclave_matches'::regclass
      and conname = 'conclave_matches_id_key'
  ) then
    alter table public.conclave_matches
      add constraint conclave_matches_id_key unique (id);
  end if;
end;
$$;

create table if not exists public.conclave_match_players (
  match_id uuid not null references public.conclave_matches(id) on delete cascade,
  uid uuid not null,
  side smallint not null check (side in (1, 2)),
  display_name text not null default '',
  faction_id int not null default 0,
  cr_snapshot int not null default 1000,
  loadout_hash text not null default '',
  team_snapshot jsonb not null default '[]'::jsonb,
  locked_round int not null default 0,
  connected_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  primary key (match_id, uid)
);

alter table public.conclave_match_players add column if not exists match_id uuid;
alter table public.conclave_match_players add column if not exists uid uuid;
alter table public.conclave_match_players add column if not exists side smallint not null default 1;
alter table public.conclave_match_players add column if not exists display_name text not null default '';
alter table public.conclave_match_players add column if not exists faction_id int not null default 0;
alter table public.conclave_match_players add column if not exists cr_snapshot int not null default 1000;
alter table public.conclave_match_players add column if not exists loadout_hash text not null default '';
alter table public.conclave_match_players add column if not exists team_snapshot jsonb not null default '[]'::jsonb;
alter table public.conclave_match_players add column if not exists locked_round int not null default 0;
alter table public.conclave_match_players add column if not exists connected_at timestamptz not null default now();
alter table public.conclave_match_players add column if not exists last_seen_at timestamptz not null default now();

create table if not exists public.conclave_turn_actions (
  match_id uuid not null references public.conclave_matches(id) on delete cascade,
  round int not null check (round > 0),
  uid uuid not null,
  actor_id text not null,
  action jsonb not null,
  submitted_at timestamptz not null default now(),
  locked boolean not null default false,
  primary key (match_id, round, uid, actor_id)
);

alter table public.conclave_turn_actions add column if not exists match_id uuid;
alter table public.conclave_turn_actions add column if not exists round int not null default 1;
alter table public.conclave_turn_actions add column if not exists uid uuid;
alter table public.conclave_turn_actions add column if not exists actor_id text not null default '';
alter table public.conclave_turn_actions add column if not exists action jsonb not null default '{}'::jsonb;
alter table public.conclave_turn_actions add column if not exists submitted_at timestamptz not null default now();
alter table public.conclave_turn_actions add column if not exists locked boolean not null default false;

create table if not exists public.conclave_match_events (
  id bigserial primary key,
  match_id uuid not null references public.conclave_matches(id) on delete cascade,
  round int not null check (round > 0),
  seq int not null,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (match_id, round, seq)
);

alter table public.conclave_match_events add column if not exists id bigserial;
alter table public.conclave_match_events add column if not exists match_id uuid;
alter table public.conclave_match_events add column if not exists round int not null default 1;
alter table public.conclave_match_events add column if not exists seq int not null default 1;
alter table public.conclave_match_events add column if not exists event_type text not null default 'system';
alter table public.conclave_match_events add column if not exists payload jsonb not null default '{}'::jsonb;
alter table public.conclave_match_events add column if not exists created_at timestamptz not null default now();

create index if not exists conclave_matches_status_deadline_idx
  on public.conclave_matches (status, turn_deadline);

create index if not exists conclave_match_players_uid_idx
  on public.conclave_match_players (uid, match_id);

create index if not exists conclave_turn_actions_resolve_idx
  on public.conclave_turn_actions (match_id, round, locked, submitted_at);

create index if not exists conclave_events_match_seq_idx
  on public.conclave_match_events (match_id, round, seq);

create or replace function public.set_conclave_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_conclave_matches_updated_at on public.conclave_matches;
create trigger trg_conclave_matches_updated_at
before update on public.conclave_matches
for each row execute function public.set_conclave_updated_at();

alter table public.conclave_matches enable row level security;
alter table public.conclave_match_players enable row level security;
alter table public.conclave_turn_actions enable row level security;
alter table public.conclave_match_events enable row level security;

create or replace function public.is_conclave_participant(p_match_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.conclave_match_players p
    where p.match_id = p_match_id
      and p.uid = auth.uid()
  );
$$;

drop policy if exists "participants can read conclave matches" on public.conclave_matches;
create policy "participants can read conclave matches"
on public.conclave_matches
for select
using (public.is_conclave_participant(id));

drop policy if exists "participants can read conclave players" on public.conclave_match_players;
create policy "participants can read conclave players"
on public.conclave_match_players
for select
using (public.is_conclave_participant(match_id));

drop policy if exists "players can read own pending actions" on public.conclave_turn_actions;
create policy "players can read own pending actions"
on public.conclave_turn_actions
for select
using (uid = auth.uid());

drop policy if exists "participants can read conclave events" on public.conclave_match_events;
create policy "participants can read conclave events"
on public.conclave_match_events
for select
using (public.is_conclave_participant(match_id));

create or replace function public.conclave_submit_turn_actions(
  p_match_id uuid,
  p_round int,
  p_actions jsonb
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_match public.conclave_matches%rowtype;
  v_action jsonb;
  v_actor_id text;
  v_action_type text;
begin
  if v_uid is null then
    raise exception 'not_authenticated';
  end if;

  if p_actions is null or jsonb_typeof(p_actions) <> 'array' then
    raise exception 'invalid_actions_payload';
  end if;

  if jsonb_array_length(p_actions) > 4 then
    raise exception 'too_many_actions';
  end if;

  if octet_length(p_actions::text) > 8192 then
    raise exception 'actions_payload_too_large';
  end if;

  select *
  into v_match
  from public.conclave_matches
  where id = p_match_id
  for update;

  if not found then
    raise exception 'match_not_found';
  end if;

  if v_match.status <> 'active' or v_match.round <> p_round then
    raise exception 'match_not_accepting_actions';
  end if;

  if v_match.turn_deadline is not null
      and now() > v_match.turn_deadline + interval '3 seconds' then
    raise exception 'turn_deadline_expired';
  end if;

  if not exists (
    select 1
    from public.conclave_match_players p
    where p.match_id = p_match_id
      and p.uid = v_uid
  ) then
    raise exception 'not_match_participant';
  end if;

  for v_action in select * from jsonb_array_elements(p_actions)
  loop
    v_actor_id := nullif(v_action->>'actor_id', '');
    v_action_type := nullif(v_action->>'type', '');

    if v_actor_id is null then
      raise exception 'missing_actor_id';
    end if;

    if v_action_type not in ('attack', 'skill', 'item', 'defend') then
      raise exception 'invalid_action_type';
    end if;

    if v_action_type = 'skill' and nullif(v_action->>'skill_id', '') is null then
      raise exception 'missing_skill_id';
    end if;

    if v_action_type = 'item' and nullif(v_action->>'item_instance_id', '') is null then
      raise exception 'missing_item_instance_id';
    end if;

    -- Team ownership, skill ownership, item ownership, cooldowns, and MP must
    -- be checked by the resolver against team_snapshot and canonical data.
    insert into public.conclave_turn_actions (
      match_id,
      round,
      uid,
      actor_id,
      action,
      submitted_at,
      locked
    )
    values (
      p_match_id,
      p_round,
      v_uid,
      v_actor_id,
      v_action,
      now(),
      false
    )
    on conflict (match_id, round, uid, actor_id) do update
      set action = excluded.action,
          submitted_at = now()
      where public.conclave_turn_actions.locked = false;
  end loop;
end;
$$;

create or replace function public.conclave_lock_turn(
  p_match_id uuid,
  p_round int
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_match public.conclave_matches%rowtype;
begin
  if v_uid is null then
    raise exception 'not_authenticated';
  end if;

  select *
  into v_match
  from public.conclave_matches
  where id = p_match_id
  for update;

  if not found then
    raise exception 'match_not_found';
  end if;

  if v_match.status <> 'active' or v_match.round <> p_round then
    raise exception 'match_not_accepting_locks';
  end if;

  if not exists (
    select 1
    from public.conclave_match_players p
    where p.match_id = p_match_id
      and p.uid = v_uid
  ) then
    raise exception 'not_match_participant';
  end if;

  update public.conclave_turn_actions
  set locked = true
  where match_id = p_match_id
    and round = p_round
    and uid = v_uid;

  update public.conclave_match_players
  set locked_round = p_round,
      last_seen_at = now()
  where match_id = p_match_id
    and uid = v_uid;

  update public.conclave_matches
  set state = jsonb_set(
        state,
        '{turn_locks}',
        coalesce(state->'turn_locks', '{}'::jsonb) ||
          jsonb_build_object(v_uid::text, true),
        true
      ),
      status = case
        when (
          select count(*)
          from public.conclave_match_players p
          where p.match_id = p_match_id
            and p.locked_round >= p_round
        ) >= 2
        then 'resolving'
        else status
      end
  where id = p_match_id;
end;
$$;

create or replace function public.conclave_touch_match_presence(
  p_match_id uuid,
  p_uid uuid default auth.uid()
)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if auth.uid() is null or p_uid <> auth.uid() then
    raise exception 'not_authenticated';
  end if;

  update public.conclave_match_players
  set last_seen_at = now()
  where match_id = p_match_id
    and uid = p_uid;
end;
$$;

grant execute on function public.conclave_submit_turn_actions(uuid, int, jsonb)
  to authenticated;
grant execute on function public.conclave_lock_turn(uuid, int)
  to authenticated;
grant execute on function public.conclave_touch_match_presence(uuid, uuid)
  to authenticated;
grant execute on function public.is_conclave_participant(uuid)
  to authenticated;
