"""Import detailed CSV.gz aggregates into a new PostgreSQL database.

Set NEON_ADMIN_URL privately. Run after load_postgresql.py, with
postgres_import_data beside this file. No credentials are written.
"""
from pathlib import Path
import os,csv,gzip,json
from psycopg import sql
from load_postgresql import connect

def load_detail(url,folder=None):
    folder=Path(folder or Path(__file__).parent/'postgres_import_data');ledger=[]
    with connect(url) as c:
        c.execute('CREATE SCHEMA IF NOT EXISTS detail')
        for p in sorted(folder.glob('*.csv.gz')):
            name=p.name.removesuffix('.csv.gz')
            with gzip.open(p,'rt',encoding='utf8',newline='') as f:columns=next(csv.reader(f))
            defs=[]
            for col in columns:
                typ='DATE' if col=='pickup_date' else 'TEXT' if col=='source_month' else 'SMALLINT' if col in ['pickup_zone','dropoff_zone','pickup_hour','payment_type'] else 'BIGINT' if col in ['trips','fare_n','distance_n','card_tip_n','cbd_fee_n'] else 'DOUBLE PRECISION'
                defs.append(sql.SQL('{} {}').format(sql.Identifier(col),sql.SQL(typ)))
            c.execute(sql.SQL('CREATE TABLE detail.{} ({})').format(sql.Identifier(name),sql.SQL(',').join(defs)))
            with gzip.open(p,'rb') as f,c.cursor().copy(sql.SQL('COPY detail.{} FROM STDIN WITH (FORMAT CSV,HEADER TRUE)').format(sql.Identifier(name))) as cp:
                while block:=f.read(4*1024*1024):cp.write(block)
            rows,trips,fares=c.execute(sql.SQL('SELECT count(*),sum(trips),sum(fare_n) FROM detail.{}').format(sql.Identifier(name))).fetchone()
            assert (int(trips),int(fares))==(48157684,44727165)
            dims=[x for x in ['pickup_date','source_month','pickup_zone','pickup_hour','payment_type','dropoff_zone'] if x in columns]
            c.execute(sql.SQL('CREATE INDEX ON detail.{} ({})').format(sql.Identifier(name),sql.SQL(',').join(map(sql.Identifier,dims))))
            c.execute(sql.SQL('ANALYZE detail.{}').format(sql.Identifier(name)))
            ledger.append({'table':name,'rows':rows,'trips':int(trips),'fare_n':int(fares)})
        if c.execute('SELECT count(*) FROM taxi_analysis.zones').fetchone()[0]==0:
            with (folder/'zones.csv').open('rb') as f,c.cursor().copy('COPY taxi_analysis.zones FROM STDIN WITH (FORMAT CSV,HEADER TRUE)') as cp:cp.write(f.read())
    return ledger

if __name__=='__main__':
    if not os.environ.get('NEON_ADMIN_URL'):raise SystemExit('Set NEON_ADMIN_URL privately before importing.')
    try:print(json.dumps(load_detail(os.environ['NEON_ADMIN_URL'])))
    except Exception:raise SystemExit('Detailed import failed; no connection secrets printed.') from None
