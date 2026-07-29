import duckdb
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "derived", "sessions.parquet")).replace("\\", "/")

def inspect_data():
    con = duckdb.connect(database=':memory:')
    
    print("[*] Total Sessions and Event Summary:")
    summary = con.execute(f"""
        SELECT 
            COUNT(DISTINCT session_id) AS total_sessions,
            COUNT(*) AS total_records,
            MIN(session_start) AS earliest_event,
            MAX(session_end) AS latest_event
        FROM '{OUTPUT_PATH}';
    """).fetchdf()
    print(summary)
    
    print("\n[*] Sample Sessions:")
    samples = con.execute(f"""
        SELECT session_id, source_ip, protocol, event_count, session_start 
        FROM '{OUTPUT_PATH}' 
        LIMIT 5;
    """).fetchdf()
    print(samples)

if __name__ == "__main__":
    inspect_data()