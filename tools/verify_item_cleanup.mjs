// Run: node tools/verify_item_cleanup.mjs /path/to/@electric-sql/pglite/dist/index.js
// Uses an isolated in-memory Postgres, never the live Supabase database.
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const { PGlite } = await import(pathToFileURL(process.argv[2]).href);
const db = new PGlite();
const root = new URL('../', import.meta.url);
const read = async path => readFile(new URL(path, root), 'utf8');
const json = async path => JSON.parse(await read(path));
const report = await json('item_audit_20261008.json');
const aliases = { ...report.retired_existing_ids, ...report.undefined_ids_replaced };
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const normalize = value => {
  if (Array.isArray(value)) return value.map(normalize);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => [k, normalize(v)]));
  return value;
};
const equal = (a, b) => JSON.stringify(normalize(a)) === JSON.stringify(normalize(b));

try {
  for (const file of ['0001_quests', '0002_shops', '0003_raid_events', '0004_items', '0006_monsters']) {
    await db.exec(await read(`supabase/migrations/${file}.sql`));
  }
  for (const domain of ['items', 'shops', 'quests', 'monsters', 'raid_events']) {
    await db.exec(await read(`supabase/seed/${domain}_seed.sql`));
  }
  await db.exec("insert into public.quests(id,title,faction,rewards) values ('audit_fixture','audit_fixture','NEUTRAL','{\"iron_ore\":2,\"mat_iron_ore\":2,\"nested\":[\"potion_minor_healing\",\"potion_minor_healing_extra\"]}');");
  const snapshot = async () => {
    const result = {};
    for (const table of ['items', 'shop_items', 'quests', 'monsters', 'raid_events']) {
      result[table] = (await db.query(`select to_jsonb(t)-'updated_at' as data from public.${table} t order by 1`, [])).rows.map(r => r.data);
    }
    return result;
  };
  const delta = await read('supabase/seed/item_shop_cleanup_20261008.sql');
  await db.exec(delta);
  const first = await snapshot();
  await db.exec(delta);
  assert(equal(first, await snapshot()), 'Full delta is not idempotent');
  // Numbered parts must also succeed when each uses a fresh editor/session.
  for (let part = 1; part <= 7; part++) {
    await db.exec(await read(`supabase/seed/item_shop_cleanup_20261008_part${String(part).padStart(2, '0')}.sql`));
  }
  assert(equal(first, await snapshot()), 'Editor parts differ from full delta');
  const fixture = (await db.query("select rewards from public.quests where id='audit_fixture'")).rows[0].rewards;
  assert(equal(fixture, { mat_iron_ore: 4, nested: ['con_small_hp_cell', 'potion_minor_healing_extra'] }), 'Exact references/key collision/array order failed');
  const dbItems = new Map((await db.query('select * from public.items')).rows.map(i => [i.id, i]));
  const itemColumns = ['name', 'type', 'rarity', 'level_requirement', 'buy_price', 'sell_price', 'sell_value', 'max_stack', 'icon_image', 'description', 'equipment_slots', 'stats_bonus', 'special_effects'];
  const catalog = new Map((await json('item_list.json')).items.map(i => [i.id, i]));
  for (const id of new Set([...report.updated_items.map(i => i.id), ...Object.values(aliases)])) {
    const expected = catalog.get(id);
    const actual = dbItems.get(id);
    assert(actual, `Missing DB item ${id}`);
    for (const column of itemColumns) {
      const value = expected[column] ?? (column === 'stats_bonus' ? {} : ['equipment_slots', 'special_effects'].includes(column) ? [] : null);
      assert(equal(actual[column], value), `DB item ${id}/${column} differs from JSON`);
    }
  }
  for (const [oldId, newId] of Object.entries(aliases)) {
    assert(dbItems.get(oldId)?.name === dbItems.get(newId)?.name, `Missing compatible legacy definition ${oldId}`);
  }
  const shops = (await json('shop_inventory.json')).shops;
  for (const shopId of report.changed_shops) {
    const shop = shops.find(s => s.id === shopId);
    let order = 0;
    const expected = shop.categories.flatMap(c => c.items.map(i => ({ shop_id: shopId, category: c.category, ...i, sort_order: order++ })));
    const actual = (await db.query('select shop_id,category,item_id,stock,refresh_time,price_modifier::float,sort_order from public.shop_items where shop_id=$1 order by sort_order', [shopId])).rows;
    assert(equal(actual, expected), `DB shop ${shopId} differs from JSON`);
  }
  const hasRetired = value => {
    if (typeof value === 'string') return value in aliases;
    if (Array.isArray(value)) return value.some(hasRetired);
    if (value && typeof value === 'object') return Object.entries(value).some(([k, v]) => k in aliases || hasRetired(v));
    return false;
  };
  for (const table of ['quests', 'monsters', 'raid_events']) {
    assert(!hasRetired(first[table]), `Retired reference remains in ${table}`);
  }
  const checks = await db.query(await read('supabase/seed/item_shop_cleanup_20261008_verify.sql'));
  assert(checks.rows.every(check => Number(check.issues) === 0), 'Read-only verification reports issues');
  console.log(`PASS: full SQL + 7 editor parts; repeat application; ${report.changed_shops.length} shops match JSON; legacy compatibility and nested references valid.`);
} finally {
  await db.close();
}
