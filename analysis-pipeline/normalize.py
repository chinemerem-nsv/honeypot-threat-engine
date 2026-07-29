import duckdb
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
INPUT_PATH = os.path.join(PROJECT_ROOT, "raw-export", "honeypot-replay.jsonl").replace("\\", "/")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "sessions.parquet").replace("\\", "/")

def process_sessions():
    print("[*] Processing sessionization pipeline with DuckDB...")
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    con = duckdb.connect(database=':memory:')
    
    query = f"""
        COPY (
            WITH raw_events AS (
                SELECT 
                    connection_id,
                    source_ip,
                    protocol,
                    sensor_time,
                    action,
                    COALESCE(sensor_time - LAG(sensor_time) OVER (PARTITION BY connection_id ORDER BY sensor_time), INTERVAL '0' SECOND) AS time_delta
                FROM read_json_auto('{INPUT_PATH}')
            ),
            session_flags AS (
                SELECT *,
                    SUM(CASE WHEN time_delta > INTERVAL '300' SECOND THEN 1 ELSE 0 END) OVER (PARTITION BY connection_id ORDER BY sensor_time) AS session_split
                FROM raw_events
            )
            SELECT 
                connection_id,
                source_ip,
                protocol,
                action,
                MIN(sensor_time) AS session_start,
                MAX(sensor_time) AS session_end,
                COUNT(*) AS event_count,
                connection_id || '_' || session_split AS session_id
            FROM session_flags
            GROUP BY connection_id, source_ip, protocol, action, session_split
            ORDER BY session_start ASC
        ) TO '{OUTPUT_PATH}' (FORMAT PARQUET);
    """
    
    con.execute(query)
    
    rel_output = os.path.relpath(OUTPUT_PATH, PROJECT_ROOT).replace("\\", "/")
    print(f"[+] Sessionization pipeline complete. Results saved to root: {rel_output}")

if __name__ == "__main__":
    process_sessions()