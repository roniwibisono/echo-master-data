-- Optional context for Memory validation on the original raid host.
-- Existing owner/host RLS is unchanged. Protocol 2 adds Memory context.
begin;
alter table public.raid_room_members
  add column if not exists memory_context jsonb not null default '{}'::jsonb;

alter table public.raid_room_members
  add constraint raid_memory_context_shape check (
    coalesce(
      jsonb_typeof(memory_context) = 'object'
      and octet_length(memory_context::text) <= 16384
      and (
        memory_context = '{}'::jsonb
        or case when memory_context->>'protocol' = '1'
          and jsonb_typeof(memory_context->'weapons') = 'array'
          and jsonb_typeof(memory_context->'memories') = 'array'
        then not jsonb_path_exists(memory_context, '$.weapons[*] ? (@.type() != "string")')
          and not jsonb_path_exists(memory_context, '$.memories[*] ? (@.type() != "string")')
          and to_jsonb(skill_ids) @> (memory_context->'memories')
        else false end
      ), false
    )
  );

alter table public.raid_room_members drop constraint if exists raid_member_act_protocol;
alter table public.raid_room_members
  add constraint raid_member_act_protocol check (act_protocol in (0, 1, 2)),
  add constraint raid_memory_context_protocol check (memory_context = '{}'::jsonb or act_protocol = 2);
commit;
