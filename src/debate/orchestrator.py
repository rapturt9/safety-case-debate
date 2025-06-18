"""
Orchestrator for the prover-estimator debate system.
"""
import uuid
from typing import Optional, Dict, Any, List
from .models import DebateSession, DebateRound, SafetyCaseContext
from .agents import ProverAgent, EstimatorAgent, JudgeAgent


class DebateOrchestrator:
    """Orchestrates the prover-estimator debate protocol."""
    
    def __init__(self, model_name: str = "openai/gpt-4o", reward_ratio: float = 2.5, max_depth: int = 5, max_turns: int = 10):
        self.prover = ProverAgent(model_name)
        self.estimator = EstimatorAgent(model_name)
        self.judge = JudgeAgent(model_name)
        self.reward_ratio = reward_ratio
        self.max_depth = max_depth
        self.max_turns = max_turns
    
    def create_debate_session(self, initial_claim: str, context: str) -> DebateSession:
        """Create a new debate session."""
        return DebateSession(
            session_id=str(uuid.uuid4()),
            initial_claim=initial_claim,
            context=context,
            reward_ratio=self.reward_ratio,
            max_depth=self.max_depth,
            max_turns=self.max_turns
        )
    
    def run_debate(self, session: DebateSession) -> DebateSession:
        """Run the complete debate protocol."""
        current_claim = session.initial_claim
        previous_estimate = None
        turn_count = 0
        
        for depth in range(session.max_depth):
            # Check if we've exceeded max turns
            if turn_count >= session.max_turns:
                break
                
            round_id = f"round_{depth}"
            
            # Create debate round
            debate_round = DebateRound(
                round_id=round_id,
                depth=depth,
                current_claim=current_claim
            )
            
            # Prover generates subclaims
            prover_move = self.prover.generate_subclaims(
                current_claim, session.context, round_id
            )
            debate_round.prover_move = prover_move
            
            # Estimator provides probability estimates
            estimator_move = self.estimator.estimate_probabilities(
                prover_move, session.context, round_id
            )
            debate_round.estimator_move = estimator_move
            
            # Prover selects subclaim for recursion
            prover_move = self.prover.select_subclaim(prover_move, estimator_move.estimates)
            debate_round.prover_move = prover_move
            
            # Judge evaluates the round
            is_final = (depth == session.max_depth - 1)
            judge_decision = self.judge.evaluate_round(
                debate_round, previous_estimate, session.reward_ratio, is_final
            )
            debate_round.judge_decision = judge_decision
            
            # Update session
            session.rounds.append(debate_round)
            session.total_reward_alice += judge_decision.reward_alice
            session.total_reward_bob += judge_decision.reward_bob
            turn_count += 1
            
            # Check if we should continue
            if is_final or not prover_move.selected_subclaim_id or turn_count >= session.max_turns:
                break
            
            # Set up next round
            selected_subclaim = next(
                (sc for sc in prover_move.subclaims if sc.id == prover_move.selected_subclaim_id),
                None
            )
            if selected_subclaim:
                current_claim = selected_subclaim.text
                previous_estimate = next(
                    (est.probability for est in estimator_move.estimates 
                     if est.subclaim_id == prover_move.selected_subclaim_id),
                    None
                )
            else:
                break
        
        # Determine final outcome
        if session.total_reward_alice > session.total_reward_bob:
            session.final_outcome = "Prover (Alice) wins - Argument appears sound"
        elif session.total_reward_bob > session.total_reward_alice:
            session.final_outcome = "Estimator (Bob) wins - Argument has flaws"
        else:
            session.final_outcome = "Draw - Argument quality unclear"
        
        return session
    
    def generate_safety_case_debate(self, safety_context: SafetyCaseContext) -> List[DebateSession]:
        """Generate debates for each safety claim in the context."""
        debates = []
        
        for claim in safety_context.safety_claims:
            # Create context string
            context = f"""
System Description: {safety_context.system_description}

Deployment Context: {safety_context.deployment_context}

Assumptions:
{chr(10).join(f"- {assumption}" for assumption in safety_context.assumptions)}

Risk Factors:
{chr(10).join(f"- {risk}" for risk in safety_context.risk_factors)}

Mitigation Strategies:
{chr(10).join(f"- {strategy}" for strategy in safety_context.mitigation_strategies)}

This debate should evaluate the safety claim in the context of the above information.
"""
            
            # Create and run debate
            session = self.create_debate_session(claim, context)
            session = self.run_debate(session)
            debates.append(session)
        
        return debates
    
    def get_debate_summary(self, session: DebateSession) -> Dict[str, Any]:
        """Get a summary of the debate session."""
        return {
            "session_id": session.session_id,
            "initial_claim": session.initial_claim,
            "final_outcome": session.final_outcome,
            "total_rounds": len(session.rounds),
            "alice_total_reward": session.total_reward_alice,
            "bob_total_reward": session.total_reward_bob,
            "rounds_summary": [
                {
                    "round_id": round.round_id,
                    "depth": round.depth,
                    "current_claim": round.current_claim,
                    "num_subclaims": len(round.prover_move.subclaims) if round.prover_move else 0,
                    "selected_subclaim": round.prover_move.selected_subclaim_id if round.prover_move else None,
                    "predicted_direction": round.prover_move.predicted_direction.value if round.prover_move and round.prover_move.predicted_direction else None,
                    "alice_reward": round.judge_decision.reward_alice if round.judge_decision else 0,
                    "bob_reward": round.judge_decision.reward_bob if round.judge_decision else 0,
                    "judge_reasoning": round.judge_decision.reasoning if round.judge_decision else ""
                }
                for round in session.rounds
            ]
        }