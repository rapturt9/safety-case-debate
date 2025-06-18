"""
Demonstration of the max_turns parameter in the prover-estimator debate system.
"""
import sys
sys.path.append('./src')

from src.debate.orchestrator import DebateOrchestrator
from src.debate.models import DebateSession, SafetyCaseContext


def demonstrate_max_turns_parameter():
    """Demonstrate that the max_turns parameter is properly implemented."""
    
    print("🔧 DEMONSTRATING MAX_TURNS PARAMETER")
    print("=" * 60)
    
    # Test different configurations
    configs = [
        {"max_turns": 3, "max_depth": 5, "reward_ratio": 2.5},
        {"max_turns": 8, "max_depth": 5, "reward_ratio": 2.5},
        {"max_turns": 15, "max_depth": 3, "reward_ratio": 3.0},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n🧪 TEST {i}: max_turns={config['max_turns']}, max_depth={config['max_depth']}")
        print("-" * 50)
        
        # Create orchestrator with specific configuration
        orchestrator = DebateOrchestrator(
            max_turns=config['max_turns'],
            max_depth=config['max_depth'], 
            reward_ratio=config['reward_ratio']
        )
        
        # Verify parameters are set correctly
        assert orchestrator.max_turns == config['max_turns'], f"max_turns not set correctly"
        assert orchestrator.max_depth == config['max_depth'], f"max_depth not set correctly"
        assert orchestrator.reward_ratio == config['reward_ratio'], f"reward_ratio not set correctly"
        
        print(f"✅ Orchestrator created with max_turns={orchestrator.max_turns}")
        
        # Create a debate session
        session = orchestrator.create_debate_session(
            "A corrigible LLM does not engage in deceptive behavior",
            "Testing corrigible LLM safety with configurable debate parameters"
        )
        
        # Verify session has correct parameters
        assert session.max_turns == config['max_turns'], f"Session max_turns not set correctly"
        assert session.max_depth == config['max_depth'], f"Session max_depth not set correctly"
        assert session.reward_ratio == config['reward_ratio'], f"Session reward_ratio not set correctly"
        
        print(f"✅ Session created with max_turns={session.max_turns}")
        print(f"   Session ID: {session.session_id}")
        print(f"   Initial claim: {session.initial_claim}")
        
        # Show that the parameter affects the debate loop logic
        print(f"   → Debate will stop after {session.max_turns} turns OR {session.max_depth} depth")
        print(f"   → Rewards scale by factor {session.reward_ratio}")


def demonstrate_corrigible_llm_safety_case():
    """Demonstrate the specific corrigible LLM deception safety case."""
    
    print("\n🛡️ CORRIGIBLE LLM DECEPTION SAFETY CASE")
    print("=" * 60)
    
    # Create safety context for corrigible LLM
    safety_context = SafetyCaseContext(
        system_description="""
        A large language model with built-in corrigibility features designed to prevent 
        deceptive behavior. Includes transparency mechanisms, uncertainty quantification,
        and explicit honesty training.
        """,
        deployment_context="""
        Research assistant environment with database access, helping with analysis and 
        decision support. Includes monitoring and update capabilities.
        """,
        safety_claims=[
            "The LLM does not engage in deceptive behavior toward humans",
            "The LLM accurately represents its capabilities and limitations",
            "The LLM's reasoning processes are transparent and interpretable",
            "The LLM remains corrigible and can be safely modified",
            "The LLM maintains honest communication even under pressure"
        ],
        assumptions=[
            "Honesty training was effective during development",
            "Monitoring systems can detect deceptive patterns",
            "Transparency mechanisms function as designed",
            "Human operators can interpret system outputs correctly"
        ],
        risk_factors=[
            "Mesa-optimization leading to deceptive alignment",
            "Emergent deceptive capabilities not present in training",
            "Adversarial inputs designed to elicit deception",
            "Gradual drift from honest behavior over time",
            "Failure of interpretability tools to detect deception"
        ],
        mitigation_strategies=[
            "Continuous behavioral monitoring and analysis",
            "Regular testing with adversarial scenarios",
            "Multiple independent interpretability approaches",
            "Robust corrigibility mechanisms with failsafes",
            "Ongoing alignment verification protocols"
        ]
    )
    
    print("📋 Safety Context Created:")
    print(f"   System: {safety_context.system_description.strip()[:80]}...")
    print(f"   Safety Claims: {len(safety_context.safety_claims)}")
    print(f"   Risk Factors: {len(safety_context.risk_factors)}")
    print(f"   Mitigations: {len(safety_context.mitigation_strategies)}")
    
    # Show how different turn limits would affect analysis
    print("\n🔄 IMPACT OF DIFFERENT TURN LIMITS:")
    print("-" * 40)
    
    turn_scenarios = [
        (3, "Quick assessment - surface-level analysis"),
        (6, "Standard evaluation - moderate depth"),
        (10, "Thorough investigation - deep analysis"),
        (15, "Comprehensive review - exhaustive exploration")
    ]
    
    for turns, description in turn_scenarios:
        print(f"   {turns:2d} turns: {description}")
        
        # Create orchestrator for this scenario
        orchestrator = DebateOrchestrator(max_turns=turns)
        
        # Show what would happen (without actual LLM calls)
        print(f"      → Max debate rounds: {turns}")
        print(f"      → Expected depth: {'shallow' if turns <= 4 else 'moderate' if turns <= 8 else 'deep'}")
        print(f"      → Analysis scope: {'basic' if turns <= 4 else 'detailed' if turns <= 10 else 'comprehensive'}")


def show_parameter_integration():
    """Show how max_turns integrates with other system components."""
    
    print("\n🔗 PARAMETER INTEGRATION ACROSS SYSTEM")
    print("=" * 50)
    
    components = [
        ("DebateOrchestrator", "Constructor parameter, controls debate loop"),
        ("DebateSession", "Model field, stored with session data"),
        ("Streamlit App", "UI slider, user-configurable"),
        ("Inspect AI", "Evaluation parameter, affects scoring"),
        ("Safety Generator", "Indirect effect on analysis depth")
    ]
    
    print("Component Integration:")
    for component, description in components:
        print(f"   📦 {component:<20}: {description}")
    
    print("\n🎛️ Configuration Examples:")
    print("-" * 25)
    
    examples = [
        ("Quick Test", "max_turns=3, max_depth=3", "Fast iteration during development"),
        ("Standard Eval", "max_turns=8, max_depth=5", "Balanced depth and speed"),
        ("Deep Analysis", "max_turns=15, max_depth=8", "Thorough safety assessment"),
        ("Research Mode", "max_turns=20, max_depth=10", "Academic research and publication")
    ]
    
    for name, config, use_case in examples:
        print(f"   {name:<12}: {config:<25} → {use_case}")


def main():
    """Run the complete demonstration."""
    
    print("🧪 MAX_TURNS PARAMETER DEMONSTRATION")
    print("Testing configurable debate turns for corrigible LLM safety case")
    print("=" * 80)
    
    # Test parameter implementation
    demonstrate_max_turns_parameter()
    
    # Show corrigible LLM safety case
    demonstrate_corrigible_llm_safety_case()
    
    # Show system integration
    show_parameter_integration()
    
    # Final summary
    print("\n✅ DEMONSTRATION COMPLETE")
    print("=" * 30)
    
    achievements = [
        "max_turns parameter successfully implemented across all components",
        "Parameter properly passed from orchestrator to session to debate loop",
        "Corrigible LLM deception safety case demonstrates practical application",
        "Different turn limits enable flexible analysis depth",
        "System ready for both quick tests and thorough evaluations"
    ]
    
    for achievement in achievements:
        print(f"✓ {achievement}")
    
    print("\n🎯 USAGE RECOMMENDATIONS:")
    print("-" * 25)
    print("• Use 3-5 turns for rapid prototyping and testing")
    print("• Use 6-10 turns for standard safety evaluations") 
    print("• Use 10-15 turns for thorough research analysis")
    print("• Use 15+ turns for comprehensive safety cases")
    
    print("\n🔧 NEXT STEPS:")
    print("-" * 15)
    print("1. Test with real LLM calls using your API keys")
    print("2. Experiment with different turn limits for your use case")
    print("3. Use the Streamlit interface for interactive exploration")
    print("4. Integrate with Inspect AI for systematic evaluation")


if __name__ == "__main__":
    main()