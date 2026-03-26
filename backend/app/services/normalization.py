
from typing import Dict, Any, Optional

SEVERITY_MAP = {
    range(0, 4): "informational",
    range(4, 8): "low",
    range(8, 12): "medium",
    range(12, 16): "high",
}

def map_severity(rule_level: int) -> str:
    for r, sev in SEVERITY_MAP.items():
        if rule_level in r:
            return sev
    return "critical" if rule_level >= 16 else "low"

def normalize_wazuh_alert(raw: Dict[str, Any]) -> Dict[str, Any]:
    rule = raw.get("rule", {})
    agent = raw.get("agent", {})
    level = int(rule.get("level", 0))
    mitre = rule.get("mitre", {})
    mitre_ids = mitre.get("id", []) if isinstance(mitre, dict) else []
    groups = rule.get("groups", [])
    return {
        "external_id": raw.get("id"),
        "agent_id": str(agent.get("id", "")),
        "agent_name": agent.get("name"),
        "agent_ip": agent.get("ip"),
        "rule_id": str(rule.get("id", "")),
        "rule_description": rule.get("description"),
        "rule_level": level,
        "rule_groups": groups,
        "mitre_ids": mitre_ids,
        "severity": map_severity(level),
        "normalized": True,
    }

def normalize_alert(source: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    if source == "wazuh":
        return normalize_wazuh_alert(raw)
    return {"normalized": False, "severity": "low"}
