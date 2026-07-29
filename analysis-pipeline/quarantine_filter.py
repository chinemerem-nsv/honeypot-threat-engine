import duckdb
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
# Updated to read sessions.parquet from the project root
INPUT_PATH = os.path.join(PROJECT_ROOT, "sessions.parquet").replace("\\", "/")
QUARANTINE_DIR = os.path.join(PROJECT_ROOT, "quarantine")
QUARANTINE_PATH = os.path.join(QUARANTINE_DIR, "flagged_sessions.parquet").replace("\\", "/")

def quarantine_suspicious_traffic():
    print("[*] Processing dynamic quarantine pipeline...")
    
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    con = duckdb.connect(database=':memory:')
    
    query = f"""
        COPY (
            WITH ip_volumes AS (
                SELECT source_ip, COUNT(*) AS total_ip_sessions
                FROM '{INPUT_PATH}'
                GROUP BY source_ip
            )
            SELECT s.*
            FROM '{INPUT_PATH}' s
            JOIN ip_volumes v ON s.source_ip = v.source_ip
            WHERE v.total_ip_sessions > 500
               OR s.event_count > 10
        ) TO '{QUARANTINE_PATH}' (FORMAT PARQUET);
    """
    
    con.execute(query)
    
    count_df = con.execute(f"SELECT COUNT(*) AS quarantined_count FROM '{QUARANTINE_PATH}';").fetchdf()
    count = count_df['quarantined_count'].iloc[0]
    
    # Compute clean relative path for clear user feedback
    rel_quarantine = os.path.relpath(QUARANTINE_PATH, PROJECT_ROOT).replace("\\", "/")
    print(f"[+] Successfully quarantined {count} dynamic sessions to: {rel_quarantine}")

if __name__ == "__main__":
    quarantine_suspicious_traffic()