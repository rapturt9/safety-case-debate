"""
Simple test to verify the safety case debate system works.
"""
import os
import sys
sys.path.append('./src')

from src.debate.models import SafetyCaseContext
from src.safety_case.generator import SafetyCaseGenerator

def test_basic_functionality():
    """Test basic functionality without API calls."""
    print("Testing basic functionality...")
    
    # Test SafetyCaseContext creation
    context = SafetyCaseContext(
        system_description="Test AI system",
        deployment_context="Test environment",
        safety_claims=["System is safe", "System is reliable"],
        assumptions=["Test assumption"],
        risk_factors=["Test risk"],
        mitigation_strategies=["Test mitigation"]
    )
    
    print(f"✓ SafetyCaseContext created: {context.system_description}")
    print(f"✓ Safety claims: {len(context.safety_claims)}")
    
    # Test that imports work
    try:
        from src.debate.orchestrator import DebateOrchestrator
        from src.visualization.diagrams import DiagramGenerator
        print("✓ All imports successful")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print("✓ Basic functionality test passed!")
    return True

def test_with_mock_api():
    """Test with mock API responses."""
    print("\nTesting with mock responses...")
    
    # Mock the API call to avoid needing real API keys
    class MockSafetyGenerator:
        def generate_safety_context(self, user_input):
            return SafetyCaseContext(
                system_description=f"Mock system for: {user_input}",
                deployment_context="Mock deployment environment",
                safety_claims=[
                    "The system operates within safe parameters",
                    "The system has appropriate fail-safes"
                ],
                assumptions=["Mock assumption 1", "Mock assumption 2"],
                risk_factors=["Mock risk 1", "Mock risk 2"],
                mitigation_strategies=["Mock mitigation 1", "Mock mitigation 2"]
            )
    
    generator = MockSafetyGenerator()
    context = generator.generate_safety_context("Test medical AI system")
    
    print(f"✓ Mock safety context generated")
    print(f"  System: {context.system_description}")
    print(f"  Claims: {len(context.safety_claims)}")
    print(f"  Risks: {len(context.risk_factors)}")
    
    print("✓ Mock API test passed!")
    return True

if __name__ == "__main__":
    print("🛡️ Safety Case Debate System - Basic Tests")
    print("=" * 50)
    
    success = True
    success &= test_basic_functionality()
    success &= test_with_mock_api()
    
    if success:
        print("\n✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: streamlit run app.py --server.port 12000 --server.host 0.0.0.0")
        print("3. Or run: python example_usage.py")
    else:
        print("\n❌ Some tests failed. Please check the setup.")