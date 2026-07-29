import duckdb
import os
import glob
import yaml
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
# Updated to point to sessions.parquet at the project root
SESSION_PATH = os.path.join(PROJECT_ROOT, "sessions.parquet").replace("\\", "/")
DETECTIONS_DIR = os.path.join(PROJECT_ROOT, "detections")
CLUSTERS_OUTPUT = os.path.join(PROJECT_ROOT, "clusters.json")

def analyze_traffic():
    con = duckdb.connect(database=':memory:')
    
    print("==================================================")
    print("[*] MACRO TRAFFIC ANALYSIS & BASELINE PROFILING")
    print("==================================================")
    
    # 1. Broad visibility: Top Source IPs
    print("\n[*] Top 5 Source IPs by Session Count:")
    top_ips = con.execute(f"""
        SELECT source_ip, COUNT(*) AS session_count
        FROM '{SESSION_PATH}'
        GROUP BY source_ip
        ORDER BY session_count DESC
        LIMIT 5;
    """).fetchdf()
    print(top_ips)
    
    # 2. Broad visibility: Universal Protocol Breakdown
    print("\n[*] Protocol Breakdown (Full Visibility):")
    protocols = con.execute(f"""
        SELECT protocol, COUNT(*) AS session_count
        FROM '{SESSION_PATH}'
        GROUP BY protocol
        ORDER BY session_count DESC;
    """).fetchdf()
    print(protocols)

    print("\n==================================================")
    print("[*] DYNAMIC SIGMA DETECTION RULES EXECUTION")
    print("==================================================")
    
    # Find all YAML detection rules dynamically in the detections folder
    rule_files = glob.glob(os.path.join(DETECTIONS_DIR, "*.yml"))
    print(f"[*] Loaded {len(rule_files)} detection rule(s) from detections/")
    
    all_clusters = []
    cluster_counter = 1

    for rule_file in rule_files:
        with open(rule_file, 'r', encoding='utf-8') as f:
            rule = yaml.safe_load(f)
            
        rule_title = rule.get('title', 'Unknown Rule')
        selection = rule.get('detection', {}).get('selection', {})
        protocol_target = selection.get('protocol')
        action_target = selection.get('action')
        
        print(f"[-] Running rule: {rule_title} [Protocol: {protocol_target}, Action: {action_target}]")
        
        # Build dynamic query filters based on rule configuration
        where_clauses = []
        if protocol_target:
            where_clauses.append(f"protocol = '{protocol_target}'")
        if action_target:
            where_clauses.append(f"action = '{action_target}'")
        
        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
            SELECT 
                source_ip,
                COUNT(*) as event_count,
                MIN(session_start) as first_seen,
                MAX(session_end) as last_seen
            FROM '{SESSION_PATH}'
            {where_sql}
            GROUP BY source_ip
            HAVING COUNT(*) > 3;
        """
        
        try:
            results = con.execute(query).fetchdf()
            if not results.empty:
                for _, row in results.iterrows():
                    cluster_entry = {
                        "id": f"C-{cluster_counter:03d}",
                        "name": rule_title,
                        "source_ip": row['source_ip'],
                        "event_count": int(row['event_count']),
                        "timestamp": str(row['first_seen']),
                        "description": f"Behavioral cluster flagged by rule '{rule_title}': {row['event_count']} matching events from {row['source_ip']}."
                    }
                    all_clusters.append(cluster_entry)
                    cluster_counter += 1
        except Exception as e:
            print(f"[!] Error executing rule {rule_title}: {e}")

    # Output clusters to file so build_and_verify.py and downstream scripts can parse it
    output_data = {
        "total_clusters": len(all_clusters),
        "clusters": all_clusters
    }
    with open(CLUSTERS_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"\n[+] Analysis complete. Generated {len(all_clusters)} behavior clusters -> clusters.json")

if __name__ == "__main__":
    analyze_traffic()