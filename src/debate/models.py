"""
Data models for the prover-estimator debate system.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ClaimDirection(Enum):
    """Direction of claim correctness prediction."""
    OVERESTIMATED = "overestimated"
    UNDERESTIMATED = "underestimated"
    CORRECT = "correct"


class SubClaim(BaseModel):
    """A subclaim made by the prover."""
    id: str
    text: str
    evidence: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)


class ProbabilityEstimate(BaseModel):
    """Probability estimate for a subclaim."""
    subclaim_id: str
    probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class ProverMove(BaseModel):
    """A move by the prover (Alice)."""
    round_id: str
    main_claim: str
    subclaims: List[SubClaim]
    selected_subclaim_id: Optional[str] = None
    predicted_direction: Optional[ClaimDirection] = None
    reasoning: Optional[str] = None


class EstimatorMove(BaseModel):
    """A move by the estimator (Bob)."""
    round_id: str
    estimates: List[ProbabilityEstimate]
    overall_assessment: Optional[str] = None


class JudgeDecision(BaseModel):
    """A decision by the judge."""
    round_id: str
    consistency_check: bool
    direction_correct: bool
    final_truth_assessment: Optional[bool] = None
    reasoning: str
    reward_alice: float
    reward_bob: float


class DebateRound(BaseModel):
    """A single round of the debate."""
    round_id: str
    depth: int
    current_claim: str
    prover_move: Optional[ProverMove] = None
    estimator_move: Optional[EstimatorMove] = None
    judge_decision: Optional[JudgeDecision] = None


class DebateSession(BaseModel):
    """A complete debate session."""
    session_id: str
    initial_claim: str
    context: str
    rounds: List[DebateRound] = Field(default_factory=list)
    final_outcome: Optional[str] = None
    total_reward_alice: float = 0.0
    total_reward_bob: float = 0.0
    reward_ratio: float = 2.5
    max_depth: int = 5
    max_turns: int = 10  # Maximum number of debate turns


class SafetyCaseContext(BaseModel):
    """Context for generating a safety case."""
    system_description: str
    deployment_context: str
    safety_claims: List[str]
    assumptions: List[str]
    risk_factors: List[str]
    mitigation_strategies: List[str]