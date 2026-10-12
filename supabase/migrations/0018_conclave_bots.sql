-- Conclave bot pool for low-population matchmaking and QA.
-- Bots are server-owned opponents. They never receive rating rows.

create extension if not exists pgcrypto;

create table if not exists public.conclave_bots (
  bot_uid uuid primary key default gen_random_uuid(),
  code text not null unique,
  display_name text not null,
  rank_label text not null,
  difficulty text not null
    check (difficulty in ('easy', 'normal', 'hard', 'expert', 'nightmare')),
  mode text not null default 'both'
    check (mode in ('duel', 'strategic', 'both')),
  cr int not null default 1000,
  faction_id int not null default 1,
  ai_profile jsonb not null default '{}'::jsonb,
  team_snapshot jsonb not null default '[]'::jsonb,
  active boolean not null default true,
  last_used_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists conclave_bots_match_idx
  on public.conclave_bots (active, mode, cr);

drop trigger if exists trg_conclave_bots_updated_at on public.conclave_bots;
create trigger trg_conclave_bots_updated_at
before update on public.conclave_bots
for each row execute function public.set_conclave_updated_at();

alter table public.conclave_bots enable row level security;

drop policy if exists "players can read active conclave bots" on public.conclave_bots;
create policy "players can read active conclave bots"
on public.conclave_bots
for select
using (active);

with bot_defs as (
  select
    n,
    format('conclave_bot_%s', lpad(n::text, 2, '0')) as code,
    case
      when n <= 10 then 'Recruit'
      when n <= 22 then 'Vanguard'
      when n <= 34 then 'Elite'
      when n <= 44 then 'Champion'
      else 'Ascendant'
    end as rank_label,
    case (n - 1) % 5
      when 0 then 'easy'
      when 1 then 'normal'
      when 2 then 'hard'
      when 3 then 'expert'
      else 'nightmare'
    end as difficulty,
    case
      when n <= 10 then 825 + (n * 28)
      when n <= 22 then 1120 + ((n - 10) * 34)
      when n <= 34 then 1460 + ((n - 22) * 32)
      when n <= 44 then 1780 + ((n - 34) * 30)
      else 2070 + ((n - 44) * 35)
    end as cr,
    ((n - 1) % 7) + 1 as faction_id,
    case (n - 1) % 5
      when 0 then 0.88
      when 1 then 1.00
      when 2 then 1.12
      when 3 then 1.25
      else 1.40
    end as mult,
    (array[
      'Aster', 'Nyx', 'Orion', 'Vega', 'Lyra', 'Sable', 'Kairo', 'Iris',
      'Drax', 'Vesper', 'Axiom', 'Nova', 'Cinder', 'Riven', 'Solace',
      'Cipher', 'Mira', 'Kestrel', 'Obsidian', 'Helix', 'Rune', 'Nadir',
      'Echo', 'Vanta', 'Cael', 'Zenith', 'Onyx', 'Aural', 'Vox', 'Sevra',
      'Pulse', 'Ardent', 'Vale', 'Korin', 'Dusk', 'Lumen', 'Quill',
      'Raze', 'Morrow', 'Krynn', 'Talon', 'Nerva', 'Glass', 'Vire',
      'Ichor', 'Halcyon', 'Vector', 'Umbral', 'Solis', 'Eon'
    ])[n] as callsign
  from generate_series(1, 50) as n
),
bot_rows as (
  select
    code,
    format('%s %s-%s', callsign, upper(left(rank_label, 1)), lpad(n::text, 2, '0')) as display_name,
    rank_label,
    difficulty,
    'both'::text as mode,
    cr,
    faction_id,
    jsonb_build_object(
      'aggression', round((0.45 + (n % 7) * 0.07)::numeric, 2),
      'risk_tolerance', difficulty,
      'rank_label', rank_label
    ) as ai_profile,
    jsonb_build_array(
      jsonb_build_object(
        'actor_id', format('bot:%s:leader', code),
        'name', format('%s %s', callsign, 'Prime'),
        'level', greatest(1, round(cr / 85.0)),
        'current_hp', round((130 + cr * 0.13) * mult),
        'max_hp', round((130 + cr * 0.13) * mult),
        'current_mp', round((45 + cr * 0.045) * mult),
        'max_mp', round((45 + cr * 0.045) * mult),
        'atk', round((12 + cr / 88.0) * mult),
        'def', round((10 + cr / 100.0) * mult),
        'agi', round((10 + cr / 105.0) * mult),
        'per', round((10 + cr / 96.0) * mult),
        'skill_ids', jsonb_build_array('basic_attack')
      ),
      jsonb_build_object(
        'actor_id', format('bot:%s:vanguard', code),
        'name', format('%s Bulwark', callsign),
        'level', greatest(1, round(cr / 90.0)),
        'current_hp', round((150 + cr * 0.15) * mult),
        'max_hp', round((150 + cr * 0.15) * mult),
        'current_mp', round((34 + cr * 0.035) * mult),
        'max_mp', round((34 + cr * 0.035) * mult),
        'atk', round((9 + cr / 110.0) * mult),
        'def', round((14 + cr / 82.0) * mult),
        'agi', round((8 + cr / 125.0) * mult),
        'per', round((9 + cr / 110.0) * mult),
        'skill_ids', jsonb_build_array('basic_attack')
      ),
      jsonb_build_object(
        'actor_id', format('bot:%s:striker', code),
        'name', format('%s Striker', callsign),
        'level', greatest(1, round(cr / 90.0)),
        'current_hp', round((105 + cr * 0.105) * mult),
        'max_hp', round((105 + cr * 0.105) * mult),
        'current_mp', round((38 + cr * 0.04) * mult),
        'max_mp', round((38 + cr * 0.04) * mult),
        'atk', round((15 + cr / 78.0) * mult),
        'def', round((8 + cr / 118.0) * mult),
        'agi', round((14 + cr / 82.0) * mult),
        'per', round((11 + cr / 92.0) * mult),
        'skill_ids', jsonb_build_array('basic_attack')
      ),
      jsonb_build_object(
        'actor_id', format('bot:%s:support', code),
        'name', format('%s Vector', callsign),
        'level', greatest(1, round(cr / 92.0)),
        'current_hp', round((112 + cr * 0.11) * mult),
        'max_hp', round((112 + cr * 0.11) * mult),
        'current_mp', round((58 + cr * 0.055) * mult),
        'max_mp', round((58 + cr * 0.055) * mult),
        'atk', round((10 + cr / 100.0) * mult),
        'def', round((10 + cr / 102.0) * mult),
        'agi', round((11 + cr / 96.0) * mult),
        'per', round((14 + cr / 82.0) * mult),
        'skill_ids', jsonb_build_array('basic_attack')
      )
    ) as team_snapshot
  from bot_defs
)
insert into public.conclave_bots (
  code,
  display_name,
  rank_label,
  difficulty,
  mode,
  cr,
  faction_id,
  ai_profile,
  team_snapshot,
  active
)
select
  code,
  display_name,
  rank_label,
  difficulty,
  mode,
  cr,
  faction_id,
  ai_profile,
  team_snapshot,
  true
from bot_rows
on conflict (code) do update set
  display_name = excluded.display_name,
  rank_label = excluded.rank_label,
  difficulty = excluded.difficulty,
  mode = excluded.mode,
  cr = excluded.cr,
  faction_id = excluded.faction_id,
  ai_profile = excluded.ai_profile,
  team_snapshot = excluded.team_snapshot,
  active = true,
  updated_at = now();
