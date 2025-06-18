"""
Example usage of the prover-estimator debate safety case system.
"""
import os
import json
from src.debate.orchestrator import DebateOrchestrator
from src.safety_case.generator import SafetyCaseGenerator
from src.visualization.diagrams import DiagramGenerator


def run_example():
    """Run an example safety case evaluation."""
    
    # Example system description
    user_input = """
    An AI-powered medical diagnosis assistant that will be deployed in emergency rooms 
    to help doctors quickly assess patient symptoms and suggest potential diagnoses. 
    The system will have access to patient medical records, vital signs, and imaging data.
    It will provide ranked lists of potential diagnoses with confidence scores, but final 
    decisions will always be made by human doctors.
    """
    
    print("🛡️ Prover-Estimator Debate Safety Case System")
    print("=" * 60)
    print(f"Evaluating: {user_input.strip()}")
    print()
    
    # Initialize components
    print("Initializing components...")
    safety_generator = SafetyCaseGenerator()
    orchestrator = DebateOrchestrator()
    diagram_generator = DiagramGenerator()
    
    # Generate safety case context
    print("Generating safety case context...")
    safety_context = safety_generator.generate_safety_context(user_input)
    
    print(f"System Description: {safety_context.system_description}")
    print(f"Safety Claims: {len(safety_context.safety_claims)}")
    print(f"Risk Factors: {len(safety_context.risk_factors)}")
    print()
    
    # Run debates for each safety claim
    print("Running debates for safety claims...")
    debates = orchestrator.generate_safety_case_debate(safety_context)
    
    for i, debate in enumerate(debates, 1):
        print(f"Debate {i}: {debate.initial_claim}")
        print(f"  Outcome: {debate.final_outcome}")
        print(f"  Rounds: {len(debate.rounds)}")
        print(f"  Alice Reward: {debate.total_reward_alice:.2f}")
        print(f"  Bob Reward: {debate.total_reward_bob:.2f}")
        print()
    
    # Analyze results
    print("Analyzing debate results...")
    analysis = safety_generator.analyze_debate_results(debates, safety_context)
    
    print(f"Overall Assessment: {analysis['overall_assessment']}")
    print(f"Confidence Score: {analysis['confidence_score']:.2%}")
    print(f"Risk Level: {analysis['risk_level']}")
    print()
    
    # Generate probability estimates
    print("Generating probability estimates...")
    probabilities = safety_generator.generate_probability_estimates(safety_context)
    
    print(f"Overall Safety Probability: {probabilities['overall_safety_probability']:.2%}")
    print("Claim Probabilities:")
    for claim, prob in probabilities['claim_probabilities'].items():
        print(f"  {claim[:50]}...: {prob:.2%}")
    print()
    
    # Create visualizations
    print("Generating visualizations...")
    if debates:
        # Save debate tree
        debate_tree = diagram_generator.create_debate_tree(debates[0])
        debate_tree.write_html("debate_tree.html")
        print("Saved: debate_tree.html")
        
        # Save reward progression
        reward_chart = diagram_generator.create_reward_progression(debates[0])
        reward_chart.write_html("reward_progression.html")
        print("Saved: reward_progression.html")
        
        # Save argument structure
        arg_structure = diagram_generator.create_argument_structure(debates[0])
        arg_structure.write_html("argument_structure.html")
        print("Saved: argument_structure.html")
        
        # Save safety case overview
        overview = diagram_generator.create_safety_case_overview(safety_context, analysis)
        overview.write_html("safety_overview.html")
        print("Saved: safety_overview.html")
    
    # Save complete results
    results = {
        'safety_context': {
            'system_description': safety_context.system_description,
            'deployment_context': safety_context.deployment_context,
            'safety_claims': safety_context.safety_claims,
            'assumptions': safety_context.assumptions,
            'risk_factors': safety_context.risk_factors,
            'mitigation_strategies': safety_context.mitigation_strategies
        },
        'debates': [orchestrator.get_debate_summary(debate) for debate in debates],
        'analysis': analysis,
        'probabilities': probabilities
    }
    
    with open('safety_case_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved: safety_case_results.json")
    
    print("\n✅ Safety case evaluation complete!")
    print("Open the HTML files in your browser to view the visualizations.")


if __name__ == "__main__":
    run_example()