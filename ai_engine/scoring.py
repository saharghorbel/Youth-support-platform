"""
AI Explainable Scoring Engine
Fully transparent rule-based risk assessment with human-readable explanations.
NO black-box ML — every decision is traceable and auditable.
"""
from typing import Dict, List, Any


def explainable_risk_score(data: dict) -> dict:
    """
    Calculate explainable risk score based on multiple indicators.
    
    Args:
        data: Dictionary with keys:
            - attendance_rate: float (0-100, percentage of days present)
            - avg_grade: float (0-20, Tunisian grading system)
            - behavior_incidents: int (number of incidents this semester)
            - missed_appointments: int (number of missed health appointments)
            - support_history: int (number of previous interventions)
            - days_since_last_contact: int (days since last follow-up)
    
    Returns:
        Dictionary with score, level, factors, recommendations, confidence, disclaimer
    """
    # Initialize
    score = 0.0
    factors = []
    recommendations = []
    data_completeness = 0
    total_fields = 6
    
    # Extract data with defaults
    attendance_rate = data.get('attendance_rate')
    avg_grade = data.get('avg_grade')
    behavior_incidents = data.get('behavior_incidents', 0)
    missed_appointments = data.get('missed_appointments', 0)
    support_history = data.get('support_history', 0)
    days_since_last_contact = data.get('days_since_last_contact', 0)
    
    # Count available data
    if attendance_rate is not None:
        data_completeness += 1
    if avg_grade is not None:
        data_completeness += 1
    if behavior_incidents is not None:
        data_completeness += 1
    if missed_appointments is not None:
        data_completeness += 1
    if support_history is not None:
        data_completeness += 1
    if days_since_last_contact is not None:
        data_completeness += 1
    
    # Factor 1: Attendance Rate
    if attendance_rate is not None:
        if attendance_rate < 60:
            contribution = 40.0
            status = "CRITICAL"
            explanation = f"Attendance rate of {attendance_rate:.1f}% is critically low (below 60%). Immediate intervention required."
            recommendations.append("Immediate family contact required within 48 hours")
        elif attendance_rate < 75:
            contribution = 25.0
            status = "ALERT"
            explanation = f"Attendance rate of {attendance_rate:.1f}% is concerning (below 75%). Close monitoring needed."
        elif attendance_rate < 85:
            contribution = 10.0
            status = "WARNING"
            explanation = f"Attendance rate of {attendance_rate:.1f}% is below optimal (85%). Minor concern."
        else:
            contribution = 0.0
            status = "OK"
            explanation = f"Attendance rate of {attendance_rate:.1f}% is good (above 85%)."
        
        score += contribution
        factors.append({
            "name": "Attendance Rate",
            "value": f"{attendance_rate:.1f}%",
            "contribution": contribution,
            "weight": 40.0,
            "status": status,
            "explanation": explanation
        })
    
    # Factor 2: Academic Performance
    if avg_grade is not None:
        if avg_grade < 8:
            contribution = 30.0
            status = "CRITICAL"
            explanation = f"Average grade of {avg_grade:.1f}/20 is critically low (below 8/20). Academic support urgently needed."
            recommendations.append("Academic tutoring referral recommended")
        elif avg_grade < 12:
            contribution = 20.0
            status = "ALERT"
            explanation = f"Average grade of {avg_grade:.1f}/20 is below passing standard (12/20). Academic intervention recommended."
            recommendations.append("Academic tutoring referral recommended")
        elif avg_grade < 14:
            contribution = 10.0
            status = "WARNING"
            explanation = f"Average grade of {avg_grade:.1f}/20 is below target (14/20). Additional support may help."
        else:
            contribution = 0.0
            status = "OK"
            explanation = f"Average grade of {avg_grade:.1f}/20 is satisfactory (above 14/20)."
        
        score += contribution
        factors.append({
            "name": "Academic Performance",
            "value": f"{avg_grade:.1f}/20",
            "contribution": contribution,
            "weight": 30.0,
            "status": status,
            "explanation": explanation
        })
    
    # Factor 3: Behavior Incidents
    if behavior_incidents >= 5:
        contribution = 20.0
        status = "ALERT"
        explanation = f"{behavior_incidents} behavior incidents recorded (5 or more). Significant behavioral concerns."
        recommendations.append("Counselor meeting scheduled within 1 week")
    elif behavior_incidents >= 3:
        contribution = 10.0
        status = "WARNING"
        explanation = f"{behavior_incidents} behavior incidents recorded (3-4). Behavioral monitoring recommended."
        recommendations.append("Counselor meeting scheduled within 1 week")
    else:
        contribution = 0.0
        status = "OK"
        explanation = f"{behavior_incidents} behavior incident(s) recorded. Behavior is acceptable."
    
    score += contribution
    factors.append({
        "name": "Behavior Incidents",
        "value": behavior_incidents,
        "contribution": contribution,
        "weight": 20.0,
        "status": status,
        "explanation": explanation
    })
    
    # Factor 4: Missed Appointments
    if missed_appointments >= 3:
        contribution = 20.0
        status = "ALERT"
        explanation = f"{missed_appointments} appointments missed (3 or more). Health engagement is critically low."
        recommendations.append("Health follow-up reminder — send today")
    elif missed_appointments >= 1:
        contribution = 10.0
        status = "WARNING"
        explanation = f"{missed_appointments} appointment(s) missed. Follow-up reminder needed."
        recommendations.append("Health follow-up reminder — send today")
    else:
        contribution = 0.0
        status = "OK"
        explanation = f"{missed_appointments} appointments missed. Health engagement is good."
    
    score += contribution
    factors.append({
        "name": "Missed Appointments",
        "value": missed_appointments,
        "contribution": contribution,
        "weight": 20.0,
        "status": status,
        "explanation": explanation
    })
    
    # Factor 5: Days Since Last Contact
    if days_since_last_contact > 60:
        contribution = 15.0
        status = "ALERT"
        explanation = f"{days_since_last_contact} days since last contact (over 60 days). Extended disengagement detected."
        recommendations.append("Schedule check-in contact")
    elif days_since_last_contact > 30:
        contribution = 10.0
        status = "WARNING"
        explanation = f"{days_since_last_contact} days since last contact (over 30 days). Regular contact recommended."
        recommendations.append("Schedule check-in contact")
    else:
        contribution = 0.0
        status = "OK"
        explanation = f"{days_since_last_contact} days since last contact. Contact frequency is adequate."
    
    score += contribution
    factors.append({
        "name": "Days Since Last Contact",
        "value": days_since_last_contact,
        "contribution": contribution,
        "weight": 15.0,
        "status": status,
        "explanation": explanation
    })
    
    # Factor 6: Support History (informational only, doesn't add to score)
    if support_history >= 2:
        status = "WARNING"
        explanation = f"{support_history} previous interventions recorded. History of requiring support."
        recommendations.append(f"Note: {support_history} previous interventions on record — review past strategies")
    elif support_history == 1:
        status = "OK"
        explanation = f"{support_history} previous intervention recorded. Some support history exists."
    else:
        status = "OK"
        explanation = "No previous interventions recorded. First-time case."
    
    factors.append({
        "name": "Support History",
        "value": support_history,
        "contribution": 0.0,
        "weight": 0.0,
        "status": status,
        "explanation": explanation
    })
    
    # Determine risk level based on score
    if score >= 60:
        level = "CRITICAL"
        color = "darkred"
    elif score >= 35:
        level = "HIGH"
        color = "red"
    elif score >= 15:
        level = "MEDIUM"
        color = "orange"
    else:
        level = "LOW"
        color = "green"
    
    # Determine confidence based on data completeness
    completeness_ratio = data_completeness / total_fields
    if completeness_ratio >= 0.8:
        confidence = "HIGH"
    elif completeness_ratio >= 0.5:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"
    
    # Remove duplicate recommendations
    recommendations = list(dict.fromkeys(recommendations))
    
    # Build result
    result = {
        "score": round(score, 2),
        "level": level,
        "color": color,
        "factors": factors,
        "recommendations": recommendations,
        "confidence": confidence,
        "disclaimer": "Decision support only, not final authority. Human review and judgment required for all interventions."
    }
    
    return result
