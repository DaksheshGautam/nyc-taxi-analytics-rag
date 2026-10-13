"""Load a retained analysis snapshot into the isolated Neon project. No secrets in output."""
from pathlib import Path
import json,csv,hashlib,os,sys
import psycopg,certifi
from psycopg import sql
ROOT=Path(__file__).resolve().parent
def connect(url,read_only=False):
    conn=psycopg.connect(url,sslmode='verify-full',sslrootcert=certifi.where(),connect_timeout=20,prepare_threshold=None)
    if read_only:conn.execute('SET TRANSACTION READ ONLY')
    conn.execute('SET LOCAL statement_timeout=0')
    return conn
def load(url):
    ledger=[]
    with connect(url) as conn:
        conn.execute((ROOT/'sql/postgresql/01_schema.sql').read_text())
        existing=conn.execute('SELECT count(*) FROM evidence.taxi_knowledge').fetchone()[0]
        if existing:raise RuntimeError('This project already contains a snapshot. Review a migration before replacing it.')
        for p in sorted((ROOT/'data').glob('*.csv')):
            with p.open(encoding='utf-8-sig',newline='') as f:
                rows=csv.reader(f);columns=next(rows);count=0
                command=sql.SQL('COPY results.{} ({}) FROM STDIN').format(sql.Identifier(p.stem),sql.SQL(',').join(map(sql.Identifier,columns)))
                with conn.cursor().copy(command) as cp:
                    for row in rows:cp.write_row([v if v!='' else None for v in row]);count+=1
            ledger.append({'table':'results.'+p.stem,'rows':count})
        app=ROOT/'nyc-taxi-rag';payload=(app/'knowledge.json').read_text(encoding='utf8');kb=json.loads(payload)
        conn.execute('INSERT INTO evidence.taxi_knowledge VALUES (1,%s,%s)',(payload,hashlib.sha256(payload.encode()).hexdigest()))
        for m in kb['manifest']:
            content=(app/'corpus'/m['path']).read_bytes();assert hashlib.sha256(content).hexdigest()==m['sha256']
            conn.execute('INSERT INTO evidence.taxi_sources VALUES (%s,%s,%s)',(m['path'],m['sha256'],content))
        with conn.cursor().copy('COPY evidence.taxi_chunks (chunk_id,source_path,payload) FROM STDIN') as cp:
            for c in kb['chunks']:cp.write_row((c['id'],c['source'],json.dumps(c)))
        for p in [ROOT/'sql/01_stage_2025.sql',ROOT/'sql/02_flags.sql']:conn.execute(p.read_text())
    result={'engine':'PostgreSQL','tables':ledger,'sources':len(kb['manifest']),'chunks':len(kb['chunks'])}
    (ROOT/'postgresql_import_ledger.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
    url=os.environ.get('NEON_ADMIN_URL')
    if not url:raise SystemExit('Set NEON_ADMIN_URL privately before importing.')
    try:print(json.dumps(load(url)))
    except Exception:raise SystemExit('Import failed; inspect privately. Credentials and provider errors were withheld.') from None
