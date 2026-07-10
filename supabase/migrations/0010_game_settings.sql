-- ═══════════════════════════════════════════════════════════════════════
--  Master-data migration 0010 — GAME SETTINGS (centralized live-ops tuning)
--  A single key-value table of server-wide tunables (exp/drop multipliers,
--  progression curve, economy, combat, raid/siege/conclave, faction, system,
--  feature flags, maintenance, events). The Flutter client reads these via a
--  GameSettingsService (CDN game_settings.json + Supabase Realtime) so any
--  value can change for the whole server in real time without a redeploy.
--
--  `value` holds the CURRENT live value; `default_value` the production intent.
--  (Several multipliers currently ship at dev/test-inflated values — see seed.)
--  Run after 0001 (reuses touch_updated_at() + bump_content_version()).
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.game_settings (
  key                     text primary key,          -- dotted namespace e.g. 'exp.global_multiplier'
  category                text not null,             -- multiplier|progression|starting|energy|idle|economy|combat|raid|siege|conclave|faction|social|system|feature|liveops|anticheat|season
  value                   jsonb not null,            -- current live value (scalar: number/bool/string)
  default_value           jsonb not null,            -- production-intended default
  value_type              text not null,             -- double|int|bool|string
  min_value               numeric,                   -- clamp lower bound (numeric only)
  max_value               numeric,                   -- clamp upper bound (numeric only)
  hot_reloadable          boolean not null default true,   -- safe to change live without care?
  requires_client_version text,                      -- min client version that understands this key
  enabled                 boolean not null default true,
  description             text,
  sort_order              int not null default 0,
  updated_by              text,
  updated_at              timestamptz not null default now()
);
create index if not exists game_settings_category_idx on public.game_settings (category);

-- ── Audit log (admin-only; every value change is recorded) ─────────────────
create table if not exists public.game_settings_audit (
  id          bigserial primary key,
  key         text not null,
  old_value   jsonb,
  new_value   jsonb,
  changed_by  text,
  changed_at  timestamptz not null default now()
);
create index if not exists gsa_key_idx on public.game_settings_audit (key, changed_at desc);

create or replace function public.log_game_setting_change()
  returns trigger language plpgsql as $$
begin
  if (tg_op = 'UPDATE' and new.value is distinct from old.value) then
    insert into public.game_settings_audit(key, old_value, new_value, changed_by)
    values (new.key, old.value, new.value, new.updated_by);
  end if;
  return null;
end $$;

drop trigger if exists game_settings_touch on public.game_settings;
create trigger game_settings_touch before update on public.game_settings
  for each row execute function public.touch_updated_at();

drop trigger if exists game_settings_audit_trg on public.game_settings;
create trigger game_settings_audit_trg after update on public.game_settings
  for each row execute function public.log_game_setting_change();

drop trigger if exists game_settings_bump_version on public.game_settings;
create trigger game_settings_bump_version after insert or update or delete on public.game_settings
  for each statement execute function public.bump_content_version('settings');

-- Public read so the client can fetch tunables + subscribe to Realtime changes.
alter table public.game_settings enable row level security;
drop policy if exists game_settings_public_read on public.game_settings;
create policy game_settings_public_read on public.game_settings for select using (true);

-- Audit is NOT public-read (admin/service-role only): RLS on, no public policy.
alter table public.game_settings_audit enable row level security;
