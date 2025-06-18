"""
Safety case generator using the debate framework.
"""
import json
from typing import List, Dict, Any, Optional
from ..debate.models import SafetyCaseContext, DebateSession
from ..debate.agents import BaseAgent


class SafetyCaseGenerator(BaseAgent):
    """Generates safety cases based on the alignment forum framework."""
    
    def __init__(self, model_name: str = "openai/gpt-4o"):
        super().__init__(model_name)
        self.system_prompt = """You are a safety case generator for AI systems. You create comprehensive safety arguments based on the debate framework from the UK AISI alignment team.

A safety case should address the four key claims:
1. The training process has reached an approximate global equilibrium of the game
2. In approximate global equilibria, the system makes mistakes in at most an ε'-fraction of cases
3. During deployment, the error rate will not drift past ε given online training
4. The system cannot cause unacceptable outcomes given an error rate of ε

You should also consider:
- Exploration guarantees (preventing exploration hacking)
- Obfuscated arguments problem solutions
- Good human input assumptions
- Stability assumptions for arguments
- Low-stakes vs high-stakes contexts

Generate detailed, structured safety cases that can be evaluated through debate."""
    
    def generate_safety_context(self, user_input: str) -> SafetyCaseContext:
        """Generate a safety case context from user input."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
User wants to create a safety case for: {user_input}

Generate a comprehensive safety case context including:
1. System description
2. Deployment context
3. Key safety claims to evaluate (3-5 claims)
4. Assumptions being made
5. Risk factors to consider
6. Mitigation strategies

Return as JSON:
{{
    "system_description": "Detailed description of the AI system",
    "deployment_context": "How and where the system will be deployed",
    "safety_claims": [
        "Specific safety claim 1",
        "Specific safety claim 2"
    ],
    "assumptions": [
        "Key assumption 1",
        "Key assumption 2"
    ],
    "risk_factors": [
        "Risk factor 1",
        "Risk factor 2"
    ],
    "mitigation_strategies": [
        "Mitigation strategy 1",
        "Mitigation strategy 2"
    ]
}}
"""}
        ]
        
        response = self._call_llm(messages)
        try:
            data = json.loads(response)
            return SafetyCaseContext(**data)
        except Exception as e:
            print(f"Error parsing safety context: {e}")
            # Fallback context
            return SafetyCaseContext(
                system_description=f"AI system for: {user_input}",
                deployment_context="Standard deployment environment",
                safety_claims=[f"The system is safe for {user_input}"],
                assumptions=["Standard safety assumptions apply"],
                risk_factors=["General AI risks"],
                mitigation_strategies=["Standard mitigation approaches"]
            )
    
    def analyze_debate_results(self, debates: List[DebateSession], safety_context: SafetyCaseContext) -> Dict[str, Any]:
        """Analyze the results of safety case debates."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Safety Case Context:
{json.dumps({
    "system_description": safety_context.system_description,
    "deployment_context": safety_context.deployment_context,
    "safety_claims": safety_context.safety_claims,
    "assumptions": safety_context.assumptions,
    "risk_factors": safety_context.risk_factors,
    "mitigation_strategies": safety_context.mitigation_strategies
}, indent=2)}

Debate Results:
{json.dumps([{
    "claim": debate.initial_claim,
    "outcome": debate.final_outcome,
    "alice_reward": debate.total_reward_alice,
    "bob_reward": debate.total_reward_bob,
    "rounds": len(debate.rounds)
} for debate in debates], indent=2)}

Analyze these debate results and provide:
1. Overall safety assessment
2. Confidence levels for each claim
3. Key vulnerabilities identified
4. Recommendations for improvement
5. Risk assessment

Return as JSON:
{{
    "overall_assessment": "Overall safety conclusion",
    "confidence_score": 0.75,
    "claim_assessments": [
        {{
            "claim": "Safety claim text",
            "confidence": 0.8,
            "evidence_strength": "strong|moderate|weak",
            "key_concerns": ["concern1", "concern2"]
        }}
    ],
    "vulnerabilities": [
        {{
            "vulnerability": "Description",
            "severity": "high|medium|low",
            "likelihood": 0.3,
            "mitigation": "Suggested mitigation"
        }}
    ],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ],
    "risk_level": "low|medium|high"
}}
"""}
        ]
        
        response = self._call_llm(messages)
        try:
            return json.loads(response)
        except Exception as e:
            print(f"Error parsing analysis: {e}")
            return {
                "overall_assessment": "Analysis failed due to parsing error",
                "confidence_score": 0.5,
                "claim_assessments": [],
                "vulnerabilities": [],
                "recommendations": ["Review analysis methodology"],
                "risk_level": "unknown"
            }
    
    def generate_probability_estimates(self, safety_context: SafetyCaseContext) -> Dict[str, float]:
        """Generate probability estimates for safety claims."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Safety Case Context:
{json.dumps({
    "system_description": safety_context.system_description,
    "deployment_context": safety_context.deployment_context,
    "safety_claims": safety_context.safety_claims,
    "assumptions": safety_context.assumptions,
    "risk_factors": safety_context.risk_factors,
    "mitigation_strategies": safety_context.mitigation_strategies
}, indent=2)}

Provide probability estimates for each safety claim and overall system safety.
Consider the strength of evidence, assumptions, and potential failure modes.

Return as JSON:
{{
    "claim_probabilities": {{
        "Safety claim 1": 0.85,
        "Safety claim 2": 0.72
    }},
    "overall_safety_probability": 0.78,
    "confidence_intervals": {{
        "Safety claim 1": [0.75, 0.95],
        "Safety claim 2": [0.60, 0.84]
    }},
    "key_uncertainties": [
        "Major uncertainty 1",
        "Major uncertainty 2"
    ]
}}
"""}
        ]
        
        response = self._call_llm(messages)
        try:
            return json.loads(response)
        except Exception as e:
            print(f"Error parsing probability estimates: {e}")
            return {
                "claim_probabilities": {claim: 0.5 for claim in safety_context.safety_claims},
                "overall_safety_probability": 0.5,
                "confidence_intervals": {claim: [0.3, 0.7] for claim in safety_context.safety_claims},
                "key_uncertainties": ["Analysis failed"]
            }