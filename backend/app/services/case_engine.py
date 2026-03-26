
from sqlalchemy.orm import Session
from backend.app.models.alert import Alert
from backend.app.models.case import Case
import uuid

def create_case_from_alert(alert: Alert, db: Session) -> Case:
    mitre = alert.mitre_ids or []
    case = Case(
        title=f"[AUTO] {alert.rule_description or alert.rule_id or alert.source}",
        description=f"Auto-generated case from alert {alert.id}. Agent: {alert.agent_name}. Rule: {alert.rule_description}",
        severity=alert.severity,
        status="open",
        priority="medium" if alert.severity in ["low", "informational"] else "high",
        customer_id=alert.customer_id,
        alert_count=1,
        mitre_tactics=mitre,
        tags=[alert.source, f"rule:{alert.rule_id}"] if alert.rule_id else [alert.source],
    )
    db.add(case)
    db.flush()
    alert.case_id = case.id
    alert.status = "acknowledged"
    db.commit()
    db.refresh(case)
    return case

def auto_case_high_severity(db: Session, customer_id) -> list:
    uncased_high = db.query(Alert).filter(
        Alert.customer_id == customer_id,
        Alert.case_id == None,
        Alert.severity.in_(["high", "critical"]),
        Alert.status == "new"
    ).all()
    cases = []
    for alert in uncased_high:
        c = create_case_from_alert(alert, db)
        cases.append(c)
    return cases
