"""Neon PostgreSQL evidence storage; verified TLS and fixed read-only queries."""
import json,hashlib
import psycopg,certifi

def connect(values):
    conn=psycopg.connect(values['url'],sslmode='verify-full',sslrootcert=certifi.where(),connect_timeout=15,prepare_threshold=None)
    conn.execute('SET TRANSACTION READ ONLY')
    conn.execute('SET LOCAL statement_timeout=20000')
    return conn

def load_knowledge(values):
    with connect(values) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT payload,sha256 FROM evidence.taxi_knowledge WHERE id=1")
            row=cur.fetchone()
    if not row:raise ValueError('No evidence snapshot loaded.')
    payload=row[0]
    if hashlib.sha256(payload.encode('utf8')).hexdigest()!=row[1]:raise ValueError('Evidence checksum mismatch.')
    return json.loads(payload)

def load_source(values,path,expected_hash):
    with connect(values) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT content FROM evidence.taxi_sources WHERE path=%s',(path,))
            row=cur.fetchone()
    if not row:raise ValueError('Source unavailable.')
    content=bytes(row[0])
    if hashlib.sha256(content).hexdigest()!=expected_hash:raise ValueError('Source checksum mismatch.')
    return content
