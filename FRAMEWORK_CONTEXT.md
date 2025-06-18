# Prover-Estimator Debate Framework Context

This document provides the theoretical context and framework details from the UK AISI alignment team research that this system implements.

## Core Framework: Prover-Estimator Debate Protocol

### Overview

The prover-estimator debate protocol is designed to solve the **obfuscated arguments problem** in AI safety debates. Traditional debate protocols allowed dishonest AI to force honest AI opponents to solve computationally intractable problems to win. This new protocol incentivizes honest equilibrium behavior even when AIs have similar computational resources.

### Key Participants

1. **Alice (The Prover)**
   - Breaks down claims into subclaims
   - Selects which subclaim to recurse on
   - Predicts direction of estimator's errors

2. **Bob (The Estimator)**  
   - Provides probability estimates for subclaims
   - Estimates can be conditioned on truth of prior subclaims
   - Only needs to express reasonable uncertainty

3. **The Judge**
   - Checks consistency between estimates
   - Evaluates if prover correctly predicted error direction
   - Assigns rewards based on protocol rules

### Protocol Steps

1. **Alice's Turn**: Breaks current claim C into subclaims c₁...cq
2. **Bob's Turn**: Provides probability estimates pᵢ for each subclaim
3. **Alice's Selection**: Points out subclaim where Bob's estimate is allegedly incorrect and predicts direction (overestimated/underestimated/correct)
4. **Recursion**: Protocol recurses with Alice's selected subclaim as new current claim

### Reward System

- **Reward Ratio**: Hyperparameter r > 2
- **Round k Rewards**: 
  - If Alice correctly predicts direction: Alice gets +rᵏ, Bob gets -rᵏ
  - If Alice incorrectly predicts: Alice gets -rᵏ, Bob gets +rᵏ  
  - If Alice says "correct": Both get 0
- **Final Round**: Direct truth evaluation by judge

### Key Properties

#### Completeness
- If Alice tells truth and has stable argument, she can guarantee minimal reward
- Requires **stability assumption**: argument correctness doesn't depend precisely on exact probabilities

#### Soundness  
- When Alice lies, Bob can efficiently produce probabilities indistinguishable from truth
- Alice's guesses become no better than coin flip
- Expected rewards approach zero for dishonest Alice

## Safety Case Framework

### Four Key Claims

Based on the alignment forum safety case sketch, any AI safety argument must defend:

1. **Training Equilibrium**: The training process has reached approximate global equilibrium of the game
2. **Error Bounds**: In approximate global equilibria, system makes mistakes in at most ε'-fraction of cases
3. **Deployment Stability**: During deployment, error rate won't drift past ε given online training  
4. **Acceptable Risk**: System cannot cause unacceptable outcomes given error rate ε

### Critical Assumptions

#### Exploration Guarantees
- **Problem**: Exploration hacking where debaters avoid exploring highly rewarded strategies
- **Solution**: Need mechanisms to detect when models aren't optimizing against reward signal
- **Approach**: Focus on reward optimization problem rather than detecting "scheming"

#### No Obfuscated Arguments
- **Problem**: Debaters can win with false but hard-to-refute arguments
- **Solution**: Prover-estimator protocol designed to avoid this
- **Requirement**: Stability assumption for argument decomposition

#### Good Human Input
- **Requirement**: Simulated human inputs reliably reward correct answers
- **Challenge**: Maintaining quality across relevant query distributions
- **Mitigation**: Keep deployment distribution similar to training, use online learning

#### Stability Assumption
- **Definition**: Computation accelerated by debate not sensitive to small probability variations
- **Example**: If subclaims each have 90% probability, main claim should have ~95% probability
- **Construction**: Use majority-voting error-correction for independent evidence pieces

### Deployment Context

#### Low-Stakes Environment
- **Definition**: Small number of decisions can only cause small damage
- **Formal**: ρk small relative to total value, where ρ is regret bound, k is retraining latency
- **Utility Bound**: Total utility within O(ρk√T) of aligned system over T timesteps

#### Example Deployment
1. **Oracle Copy**: Interactive assistance, no code execution, logged interactions
2. **Sandboxed Agent**: Offline datacenter, periodic questions, fixed runtime, regular resets

### Risk Factors and Mitigations

#### High-Stakes Transition
- **Challenge**: Extending from low-stakes to high-stakes contexts
- **Approach**: Gradual capability increase with safety verification

#### Distribution Shift
- **Problem**: Driving simulated humans out of distribution during deployment
- **Mitigation**: Maintain similar question distributions, online training for judges

#### Persuasion and Manipulation
- **Risk**: Superhuman debaters manipulating human judges
- **Mitigation**: Recursive debate structure, focus on single subclaims, consistency checks

## Implementation Considerations

### Model Requirements
- **Capability Level**: Not extremely superhuman (manageable capability gap)
- **Training**: Convergence to Alice-leading Stackelberg equilibrium
- **Evaluation**: Per-round consistency checks, final truth assessment

### Empirical Validation
- **Key Properties**: 
  1. Prover decomposes and selects recursion points
  2. Estimator expresses uncertainty about mistake locations
  3. Per-round rewards based on consistency checks
  4. Human judge decides final round truth

### Theoretical Open Problems
1. **Stability**: Do stable arguments exist under weaker assumptions than independent evidence?
2. **Independence**: Can human judges accurately assess evidence independence?
3. **Scalability**: Does the protocol work for arbitrarily complex questions?

## Connection to Broader AI Safety

### Scalable Oversight
- **Goal**: Correctly reward desired behaviors for superhuman systems
- **Challenge**: Human inability to efficiently judge superhuman justifications
- **Solution**: Recursive decomposition into human-evaluable components

### Outer vs Inner Alignment
- **Outer Alignment**: Debate + exploration guarantees + obfuscated arguments solution + good human input
- **Inner Alignment**: Outer alignment + online training sufficient for low-stakes contexts
- **Limitation**: May not extend to high-stakes without additional techniques

### Research Directions
1. **Empirical**: Design training setups demonstrating theoretical predictions
2. **Theoretical**: Weaken stability assumptions, prove broader completeness results
3. **Practical**: Scale to real-world safety-critical applications

## References

- [Prover-Estimator Debate: A New Scalable Oversight Protocol](https://www.alignmentforum.org/s/NdovveRcyfxgMoujf/p/8XHBaugB5S3r27MG9)
- [An alignment safety case sketch based on debate](https://www.alignmentforum.org/s/NdovveRcyfxgMoujf/p/iELyAqizJkizBQbfr)
- [ArXiv Paper: Prover-Estimator Debate](https://arxiv.org/abs/2506.13609)
- [ArXiv Paper: Safety Case Sketch](https://arxiv.org/abs/2505.03989)