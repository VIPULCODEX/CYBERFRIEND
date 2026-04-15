"""
Fetch hot (latest) cybersecurity intel from official sources.

Outputs:
- data_hot/cisa_kev_latest.txt
- data_hot/nvd_recent_cves.txt
"""

import json
import os
from datetime import datetime, timezone

import requests

from config import BASE_DIR, HOT_DATA_DIR


CISA_KEV_JSON_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def fetch_cisa_kev(limit: int = 400) -> str:
    r = requests.get(CISA_KEV_JSON_URL, timeout=30)
    r.raise_for_status()
    payload = r.json()
    vulns = payload.get("vulnerabilities", [])[:limit]

    lines = [
        f"Source: CISA KEV",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Catalog Version: {payload.get('catalogVersion', 'unknown')}",
        "",
    ]
    for item in vulns:
        lines.extend(
            [
                f"CVE: {item.get('cveID', 'N/A')}",
                f"Vendor/Product: {item.get('vendorProject', 'N/A')} / {item.get('product', 'N/A')}",
                f"Vulnerability Name: {item.get('vulnerabilityName', 'N/A')}",
                f"Date Added: {item.get('dateAdded', 'N/A')}",
                f"Required Action: {item.get('requiredAction', 'N/A')}",
                f"Known Ransomware Use: {item.get('knownRansomwareCampaignUse', 'N/A')}",
                f"Notes: {item.get('notes', '')}",
                "---",
            ]
        )
    return "\n".join(lines)


def fetch_nvd_recent(limit: int = 120) -> str:
    params = {
        "resultsPerPage": limit,
        "startIndex": 0,
    }
    r = requests.get(NVD_API_URL, params=params, timeout=30)
    r.raise_for_status()
    payload = r.json()
    vulns = payload.get("vulnerabilities", [])

    lines = [
        "Source: NVD CVE API v2",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Count: {len(vulns)}",
        "",
    ]
    for row in vulns:
        cve = row.get("cve", {})
        cve_id = cve.get("id", "N/A")
        desc = ""
        for desc_row in cve.get("descriptions", []):
            if desc_row.get("lang") == "en":
                desc = desc_row.get("value", "")
                break
        severity = "N/A"
        metrics = cve.get("metrics", {})
        if metrics.get("cvssMetricV31"):
            severity = metrics["cvssMetricV31"][0]["cvssData"].get("baseSeverity", "N/A")
        elif metrics.get("cvssMetricV30"):
            severity = metrics["cvssMetricV30"][0]["cvssData"].get("baseSeverity", "N/A")
        elif metrics.get("cvssMetricV2"):
            severity = metrics["cvssMetricV2"][0]["baseSeverity"]

        lines.extend(
            [
                f"CVE: {cve_id}",
                f"Severity: {severity}",
                f"Published: {cve.get('published', 'N/A')}",
                f"Last Modified: {cve.get('lastModified', 'N/A')}",
                f"Description: {desc[:900]}",
                "---",
            ]
        )
    return "\n".join(lines)


def main():
    ensure_dir(HOT_DATA_DIR)
    kev_txt = fetch_cisa_kev()
    nvd_txt = fetch_nvd_recent()

    kev_path = os.path.join(HOT_DATA_DIR, "cisa_kev_latest.txt")
    nvd_path = os.path.join(HOT_DATA_DIR, "nvd_recent_cves.txt")
    with open(kev_path, "w", encoding="utf-8") as f:
        f.write(kev_txt)
    with open(nvd_path, "w", encoding="utf-8") as f:
        f.write(nvd_txt)

    print(f"[OK] Hot dataset written:\n- {kev_path}\n- {nvd_path}")


if __name__ == "__main__":
    main()
