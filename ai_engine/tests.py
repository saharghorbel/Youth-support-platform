"""
Tests for AI explainable scoring engine.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .scoring import explainable_risk_score

User = get_user_model()


class TestExplainableRiskScore:
    """Test the explainable_risk_score function."""
    
    def test_critical_student(self):
        """Test critical risk level detection."""
        data = {
            'attendance_rate': 45.0,
            'avg_grade': 6.0,
            'behavior_incidents': 7,
            'missed_appointments': 4,
            'days_since_last_contact': 90
        }
        result = explainable_risk_score(data)
        
        assert result['level'] == 'CRITICAL'
        assert result['score'] >= 75
        assert 'factors' in result
        assert len(result['factors']) > 0
    
    def test_high_student(self):
        """Test high risk level detection."""
        data = {
            'attendance_rate': 62.0,
            'avg_grade': 9.0,
            'behavior_incidents': 4,
            'missed_appointments': 2,
            'days_since_last_contact': 45
        }
        result = explainable_risk_score(data)
        
        assert result['level'] == 'HIGH'
        assert 50 <= result['score'] < 75
    
    def test_medium_student(self):
        """Test medium risk level detection."""
        data = {
            'attendance_rate': 78.0,
            'avg_grade': 12.0,
            'behavior_incidents': 2,
            'missed_appointments': 1,
            'days_since_last_contact': 20
        }
        result = explainable_risk_score(data)
        
        assert result['level'] == 'MEDIUM'
        assert 15 <= result['score'] < 50
    
    def test_low_student(self):
        """Test low risk level detection."""
        data = {
            'attendance_rate': 92.0,
            'avg_grade': 17.0,
            'behavior_incidents': 0,
            'missed_appointments': 0,
            'days_since_last_contact': 5
        }
        result = explainable_risk_score(data)
        
        assert result['level'] == 'LOW'
        assert result['score'] < 25
    
    def test_output_has_required_keys(self):
        """Test that output contains all required keys."""
        data = {
            'attendance_rate': 80.0,
            'avg_grade': 14.0
        }
        result = explainable_risk_score(data)
        
        required_keys = ['score', 'level', 'color', 'factors', 'recommendations', 'confidence', 'disclaimer']
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"
    
    def test_factors_have_required_keys(self):
        """Test that each factor has required keys."""
        data = {
            'attendance_rate': 75.0,
            'avg_grade': 12.0,
            'behavior_incidents': 2
        }
        result = explainable_risk_score(data)
        
        assert len(result['factors']) > 0
        
        required_factor_keys = ['name', 'value', 'contribution', 'weight', 'status', 'explanation']
        for factor in result['factors']:
            for key in required_factor_keys:
                assert key in factor, f"Factor missing required key: {key}"
    
    def test_recommendations_not_empty(self):
        """Test that recommendations are provided for any input."""
        data = {
            'attendance_rate': 50.0,
            'avg_grade': 7.0,
            'behavior_incidents': 5,
            'missed_appointments': 3
        }
        result = explainable_risk_score(data)
        
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0
    
    def test_disclaimer_always_present(self):
        """Test that disclaimer is always present."""
        data = {'attendance_rate': 80.0}
        result = explainable_risk_score(data)
        
        assert 'disclaimer' in result
        assert 'Decision support' in result['disclaimer']
    
    def test_missing_data_handled(self):
        """Test that missing data doesn't cause exceptions."""
        data = {}
        result = explainable_risk_score(data)
        
        assert 'score' in result
        assert 'level' in result
        assert result['level'] == 'LOW'  # No data means no risk
    
    def test_confidence_high_with_full_data(self):
        """Test that confidence is HIGH when all data is provided."""
        data = {
            'attendance_rate': 85.0,
            'avg_grade': 15.0,
            'behavior_incidents': 1,
            'missed_appointments': 0,
            'support_history': 0,
            'days_since_last_contact': 10
        }
        result = explainable_risk_score(data)
        
        assert result['confidence'] == 'HIGH'
    
    def test_confidence_low_with_no_data(self):
        """Test that confidence is LOW when minimal data is provided."""
        data = {}
        result = explainable_risk_score(data)
        
        assert result['confidence'] == 'LOW'


@pytest.mark.django_db
class TestAIScoreEndpoint(TestCase):
    """Test the AI score API endpoint."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testoperator',
            password='testpass123',
            role='OPERATOR'
        )
    
    def test_endpoint_requires_auth(self):
        """Test that endpoint requires authentication."""
        response = self.client.post('/api/ai/score/', {
            'attendance_rate': 80.0,
            'avg_grade': 14.0
        }, format='json')
        
        # Should redirect to login or return 401/403
        assert response.status_code in [302, 401, 403]
    
    def test_endpoint_returns_score(self):
        """Test that authenticated POST returns score."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/ai/score/', {
            'attendance_rate': 80.0,
            'avg_grade': 14.0,
            'behavior_incidents': 2,
            'missed_appointments': 1,
            'days_since_last_contact': 15
        }, format='json')
        
        assert response.status_code == 200
        data = response.json()
        assert 'score' in data
        assert 'level' in data
        assert 'factors' in data
    
    def test_endpoint_rejects_invalid_json(self):
        """Test that endpoint rejects invalid JSON."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/ai/score/', 
                                   'invalid json',
                                   content_type='application/json')
        
        assert response.status_code == 400
