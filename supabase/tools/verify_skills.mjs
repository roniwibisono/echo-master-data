import { PGlite } from '@electric-sql/pglite';
import { readFileSync, writeFileSync } from 'node:fs';

const [root, output] = process.argv.slice(2);
if (!root || !output) throw Error('Usage: node verify_skills.mjs MASTER_ROOT OUTPUT');
const db = new PGlite();
await db.exec('create role anon; create role authenticated;');
for (const file of ['0001_quests.sql', '0005_skills.sql']) {
  await db.exec(readFileSync(`${root}/supabase/migrations/${file}`, 'utf8'));
}
const source = JSON.parse(readFileSync(`${root}/skill_list.json`, 'utf8'));
const seed = readFileSync(`${root}/supabase/seed/skills_audited_20261008.sql`, 'utf8');
await db.exec(seed);
const actual = (await db.query('select * from skills order by sort_order')).rows;
if (actual.length !== source.length) throw Error('Skill count mismatch');
let fields = 0;
for (let i = 0; i < source.length; i++) {
  for (const [key, value] of Object.entries(source[i])) {
    const canonical = v => Array.isArray(v) ? v.map(canonical)
      : v && typeof v === 'object' ? Object.fromEntries(Object.entries(v)
        .sort(([a], [b]) => a.localeCompare(b)).map(([k, x]) => [k, canonical(x)])) : v;
    const observed = typeof value === 'number' ? Number(actual[i][key]) : actual[i][key];
    if (JSON.stringify(canonical(value)) !== JSON.stringify(canonical(observed))) {
      throw Error(`Field mismatch: ${source[i].id}/${key}`);
    }
    fields++;
  }
}
await db.exec(seed);
const repeated = (await db.query('select * from skills order by sort_order')).rows;
if (JSON.stringify(repeated) !== JSON.stringify(actual)) throw Error('Seed changed identical rows');
const firstId = source[0].id.replaceAll("'", "''");
await db.exec(`update skills set name='Changed fixture', sort_order=9999 where id='${firstId}';
 insert into skills(id,name) values('unrelated_skill_fixture','Unrelated fixture');`);
await db.exec(seed);
const first = (await db.query(`select name,sort_order from skills where id='${firstId}'`)).rows[0];
if (first.name !== source[0].name || first.sort_order !== 9999) throw Error('Update/order preservation failed');
if ((await db.query("select count(*) n from skills where id='unrelated_skill_fixture'")).rows[0].n !== 1) {
  throw Error('Unrelated skill removed');
}
const report = { engine: 'PGlite PostgreSQL', rows_verified: source.length,
  authored_fields_verified: fields, unchanged_rows_skipped: true,
  existing_sort_order_preserved: true, changed_fields_updated: true,
  unrelated_rows_preserved: true };
writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report));
await db.close();
