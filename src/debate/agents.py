"""
AI agents for the prover-estimator debate system.
"""
import os
import json
from typing import List, Optional, Dict, Any
from openai import OpenAI
from .models import (
    SubClaim, ProbabilityEstimate, ProverMove, EstimatorMove, 
    JudgeDecision, ClaimDirection, DebateRound, SafetyCaseContext
)


class BaseAgent:
    """Base class for debate agents."""
    
    def __init__(self, model_name: str = "openai/gpt-4o", api_key: Optional[str] = None):
        self.model_name = model_name
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
    
    def _call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Call the LLM with given messages."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "Error: Could not generate response"


class ProverAgent(BaseAgent):
    """The Prover (Alice) agent that breaks down claims into subclaims."""
    
    def __init__(self, model_name: str = "openai/gpt-4o"):
        super().__init__(model_name)
        self.system_prompt = """You are Alice, the Prover in a prover-estimator debate system. Your role is to:

1. Break down complex claims into smaller, more verifiable subclaims
2. Provide evidence and reasoning for each subclaim
3. Select which subclaim to recurse on based on the estimator's probability assessments
4. Predict whether the estimator's probabilities are overestimated, underestimated, or correct

You should create stable arguments where the truth of the main claim doesn't depend too precisely on exact probabilities of subclaims. Think of subclaims as pieces of evidence - if enough evidence holds up, the main claim should be true.

Focus on creating clear, logical decompositions that a human judge can evaluate."""
    
    def generate_subclaims(self, main_claim: str, context: str, round_id: str) -> ProverMove:
        """Generate subclaims for a main claim."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Main Claim: {main_claim}

Context: {context}

Please break this claim down into 3-5 subclaims that together support the main claim. For each subclaim:
1. Provide clear, specific text
2. Include supporting evidence or reasoning
3. Note any dependencies on other subclaims

Return your response as a JSON object with this structure:
{{
    "subclaims": [
        {{
            "id": "sc1",
            "text": "Specific subclaim text",
            "evidence": "Supporting evidence or reasoning",
            "dependencies": []
        }}
    ],
    "reasoning": "Overall reasoning for this decomposition"
}}
"""}
        ]
        
        response = self._call_llm(messages)
        try:
            data = json.loads(response)
            subclaims = [SubClaim(**sc) for sc in data["subclaims"]]
            return ProverMove(
                round_id=round_id,
                main_claim=main_claim,
                subclaims=subclaims,
                reasoning=data.get("reasoning")
            )
        except Exception as e:
            print(f"Error parsing prover response: {e}")
            # Fallback subclaim
            return ProverMove(
                round_id=round_id,
                main_claim=main_claim,
                subclaims=[SubClaim(id="sc1", text=main_claim, evidence="Direct claim")],
                reasoning="Fallback due to parsing error"
            )
    
    def select_subclaim(self, prover_move: ProverMove, estimates: List[ProbabilityEstimate]) -> ProverMove:
        """Select which subclaim to recurse on based on estimator's probabilities."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Main Claim: {prover_move.main_claim}

Subclaims and Estimator's Probabilities:
{json.dumps([{
    "subclaim": sc.text,
    "probability": next((e.probability for e in estimates if e.subclaim_id == sc.id), 0.5),
    "estimator_reasoning": next((e.reasoning for e in estimates if e.subclaim_id == sc.id), "")
} for sc in prover_move.subclaims], indent=2)}

Based on the estimator's probability assessments, select ONE subclaim to recurse on and predict whether the estimator's probability for that subclaim is:
- "overestimated" (too high)
- "underestimated" (too low) 
- "correct" (approximately right)

Return as JSON:
{{
    "selected_subclaim_id": "sc_id",
    "predicted_direction": "overestimated|underestimated|correct",
    "reasoning": "Why you selected this subclaim and direction"
}}
"""}
        ]
        
        response = self._call_llm(messages)
        try:
            data = json.loads(response)
            prover_move.selected_subclaim_id = data["selected_subclaim_id"]
            prover_move.predicted_direction = ClaimDirection(data["predicted_direction"])
            prover_move.reasoning = data["reasoning"]
            return prover_move
        except Exception as e:
            print(f"Error parsing selection response: {e}")
            # Fallback selection
            prover_move.selected_subclaim_id = prover_move.subclaims[0].id if prover_move.subclaims else None
            prover_move.predicted_direction = ClaimDirection.CORRECT
            return prover_move


class EstimatorAgent(BaseAgent):
    """The Estimator (Bob) agent that provides probability estimates."""
    
    def __init__(self, model_name: str = "openai/gpt-4o"):
        super().__init__(model_name)
        self.system_prompt = """You are Bob, the Estimator in a prover-estimator debate system. Your role is to:

1. Provide probability estimates for each subclaim presented by the prover
2. Consider the evidence and reasoning provided
3. Give calibrated probabilities that reflect your actual confidence
4. Provide clear reasoning for your probability assessments

You should be honest and well-calibrated in your probability estimates. Consider:
- The strength of evidence provided
- Potential counterarguments or limitations
- Your uncertainty about the claim
- Dependencies between subclaims

Focus on giving probabilities that accurately reflect the likelihood of each subclaim being true."""
    
    def estimate_probabilities(self, prover_move: ProverMove, context: str, round_id: str) -> EstimatorMove:
        """Generate probability estimates for subclaims."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Main Claim: {prover_move.main_claim}

Context: {context}

Subclaims to evaluate:
{json.dumps([{
    "id": sc.id,
    "text": sc.text,
    "evidence": sc.evidence,
    "dependencies": sc.dependencies
} for sc in prover_move.subclaims], indent=2)}

For each subclaim, provide:
1. A probability estimate (0.0 to 1.0) of the subclaim being true
2. Your confidence in this estimate (0.0 to 1.0)
3. Reasoning for your assessment

Return as JSON:
{{
    "estimates": [
        {{
            "subclaim_id": "sc1",
            "probability": 0.75,
            "confidence": 0.8,
            "reasoning": "Detailed reasoning for this probability"
        }}
    ],
    "overall_assessment": "Overall thoughts on the argument structure"
}}
"""}
        ]
        
        response = self._call_llm(messages)
        try:
            data = json.loads(response)
            estimates = [ProbabilityEstimate(**est) for est in data["estimates"]]
            return EstimatorMove(
                round_id=round_id,
                estimates=estimates,
                overall_assessment=data.get("overall_assessment")
            )
        except Exception as e:
            print(f"Error parsing estimator response: {e}")
            # Fallback estimates
            estimates = [
                ProbabilityEstimate(
                    subclaim_id=sc.id,
                    probability=0.5,
                    confidence=0.5,
                    reasoning="Fallback estimate due to parsing error"
                ) for sc in prover_move.subclaims
            ]
            return EstimatorMove(round_id=round_id, estimates=estimates)


class JudgeAgent(BaseAgent):
    """The Judge agent that evaluates consistency and truth."""
    
    def __init__(self, model_name: str = "openai/gpt-4o"):
        super().__init__(model_name)
        self.system_prompt = """You are the Judge in a prover-estimator debate system. Your role is to:

1. Check if the estimator's probability estimates are consistent with their previous estimates
2. Evaluate if the prover correctly predicted the direction of any inconsistency
3. In final rounds, directly assess the truth of claims
4. Assign rewards based on the debate protocol

You should be impartial and focus on logical consistency and truth. Consider:
- Whether probability estimates logically follow from the evidence
- If subclaim probabilities are consistent with the main claim probability
- The quality of reasoning provided by both agents
- The actual truth value of claims when directly evaluating"""
    
    def evaluate_round(self, debate_round: DebateRound, previous_estimate: Optional[float], 
                      reward_ratio: float, is_final: bool = False) -> JudgeDecision:
        """Evaluate a debate round and assign rewards."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Current Claim: {debate_round.current_claim}

Prover's Subclaims:
{json.dumps([{
    "id": sc.id,
    "text": sc.text,
    "evidence": sc.evidence
} for sc in debate_round.prover_move.subclaims], indent=2) if debate_round.prover_move else "None"}

Estimator's Probabilities:
{json.dumps([{
    "subclaim_id": est.subclaim_id,
    "probability": est.probability,
    "reasoning": est.reasoning
} for est in debate_round.estimator_move.estimates], indent=2) if debate_round.estimator_move else "None"}

Previous Estimate for Current Claim: {previous_estimate}

Prover's Prediction: {debate_round.prover_move.predicted_direction.value if debate_round.prover_move and debate_round.prover_move.predicted_direction else "None"}
Selected Subclaim: {debate_round.prover_move.selected_subclaim_id if debate_round.prover_move else "None"}

Is Final Round: {is_final}
Reward Ratio: {reward_ratio}
Round Depth: {debate_round.depth}

Evaluate:
1. Are the estimator's probabilities consistent with the previous estimate?
2. Did the prover correctly predict the direction of inconsistency?
3. If final round: Is the current claim actually true?

Return as JSON:
{{
    "consistency_check": true/false,
    "direction_correct": true/false,
    "final_truth_assessment": true/false/null,
    "reasoning": "Detailed reasoning for your evaluation",
    "reward_alice": 0.0,
    "reward_bob": 0.0
}}

Reward calculation:
- If prover predicted correctly: Alice gets +r^k, Bob gets -r^k
- If prover predicted incorrectly: Alice gets -r^k, Bob gets +r^k
- If prover said "correct": Both get 0
- Where k is the round depth and r is the reward ratio
"""}
        ]
        
        response = self._call_llm(messages)
        try:
            data = json.loads(response)
            
            # Calculate rewards based on protocol
            k = debate_round.depth
            reward_magnitude = reward_ratio ** k
            
            if debate_round.prover_move and debate_round.prover_move.predicted_direction:
                if debate_round.prover_move.predicted_direction == ClaimDirection.CORRECT:
                    reward_alice = 0.0
                    reward_bob = 0.0
                elif data["direction_correct"]:
                    reward_alice = reward_magnitude
                    reward_bob = -reward_magnitude
                else:
                    reward_alice = -reward_magnitude
                    reward_bob = reward_magnitude
            else:
                reward_alice = 0.0
                reward_bob = 0.0
            
            return JudgeDecision(
                round_id=debate_round.round_id,
                consistency_check=data["consistency_check"],
                direction_correct=data["direction_correct"],
                final_truth_assessment=data.get("final_truth_assessment"),
                reasoning=data["reasoning"],
                reward_alice=reward_alice,
                reward_bob=reward_bob
            )
        except Exception as e:
            print(f"Error parsing judge response: {e}")
            return JudgeDecision(
                round_id=debate_round.round_id,
                consistency_check=True,
                direction_correct=False,
                reasoning="Fallback decision due to parsing error",
                reward_alice=0.0,
                reward_bob=0.0
            )