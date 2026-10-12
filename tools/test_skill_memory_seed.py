"""Rehearse the exact migration and seed on a disposable local PostgreSQL."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_skill_memory_seed as builder

PG = Path('/opt/homebrew/opt/postgresql@17/bin')


class MemorySeedTest(unittest.TestCase):
    def test_migration_seed_and_permissions(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith('PG')}
        with tempfile.TemporaryDirectory(prefix='memory-seed-') as temp:
            root = Path(temp)
            sock = root / 'sock'
            sock.mkdir(mode=0o700)

            def run(name, *args, data=None):
                result = subprocess.run([str(PG / name), *map(str, args)], input=data,
                                        text=True, capture_output=True, env=env, timeout=60)
                if result.returncode:
                    raise RuntimeError(result.stderr)
                return result.stdout.strip()

            run('initdb', '-D', root / 'data', '-U', 'postgres', '--auth=trust', '--no-locale')
            started = False
            try:
                run('pg_ctl', '-D', root / 'data', '-l', root / 'log', '-w', '-o',
                    f"-c listen_addresses='' -c unix_socket_directories='{sock}' -p 55473", 'start')
                started = True

                def sql(query):
                    return run('psql', '-h', sock, '-p', '55473', '-U', 'postgres',
                               '-d', 'postgres', '-X', '-A', '-t', '-v', 'ON_ERROR_STOP=1', data=query)

                sql('create role anon; create role authenticated; create role service_role; '
                    'create function public.touch_updated_at() returns trigger language plpgsql as $$ '
                    'begin new.updated_at=now(); return new; end $$; '
                    'create function public.bump_content_version() returns trigger language plpgsql as $$ '
                    'begin return null; end $$;')
                for name in ('0004_items.sql', '0005_skills.sql', '0008_npcs.sql', '0009_dialogs.sql'):
                    sql((builder.ROOT / 'supabase/migrations' / name).read_text())
                sql("insert into public.items(id,name,type) values ('legacy','Legacy','WEAPON_SWORD');")
                sql((builder.ROOT / 'supabase/migrations/20261012094528_skill_memory_catalog.sql').read_text())
                sql(builder.build())
                self.assertEqual(sql("select count(*) from public.items where type='SKILL_MEMORY';"), '20')
                self.assertEqual(sql("select count(*) from public.skills where skill_memory_tier between 1 and 3;"), '20')
                self.assertEqual(sql("select jsonb_array_length(payload->'training_quests') from public.skill_memory_catalog;"), '180')
                before = sql("select md5(string_agg(to_jsonb(t)::text, '' order by id)) from public.items t;")
                sql(builder.build())
                self.assertEqual(before, sql("select md5(string_agg(to_jsonb(t)::text, '' order by id)) from public.items t;"))
                self.assertEqual(sql("select name from public.items where id='legacy';"), 'Legacy')
                self.assertEqual(sql("select has_table_privilege('anon','public.skill_memory_catalog','select') and not has_table_privilege('anon','public.skill_memory_catalog','insert') and not has_table_privilege('authenticated','public.skill_memory_catalog','update');"), 't')
                self.assertEqual(sql("select relrowsecurity from pg_class where oid='public.skill_memory_catalog'::regclass;"), 't')
                self.assertEqual(sql("select runtime_ready from public.skill_memory_catalog;"), 'f')
            finally:
                if started:
                    run('pg_ctl', '-D', root / 'data', '-w', 'stop')


if __name__ == '__main__':
    unittest.main()
