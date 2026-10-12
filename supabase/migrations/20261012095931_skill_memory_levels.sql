begin;
alter table public.raid_room_members drop constraint raid_memory_context_shape;
alter table public.raid_room_members add constraint raid_memory_context_shape check (
  coalesce(jsonb_typeof(memory_context) = 'object'
  and octet_length(memory_context::text) <= 16384
  and (memory_context = '{}'::jsonb or case
    when memory_context->>'protocol' in ('1','2')
      and jsonb_typeof(memory_context->'weapons') = 'array'
      and jsonb_typeof(memory_context->'memories') = 'array'
    then not jsonb_path_exists(memory_context, '$.weapons[*] ? (@.type() != "string")')
      and not jsonb_path_exists(memory_context, '$.memories[*] ? (@.type() != "string")')
      and to_jsonb(skill_ids) @> (memory_context->'memories')
      and case when memory_context->>'protocol' = '2'
        and jsonb_typeof(memory_context->'levels') = 'object'
        then not jsonb_path_exists(memory_context->'levels', '$.* ? (@.type() != "number" || !(@ == 1 || @ == 2 || @ == 3 || @ == 4 || @ == 5 || @ == 6 || @ == 7 || @ == 8 || @ == 9 || @ == 10))')
          and (memory_context->'memories') @> jsonb_path_query_array(memory_context->'levels', '$.keyvalue().key')
          and jsonb_path_query_array(memory_context->'levels', '$.keyvalue().key') @> (memory_context->'memories')
        else memory_context->>'protocol' = '1' end
    else false end), false)
);
commit;
