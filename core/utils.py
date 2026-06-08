"""
Utility functions for the Youth Support Platform.
"""
from accounts.models import AuditLog


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_audit_log(user, action_type, resource_type, resource_id, 
                     description, result='SUCCESS', reason=None, request=None):
    """
    Create an audit log entry.
    
    Args:
        user: User performing the action
        action_type: Type of action (CREATE, UPDATE, DELETE, etc.)
        resource_type: Type of resource affected
        resource_id: ID of the affected resource
        description: Human-readable description
        result: Result of the action (SUCCESS, FAILURE, BLOCKED)
        reason: Reason for failure or blocking (optional)
        request: HTTP request object (optional, for IP and user agent)
    """
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    return AuditLog.objects.create(
        user=user,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        result=result,
        reason=reason,
        ip_address=ip_address,
        user_agent=user_agent
    )


def validate_age_range(age, min_age=0, max_age=25):
    """
    Validate age is within acceptable range for youth support.
    
    Args:
        age: Age to validate
        min_age: Minimum acceptable age
        max_age: Maximum acceptable age
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if age < min_age:
        return False, f"Age must be at least {min_age}"
    if age > max_age:
        return False, f"Age must not exceed {max_age}"
    return True, None


def calculate_risk_score(indicators):
    """
    Calculate a simple risk score based on multiple indicators.
    
    Args:
        indicators: Dictionary of indicator names and values
    
    Returns:
        float: Risk score between 0 and 100
    """
    if not indicators:
        return 0.0
    
    total_score = sum(indicators.values())
    max_possible = len(indicators) * 100
    
    return (total_score / max_possible) * 100 if max_possible > 0 else 0.0


def get_risk_level(score):
    """
    Determine risk level based on score.
    
    Args:
        score: Risk score (0-100)
    
    Returns:
        str: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
    """
    if score < 25:
        return 'LOW'
    elif score < 50:
        return 'MEDIUM'
    elif score < 75:
        return 'HIGH'
    else:
        return 'CRITICAL'
