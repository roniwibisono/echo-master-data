-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0005 — SKILLS
--  skill_list.json (688 skills, 0 duplicate ids) → public.skills. Scalars as
--  columns; the effect arrays (stat_modifiers / periodic_effects /
--  control_effects / special_effects) and usage_requirements as JSONB, matching
--  the Skill model. `effect` is the free-form legacy blob (kept verbatim).
--  Optional fields (special_effects, usage_requirements, target_attack,
--  target_effect, arc_angle_degrees) are NULL when absent so export can omit
--  them (round-trip). Run after 0001.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.skills (
  id                  text primary key,
  name                text not null,
  type                text,
  source_type         text,
  mp_cost             int not null default 0,
  damage_formula      text,
  effect              text,
  skill_description   text,
  skill_shape         text,
  "range"             numeric,
  aoe_radius          numeric,
  projectile_speed    numeric,
  cooldown_seconds    numeric,
  arc_angle_degrees   numeric,       -- optional (1 skill)
  target_attack       text,          -- optional
  target_effect       text,          -- optional
  stat_modifiers      jsonb not null default '[]'::jsonb,
  periodic_effects    jsonb not null default '[]'::jsonb,
  control_effects     jsonb not null default '[]'::jsonb,
  special_effects     jsonb,         -- optional (NULL when absent)
  usage_requirements  jsonb,         -- optional (NULL when absent)
  sort_order          int not null default 0,
  updated_at          timestamptz not null default now()
);

create index if not exists skills_type_idx   on public.skills (type);
create index if not exists skills_source_idx on public.skills (source_type);

drop trigger if exists skills_touch on public.skills;
create trigger skills_touch before update on public.skills
  for each row execute function public.touch_updated_at();

drop trigger if exists skills_bump_version on public.skills;
create trigger skills_bump_version after insert or update or delete on public.skills
  for each statement execute function public.bump_content_version('skills');

alter table public.skills enable row level security;
drop policy if exists skills_public_read on public.skills;
create policy skills_public_read on public.skills for select using (true);
