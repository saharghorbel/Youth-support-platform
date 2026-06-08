"""
AI Engine API Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsOperator
from core.utils import create_audit_log
from .scoring import explainable_risk_score


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsOperator])
def score_risk(request):
    """
    POST /api/ai/score/
    
    Calculate explainable risk score based on input indicators.
    
    Request body:
    {
        "attendance_rate": float (0-100),
        "avg_grade": float (0-20),
        "behavior_incidents": int,
        "missed_appointments": int,
        "support_history": int,
        "days_since_last_contact": int
    }
    
    Returns:
    {
        "score": float,
        "level": str,
        "color": str,
        "factors": [...],
        "recommendations": [...],
        "confidence": str,
        "disclaimer": str
    }
    """
    try:
        # Get input data
        data = request.data
        
        # Validate required fields (at least one indicator must be present)
        if not any(key in data for key in [
            'attendance_rate', 'avg_grade', 'behavior_incidents',
            'missed_appointments', 'support_history', 'days_since_last_contact'
        ]):
            create_audit_log(
                user=request.user,
                action_type='AI_SCORE',
                resource_type='RiskScore',
                resource_id='0',
                description='AI scoring request failed: no indicators provided',
                result='FAILED',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return Response(
                {"error": "At least one risk indicator must be provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate data types and ranges
        if 'attendance_rate' in data:
            try:
                attendance_rate = float(data['attendance_rate'])
                if not 0 <= attendance_rate <= 100:
                    raise ValueError("Attendance rate must be between 0 and 100")
            except (ValueError, TypeError) as e:
                return Response(
                    {"error": f"Invalid attendance_rate: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if 'avg_grade' in data:
            try:
                avg_grade = float(data['avg_grade'])
                if not 0 <= avg_grade <= 20:
                    raise ValueError("Average grade must be between 0 and 20")
            except (ValueError, TypeError) as e:
                return Response(
                    {"error": f"Invalid avg_grade: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate risk score
        result = explainable_risk_score(data)
        
        # Log the scoring request
        create_audit_log(
            user=request.user,
            action_type='AI_SCORE',
            resource_type='RiskScore',
            resource_id=result["level"],
            description=f'AI risk scoring calculated: level={result["level"]}, score={result["score"]}, confidence={result["confidence"]}',
            result='SUCCESS',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Log the error
        create_audit_log(
            user=request.user,
            action_type='AI_SCORE',
            resource_type='RiskScore',
            resource_id='ERROR',
            description=f'AI scoring request failed: {str(e)}',
            result='FAILED',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response(
            {"error": "Internal server error during risk calculation"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
