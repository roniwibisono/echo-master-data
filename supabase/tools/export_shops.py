#!/usr/bin/env python3
"""Publish shops from Supabase back to shop_inventory.json (CDN).

Re-nests shops + shop_items rows into the exact
{meta, shops:[{id,name,...,categories:[{category,items:[...]}]}]} structure the
Flutter client reads. Run after editing in Supabase, then commit + push.

    export SUPABASE_URL="https://<ref>.supabase.co"
    export SUPABASE_SERVICE_KEY="<service_role_key>"
    python3 supabase/tools/export_shops.py
"""
import json, os, sys, urllib.request

def _get(path):
    base = os.environ['SUPABASE_URL'].rstrip('/')
    key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    req = urllib.request.Request(f'{base}/rest/v1/{path}', headers={
        'apikey': key, 'Authorization': f'Bearer {key}',
        'Accept': 'application/json', 'Range-Unit': 'items', 'Range': '0-99999',
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    try:
        shops = _get('shops?select=*&order=sort_order.asc')
        items = _get('shop_items?select=*&order=shop_id.asc,sort_order.asc')
    except KeyError as e:
        sys.exit(f'Missing env var: {e}. Set SUPABASE_URL and SUPABASE_SERVICE_KEY.')

    items_by_shop = {}
    for it in items:
        items_by_shop.setdefault(it['shop_id'], []).append(it)

    out_shops = []
    for sh in shops:
        rows = sorted(items_by_shop.get(sh['id'], []), key=lambda r: r.get('sort_order', 0))
        # group by category, preserving first-appearance order
        cats, order = {}, []
        for r in rows:
            c = r['category']
            if c not in cats:
                cats[c] = []; order.append(c)
            cats[c].append({
                'item_id': r['item_id'], 'stock': r['stock'],
                'refresh_time': r['refresh_time'],
                'price_modifier': float(r['price_modifier']),
            })
        shop_obj = {'id': sh['id'], 'name': sh['name']}
        if sh.get('faction') is not None: shop_obj['faction'] = sh['faction']
        if sh.get('buy_currency') is not None: shop_obj['buy_currency'] = sh['buy_currency']
        if sh.get('description') is not None: shop_obj['description'] = sh['description']
        shop_obj['categories'] = [{'category': c, 'items': cats[c]} for c in order]
        out_shops.append(shop_obj)

    root = os.getcwd()
    path = os.path.join(root, 'shop_inventory.json')
    wrapper = {}
    if os.path.exists(path):
        existing = json.load(open(path))
        if isinstance(existing, dict):
            wrapper = {k: v for k, v in existing.items() if k != 'shops'}
    wrapper['shops'] = out_shops
    json.dump(wrapper, open(path, 'w'), indent=2, ensure_ascii=False)
    print(f'Exported {len(out_shops)} shops, {len(items)} items -> shop_inventory.json')

if __name__ == '__main__':
    main()
