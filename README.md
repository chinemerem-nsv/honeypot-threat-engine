# Honeypot Threat Engine & SOC Telemetry Analysis Pipeline

## Project Overview
The **Honeypot Threat Engine** is an advanced security operations center (SOC) telemetry analysis and ingestion platform. This project ingests raw honeypot replay streams, normalizes and sessionizes event data using high-performance embedded SQL engines (DuckDB), executes dynamic threat quarantine workflows, and applies modular Sigma detection rules to map behavioral attack clusters. 

The pipeline enforces rigorous cryptographic verification, maintaining full data integrity through automated hashing ledgers, evidence indexing, and compliance attestation records.

---

## Repository Information
* **Repository URL:** `https://github.com/chinemerem-nsv/honeypot-threat-engine`

---

## Core Architecture & Directory Layout
* `analysis-pipeline/` — Contains core processing, normalization, quarantine filtering, analysis, and verification scripts.
* `sensor-infrastructure/` — Infrastructure deployment templates, Ansible configuration, and boundary capture scripts.
* `detections/` — Modular Sigma YAML detection rules for threat behavioral identification.
* `tests/` — Automated test suites and fixtures validating pipeline stability.
* `raw-export/` — Native immutable raw honeypot replay datasets (`honeypot-replay.jsonl`).
* `quarantine/` — Isolated high-volume and suspicious traffic partitions (`flagged_sessions.parquet`).

---

## Clean-Build & Reproduction Instructions
To perform a complete clean build, execute the pipeline scripts sequentially from the project root directory:

```bash
# 1. Normalize raw honeypot replay events into a structured session parquet dataset
python analysis-pipeline/normalize.py

# 2. Execute dynamic quarantine filtering for high-volume and suspicious traffic
python analysis-pipeline/quarantine_filter.py

# 3. Perform macro baseline profiling and evaluate Sigma detection rules
python analysis-pipeline/analyze_traffic.py

# 4. Generate final cryptographic verification ledgers, evidence indices, and assessment manifests
python analysis-pipeline/build_and_verify.py