"""
Fetch warm (curated, high-quality) cybersecurity knowledge from official sources.

Outputs:
- data_warm/mitre_attack_enterprise_techniques.txt
- data_warm/nist_pqc_standards_summary.txt
"""

import os
from datetime import datetime, timezone

import requests

from config import WARM_DATA_DIR


MITRE_ATTACK_STIX_URL = (
    "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
)

# Official NIST FIPS landing pages for post-quantum standards
NIST_FIPS_URLS = [
    "https://csrc.nist.gov/pubs/fips/203/final",
    "https://csrc.nist.gov/pubs/fips/204/final",
    "https://csrc.nist.gov/pubs/fips/205/final",
]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def fetch_mitre_attack(limit: int = 550) -> str:
    r = requests.get(MITRE_ATTACK_STIX_URL, timeout=60)
    r.raise_for_status()
    payload = r.json()
    objects = payload.get("objects", [])

    lines = [
        "Source: MITRE ATT&CK (enterprise-attack STIX)",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]

    count = 0
    for obj in objects:
        if obj.get("type") != "attack-pattern":
            continue
        name = obj.get("name", "N/A")
        description = (obj.get("description") or "").replace("\n", " ")
        ext = obj.get("external_references", [])
        attack_id = "N/A"
        for ref in ext:
            if ref.get("source_name") == "mitre-attack":
                attack_id = ref.get("external_id", "N/A")
                break
        lines.extend(
            [
                f"Technique ID: {attack_id}",
                f"Technique Name: {name}",
                f"Description: {description[:1000]}",
                "---",
            ]
        )
        count += 1
        if count >= limit:
            break
    return "\n".join(lines)


def fetch_nist_pqc_summary() -> str:
    lines = [
        "Source: NIST CSRC FIPS standards pages",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "Topic: Post-Quantum Cryptography Standards",
        "",
    ]
    for url in NIST_FIPS_URLS:
        lines.extend(
            [
                f"Standard URL: {url}",
                "Summary: Official NIST Federal Information Processing Standard reference for PQC migration.",
                "---",
            ]
        )
    return "\n".join(lines)


def main():
    ensure_dir(WARM_DATA_DIR)

    mitre_txt = fetch_mitre_attack()
    pqc_txt = fetch_nist_pqc_summary()

    mitre_path = os.path.join(WARM_DATA_DIR, "mitre_attack_enterprise_techniques.txt")
    pqc_path = os.path.join(WARM_DATA_DIR, "nist_pqc_standards_summary.txt")

    with open(mitre_path, "w", encoding="utf-8") as f:
        f.write(mitre_txt)
    with open(pqc_path, "w", encoding="utf-8") as f:
        f.write(pqc_txt)

    print(f"[OK] Warm dataset written:\n- {mitre_path}\n- {pqc_path}")


if __name__ == "__main__":
    main()
