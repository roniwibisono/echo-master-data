-- Realtime Conclave matchmaking queue.
-- The Edge Function `conclave_matchmake` writes here with service-role access.

create extension if not exists pgcrypto;

alter table public.conclave_match_players
  add column if not exists is_echo boolean not null default false;

create table if not exists public.conclave_match_queue (
  id uuid primary key default gen_random_uuid(),
  uid uuid not null,
  season_id int not null default 1,
  mode text not null check (mode in ('duel', 'strategic')),
  queue_type text not null check (queue_type in ('ranked', 'casual')),
  status text not null default 'queued'
    check (status in ('queued', 'matched', 'cancelled', 'expired')),
  cr int not null default 1000,
  faction_id int not null default 0,
  team_snapshot jsonb not null default '[]'::jsonb,
  match_id uuid references public.conclave_matches(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  expires_at timestamptz not null default (now() + interval '2 minutes')
);

create index if not exists conclave_match_queue_find_idx
  on public.conclave_match_queue
  (status, mode, queue_type, season_id, cr, created_at);

create unique index if not exists conclave_match_queue_one_active_uid_idx
  on public.conclave_match_queue (uid, mode, queue_type, season_id)
  where status = 'queued';

drop trigger if exists trg_conclave_match_queue_updated_at on public.conclave_match_queue;
create trigger trg_conclave_match_queue_updated_at
before update on public.conclave_match_queue
for each row execute function public.set_conclave_updated_at();

alter table public.conclave_match_queue enable row level security;

drop policy if exists "players can read own conclave queue" on public.conclave_match_queue;
create policy "players can read own conclave queue"
on public.conclave_match_queue
for select
using (uid = auth.uid());

drop policy if exists "players can cancel own conclave queue" on public.conclave_match_queue;
create policy "players can cancel own conclave queue"
on public.conclave_match_queue
for update
using (uid = auth.uid())
with check (uid = auth.uid());
