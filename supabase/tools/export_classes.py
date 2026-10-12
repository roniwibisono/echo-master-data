#!/usr/bin/env python3
"""Export four-tier classes with description and the integer isActive flag.

Run from echo-master-data with existing SUPABASE_URL and SUPABASE_ANON_KEY
(or SUPABASE_SERVICE_KEY) environment variables. Does not modify Supabase.
"""
import json,os,urllib.request
from pathlib import Path


def to_class(row):
    result={k:row[k] for k in ['id','name','tier','parent_id','base_stats_bonus','learnable_skill_ids','description']}
    result['isActive']=int(row['is_active'])
    result['content_revision']=row.get('content_revision',1)
    result['emergency_blocked']=row.get('emergency_blocked',False)
    return result


def main():
    url=os.environ['SUPABASE_URL'].rstrip('/')
    key=os.environ.get('SUPABASE_SERVICE_KEY') or os.environ['SUPABASE_ANON_KEY']
    req=urllib.request.Request(url+'/rest/v1/classes?select=*&order=sort_order.asc&limit=1000',headers={'apikey':key,'Authorization':'Bearer '+key})
    with urllib.request.urlopen(req,timeout=30) as response: rows=json.loads(response.read())
    output=[to_class(row) for row in rows]
    if not output: raise ValueError('Refusing to overwrite the catalogue with an empty response')
    Path('class_list.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    print('Exported',len(output),'classes')


if __name__=='__main__': main()
