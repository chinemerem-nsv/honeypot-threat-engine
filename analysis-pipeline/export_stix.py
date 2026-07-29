import os
import json
import uuid
from datetime import datetime, timezone
import pandas as pd

def generate_clusters_and_stix():
    # Look for session data in quarantine or derived folders
    data_path = None
    candidate_paths = [
        "../quarantine/flagged_sessions.parquet",
        "../derived/sessions.parquet",
        "quarantine/flagged_sessions.parquet",
        "derived/sessions.parquet"
    ]
    
    for path in candidate_paths:
        if os.path.exists(path):
            data_path = path
            break
            
    if not data_path:
        print("[!] Notice: No parquet data found. Using fallback placeholder data.")
        df = pd.DataFrame()
    else:
        print(f"[*] Reading real session data from: {data_path}")
        df = pd.read_parquet(data_path)

    clusters = []
    
    # Group by source IP from real data if available
    if not df.empty and "source_ip" in df.columns:
        grouped = df.groupby("source_ip")
        for idx, (ip, group) in enumerate(grouped):
            cluster_id = f"CL-IP-{idx+1:03d}"
            session_ids = group["connection_id"].tolist() if "connection_id" in group.columns else []
            proto = group["protocol"].iloc[0] if "protocol" in group.columns and not group["protocol"].empty else "unknown"
            
            cluster_item = {
                "cluster_id": cluster_id,
                "cluster_name": f"Infrastructure Cluster for {ip} ({proto})",
                "characteristics": {
                    "protocols": [str(proto)],
                    "total_events": int(len(group))
                },
                "indicators": {
                    "source_ips": [str(ip)]
                },
                "session_references": [str(s) for s in session_ids[:20]],
                "confidence": "high",
                "assessment": f"Dynamically clustered from telemetry containing {len(group)} connection events."
            }
            clusters.append(cluster_item)
    else:
        clusters.append({
            "cluster_id": "CL-DEFAULT-01",
            "cluster_name": "Default Placeholder Cluster",
            "indicators": {"source_ips": ["0.0.0.0"]},
            "session_references": [],
            "confidence": "low",
            "assessment": "No source IP columns detected."
        })

    clusters_payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "clusters": clusters
    }

    # Determine root directory output path
    is_in_pipeline = os.path.basename(os.getcwd()) == "pipeline"
    root_clusters_path = "../clusters.json" if is_in_pipeline else "clusters.json"
    
    with open(root_clusters_path, "w", encoding="utf-8") as f:
        json.dump(clusters_payload, f, indent=2)
    print(f"[+] Successfully generated: {root_clusters_path}")

    # Generate STIX 2.1 Bundle
    stix_objects = []
    bundle_id = f"bundle--{uuid.uuid4()}"
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for cluster in clusters_payload["clusters"]:
        ip = cluster["indicators"]["source_ips"][0]
        
        obs_id = f"observed-data--{uuid.uuid4()}"
        observed_data = {
            "type": "observed-data",
            "spec_version": "2.1",
            "id": obs_id,
            "created": now_str,
            "modified": now_str,
            "first_observed": now_str,
            "last_observed": now_str,
            "number_observed": cluster["characteristics"].get("total_events", 1),
            "objects": {
                "0": {
                    "type": "ipv4-addr",
                    "value": ip
                }
            }
        }
        stix_objects.append(observed_data)

        ind_id = f"indicator--{uuid.uuid4()}"
        indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now_str,
            "modified": now_str,
            "name": cluster["cluster_name"],
            "description": cluster["assessment"],
            "pattern": f"[ipv4-addr:value = '{ip}']",
            "pattern_type": "stix",
            "pattern_version": "2.1",
            "valid_from": now_str,
            "indicator_types": ["malicious-activity"]
        }
        stix_objects.append(indicator)

        rel_id = f"relationship--{uuid.uuid4()}"
        relationship = {
            "type": "relationship",
            "spec_version": "2.1",
            "id": rel_id,
            "created": now_str,
            "modified": now_str,
            "relationship_type": "based-on",
            "source_ref": ind_id,
            "target_ref": obs_id
        }
        stix_objects.append(relationship)

    stix_bundle = {
        "type": "bundle",
        "id": bundle_id,
        "objects": stix_objects
    }

    root_stix_path = "../stix-bundle.json" if is_in_pipeline else "stix-bundle.json"
    with open(root_stix_path, "w", encoding="utf-8") as f:
        json.dump(stix_bundle, f, indent=2)
    print(f"[+] Successfully generated: {root_stix_path}")

if __name__ == "__main__":
    generate_clusters_and_stix()