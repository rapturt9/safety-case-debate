"""
Streamlit web interface for the prover-estimator debate safety case system.
"""
import streamlit as st
import json
import os
from typing import Dict, Any
import plotly.graph_objects as go

# Add src to path
import sys
sys.path.append('./src')

from src.debate.orchestrator import DebateOrchestrator
from src.safety_case.generator import SafetyCaseGenerator
from src.visualization.diagrams import DiagramGenerator


def initialize_session_state():
    """Initialize session state variables."""
    if 'safety_context' not in st.session_state:
        st.session_state.safety_context = None
    if 'debates' not in st.session_state:
        st.session_state.debates = []
    if 'analysis' not in st.session_state:
        st.session_state.analysis = None
    if 'probabilities' not in st.session_state:
        st.session_state.probabilities = None


def main():
    st.set_page_config(
        page_title="Safety Case Debate System",
        page_icon="🛡️",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("🛡️ Prover-Estimator Debate Safety Case System")
    st.markdown("""
    This system uses the prover-estimator debate framework from the UK AISI alignment team 
    to create and evaluate AI safety cases. Enter a description of an AI system to generate 
    a comprehensive safety analysis through structured debate.
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        model_name = st.selectbox(
            "Select Model",
            ["openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3-sonnet", "anthropic/claude-3-haiku"],
            index=0
        )
        
        reward_ratio = st.slider("Reward Ratio", 2.0, 5.0, 2.5, 0.1)
        max_depth = st.slider("Max Debate Depth", 3, 8, 5)
        max_turns = st.slider("Max Debate Turns", 5, 20, 10)
        
        st.markdown("---")
        st.markdown("### About the Framework")
        st.markdown("""
        Based on research from:
        - [Prover-Estimator Debate Protocol](https://www.alignmentforum.org/s/NdovveRcyfxgMoujf/p/8XHBaugB5S3r27MG9)
        - [Safety Case Sketch](https://www.alignmentforum.org/s/NdovveRcyfxgMoujf/p/iELyAqizJkizBQbfr)
        """)
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("System Description")
        user_input = st.text_area(
            "Describe the AI system you want to create a safety case for:",
            placeholder="e.g., An AI assistant for medical diagnosis in emergency rooms...",
            height=150
        )
        
        if st.button("Generate Safety Case", type="primary"):
            if user_input.strip():
                with st.spinner("Generating safety case..."):
                    try:
                        # Initialize components
                        safety_generator = SafetyCaseGenerator(model_name)
                        orchestrator = DebateOrchestrator(model_name, reward_ratio, max_depth, max_turns)
                        
                        # Generate safety context
                        st.session_state.safety_context = safety_generator.generate_safety_context(user_input)
                        
                        # Run debates
                        st.session_state.debates = orchestrator.generate_safety_case_debate(
                            st.session_state.safety_context
                        )
                        
                        # Analyze results
                        st.session_state.analysis = safety_generator.analyze_debate_results(
                            st.session_state.debates, st.session_state.safety_context
                        )
                        
                        # Generate probabilities
                        st.session_state.probabilities = safety_generator.generate_probability_estimates(
                            st.session_state.safety_context
                        )
                        
                        st.success("Safety case generated successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating safety case: {str(e)}")
            else:
                st.warning("Please enter a system description.")
    
    with col2:
        st.header("Quick Examples")
        examples = [
            "An AI assistant for medical diagnosis in hospitals",
            "An autonomous vehicle control system for urban environments",
            "A content moderation AI for social media platforms",
            "An AI system for automated financial trading",
            "A recommendation system for educational content",
            "An AI-powered hiring and recruitment system",
            "A predictive maintenance system for industrial equipment"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}"):
                st.session_state.user_input = example
                st.experimental_rerun()
    
    # Display results if available
    if st.session_state.safety_context:
        st.markdown("---")
        st.header("Safety Case Results")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Safety Context", 
            "⚖️ Debate Results", 
            "📊 Analysis", 
            "🎯 Probabilities",
            "📈 Visualizations"
        ])
        
        with tab1:
            st.subheader("System Description")
            st.write(st.session_state.safety_context.system_description)
            
            st.subheader("Deployment Context")
            st.write(st.session_state.safety_context.deployment_context)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Safety Claims")
                for i, claim in enumerate(st.session_state.safety_context.safety_claims, 1):
                    st.write(f"{i}. {claim}")
                
                st.subheader("Assumptions")
                for assumption in st.session_state.safety_context.assumptions:
                    st.write(f"• {assumption}")
            
            with col2:
                st.subheader("Risk Factors")
                for risk in st.session_state.safety_context.risk_factors:
                    st.write(f"• {risk}")
                
                st.subheader("Mitigation Strategies")
                for strategy in st.session_state.safety_context.mitigation_strategies:
                    st.write(f"• {strategy}")
        
        with tab2:
            if st.session_state.debates:
                for i, debate in enumerate(st.session_state.debates):
                    with st.expander(f"Debate {i+1}: {debate.initial_claim}"):
                        st.write(f"**Outcome:** {debate.final_outcome}")
                        st.write(f"**Alice (Prover) Total Reward:** {debate.total_reward_alice:.2f}")
                        st.write(f"**Bob (Estimator) Total Reward:** {debate.total_reward_bob:.2f}")
                        st.write(f"**Number of Rounds:** {len(debate.rounds)}")
                        
                        for round in debate.rounds:
                            st.write(f"**Round {round.depth}:** {round.current_claim}")
                            if round.prover_move:
                                st.write(f"- Subclaims: {len(round.prover_move.subclaims)}")
                                if round.prover_move.selected_subclaim_id:
                                    st.write(f"- Selected: {round.prover_move.selected_subclaim_id}")
                                    st.write(f"- Predicted: {round.prover_move.predicted_direction.value if round.prover_move.predicted_direction else 'None'}")
                            if round.judge_decision:
                                st.write(f"- Judge: {round.judge_decision.reasoning}")
        
        with tab3:
            if st.session_state.analysis:
                st.subheader("Overall Assessment")
                st.write(st.session_state.analysis.get('overall_assessment', 'No assessment available'))
                
                # Confidence score
                confidence = st.session_state.analysis.get('confidence_score', 0.5)
                st.metric("Overall Confidence", f"{confidence:.2%}")
                
                # Risk level
                risk_level = st.session_state.analysis.get('risk_level', 'unknown')
                risk_colors = {'low': 'green', 'medium': 'orange', 'high': 'red', 'unknown': 'gray'}
                st.markdown(f"**Risk Level:** :{risk_colors.get(risk_level, 'gray')}[{risk_level.upper()}]")
                
                # Claim assessments
                if 'claim_assessments' in st.session_state.analysis:
                    st.subheader("Claim Assessments")
                    for assessment in st.session_state.analysis['claim_assessments']:
                        with st.expander(f"Claim: {assessment['claim'][:50]}..."):
                            st.write(f"**Confidence:** {assessment['confidence']:.2%}")
                            st.write(f"**Evidence Strength:** {assessment['evidence_strength']}")
                            if assessment.get('key_concerns'):
                                st.write("**Key Concerns:**")
                                for concern in assessment['key_concerns']:
                                    st.write(f"• {concern}")
                
                # Vulnerabilities
                if 'vulnerabilities' in st.session_state.analysis:
                    st.subheader("Identified Vulnerabilities")
                    for vuln in st.session_state.analysis['vulnerabilities']:
                        severity_colors = {'high': 'red', 'medium': 'orange', 'low': 'green'}
                        st.markdown(f"**{vuln['vulnerability']}**")
                        st.markdown(f"Severity: :{severity_colors.get(vuln['severity'], 'gray')}[{vuln['severity'].upper()}]")
                        st.write(f"Likelihood: {vuln['likelihood']:.2%}")
                        st.write(f"Mitigation: {vuln['mitigation']}")
                        st.write("---")
                
                # Recommendations
                if 'recommendations' in st.session_state.analysis:
                    st.subheader("Recommendations")
                    for i, rec in enumerate(st.session_state.analysis['recommendations'], 1):
                        st.write(f"{i}. {rec}")
        
        with tab4:
            if st.session_state.probabilities:
                st.subheader("Probability Estimates")
                
                # Overall safety probability
                overall_prob = st.session_state.probabilities.get('overall_safety_probability', 0.5)
                st.metric("Overall Safety Probability", f"{overall_prob:.2%}")
                
                # Claim probabilities
                if 'claim_probabilities' in st.session_state.probabilities:
                    st.subheader("Individual Claim Probabilities")
                    for claim, prob in st.session_state.probabilities['claim_probabilities'].items():
                        st.write(f"**{claim}:** {prob:.2%}")
                
                # Confidence intervals
                if 'confidence_intervals' in st.session_state.probabilities:
                    st.subheader("Confidence Intervals")
                    for claim, interval in st.session_state.probabilities['confidence_intervals'].items():
                        st.write(f"**{claim}:** [{interval[0]:.2%}, {interval[1]:.2%}]")
                
                # Key uncertainties
                if 'key_uncertainties' in st.session_state.probabilities:
                    st.subheader("Key Uncertainties")
                    for uncertainty in st.session_state.probabilities['key_uncertainties']:
                        st.write(f"• {uncertainty}")
        
        with tab5:
            if st.session_state.debates:
                diagram_generator = DiagramGenerator()
                
                # Debate tree
                st.subheader("Debate Structure")
                debate_tree = diagram_generator.create_debate_tree(st.session_state.debates[0])
                st.plotly_chart(debate_tree, use_container_width=True)
                
                # Reward progression
                st.subheader("Reward Progression")
                reward_chart = diagram_generator.create_reward_progression(st.session_state.debates[0])
                st.plotly_chart(reward_chart, use_container_width=True)
                
                # Argument structure
                st.subheader("Argument Structure")
                arg_structure = diagram_generator.create_argument_structure(st.session_state.debates[0])
                st.plotly_chart(arg_structure, use_container_width=True)
                
                # Safety case overview
                if st.session_state.analysis:
                    st.subheader("Safety Case Overview")
                    overview = diagram_generator.create_safety_case_overview(
                        st.session_state.safety_context, st.session_state.analysis
                    )
                    st.plotly_chart(overview, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Prover-Estimator Debate Safety Case System** | 
    Built with [Inspect AI](https://inspect.ai-safety-institute.org.uk/) and [Streamlit](https://streamlit.io/) | 
    Based on research from the [UK AISI Alignment Team](https://www.alignmentforum.org/s/NdovveRcyfxgMoujf)
    """)


if __name__ == "__main__":
    main()