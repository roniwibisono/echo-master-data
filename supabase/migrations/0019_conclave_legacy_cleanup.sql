-- Cleanup for older Conclave schemas that had NOT NULL winner_team.
-- Realtime Conclave uses winner_uid and cannot know a winner at match creation.

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
