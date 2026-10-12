import { PGlite } from '@electric-sql/pglite';
import { readFileSync, writeFileSync } from 'node:fs';
const root=process.argv[2];
const output=process.argv[3];
if (!root || !output) throw Error('Usage: node verify_class_progression.mjs MASTER_ROOT REPORT_JSON');
const db=new PGlite();
await db.exec('create role anon; create role authenticated;');
for (const name of ['0001_quests.sql','0004_items.sql','0005_skills.sql','0006_monsters.sql','0008_npcs.sql','0009_dialogs.sql','20261008035249_class_trial_progression.sql']) {
 await db.exec(readFileSync(`${root}/supabase/migrations/${name}`,'utf8'));
}
const seed=readFileSync(`${root}/supabase/seed/class_progression_20261008.sql`,'utf8');
await db.exec(seed);
const once=await db.query(`select (select count(*) from classes) classes,(select count(*) from items) items,(select count(*) from npcs) npcs,(select count(*) from quests where requirements ? 'class_promotion') trials,(select count(*) from dialogs) dialogs,(select count(*) from skills) skills`);
await db.exec(seed);
const twice=await db.query(`select (select count(*) from classes) classes,(select count(*) from items) items,(select count(*) from npcs) npcs,(select count(*) from quests where requirements ? 'class_promotion') trials,(select count(*) from dialogs) dialogs,(select count(*) from skills) skills`);
if(JSON.stringify(once.rows)!==JSON.stringify(twice.rows))throw Error('Seed is not idempotent');
const broken=await db.query(`select q.id from quests q cross join lateral jsonb_array_elements(q.objectives) o left join monsters m on m.monster_id=case when q.requirements ? 'class_promotion' then (o->>'target')::integer else null end where q.requirements ? 'class_promotion' and m.monster_id is null
union all select c.id from classes c left join classes p on p.id=c.parent_id where c.parent_id is not null and p.id is null
union all select c.id from classes c cross join lateral jsonb_array_elements_text(c.learnable_skill_ids) s(id) left join skills sk on sk.id=s.id where sk.id is null
union all select q.id from quests q left join items i on i.id=q.requirements->'class_promotion'->>'proof_item_id' left join npcs n on n.npc_id=q.requirements->'class_promotion'->>'trainer_npc_id' where q.requirements ? 'class_promotion' and (i.id is null or n.npc_id is null or n.faction<>q.faction)`);
if(broken.rows.length)throw Error(JSON.stringify(broken.rows));
await db.exec('set role anon');
const publicClasses=await db.query('select count(*) n from classes');
let writeRejected=false;try { await db.exec(`insert into classes(id,name,tier) values('untrusted','Untrusted','Base')`); }catch{writeRejected=true;}
if(!writeRejected)throw Error('Anonymous writes unexpectedly allowed');
await db.exec('reset role');
const exported=await db.query('select * from classes order by sort_order');
const authored=JSON.parse(readFileSync(root+'/class_list.json','utf8'));
for (let i=0;i<authored.length;i++) {
 const row=exported.rows[i], source=authored[i];
 for (const field of ['id','name','tier','parent_id','description','base_stats_bonus','learnable_skill_ids']) {
  const normalized=(v)=>v && typeof v==='object' && !Array.isArray(v) ? Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))) : v;
  if (JSON.stringify(normalized(row[field]))!==JSON.stringify(normalized(source[field]))) throw Error('Class export mismatch: '+source.id+'/'+field);
 }
 if (Number(row.is_active)!==Number(source.isActive)) throw Error('Activation flag mismatch');
}
const preservedId=(await db.query('select monster_id from monsters limit 1')).rows[0].monster_id;
await db.exec(`update monsters set base_stats='{"hp":123456}'::jsonb where monster_id=${preservedId}; insert into items(id,name,type,rarity) values('unrelated_fixture','Preserved item','MATERIAL','COMMON');`);
await db.exec(seed);
const kept=await db.query(`select (select count(*) from items where id='unrelated_fixture') unrelated_items,(select base_stats->>'hp' from monsters where monster_id=${preservedId}) preserved_monster_hp`);
if (kept.rows[0].unrelated_items!==1 || kept.rows[0].preserved_monster_hp!=='123456') throw Error('Seed changed unrelated content or existing enemy balance');
const result={class_export_roundtrip:true,existing_content_preserved:kept.rows[0],engine:'PGlite PostgreSQL',first_seed:once.rows[0],second_seed:twice.rows[0],missing_references:broken.rows,anonymous_reads:publicClasses.rows[0],anonymous_writes_rejected:writeRejected};
writeFileSync(output,JSON.stringify(result,null,2));
console.log(JSON.stringify(result));await db.close();
