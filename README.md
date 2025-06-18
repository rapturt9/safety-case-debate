# 🛡️ Prover-Estimator Debate Safety Case System

A comprehensive AI safety evaluation system using the prover-estimator debate framework from the UK AISI alignment team. This system creates and evaluates AI safety cases through structured debates between AI agents, providing probability estimates and automated diagram generation.

## 🎯 Overview

This system implements the prover-estimator debate protocol described in:

- [Prover-Estimator Debate: A New Scalable Oversight Protocol](https://www.alignmentforum.org/s/NdovveRcyfxgMoujf/p/8XHBaugB5S3r27MG9)
- [An alignment safety case sketch based on debate](https://www.alignmentforum.org/s/NdovveRcyfxgMoujf/p/iELyAqizJkizBQbfr)

### Key Features

- **Prover-Estimator Debate Protocol**: Implements the full debate framework with Alice (Prover), Bob (Estimator), and Judge agents
- **Safety Case Generation**: Automatically creates comprehensive safety cases for AI systems
- **Probability Estimates**: Provides calibrated probability estimates for safety claims
- **Interactive Visualizations**: Generates debate trees, argument structures, and safety overviews
- **Inspect AI Integration**: Built on the Inspect AI framework for robust evaluation
- **OpenRouter Support**: Uses OpenRouter for access to multiple LLM providers
- **Web Interface**: Streamlit-based interface for easy interaction

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prover (Alice)│    │Estimator (Bob)  │    │   Judge Agent   │
│                 │    │                 │    │                 │
│ • Breaks claims │    │ • Estimates     │    │ • Evaluates     │
│   into subclaims│    │   probabilities │    │   consistency   │
│ • Selects focus │    │ • Provides      │    │ • Assigns       │
│ • Predicts      │    │   reasoning     │    │   rewards       │
│   directions    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │                 │
                    │ • Manages rounds│
                    │ • Tracks rewards│
                    │ • Controls flow │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Safety Case     │
                    │ Generator       │
                    │                 │
                    │ • Creates context│
                    │ • Analyzes results│
                    │ • Estimates probs│
                    └─────────────────┘
```

## 🚀 Quick Start

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd safety-case-debate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

#### Web Interface (Recommended)

```bash
streamlit run app.py --server.port 15000 --server.host 0.0.0.0
```

Then open your browser to the provided URL.

#### Python API

```python
from src.debate.orchestrator import DebateOrchestrator
from src.safety_case.generator import SafetyCaseGenerator

# Initialize components
safety_generator = SafetyCaseGenerator()
orchestrator = DebateOrchestrator()

# Generate safety case
user_input = "An AI assistant for medical diagnosis"
safety_context = safety_generator.generate_safety_context(user_input)
debates = orchestrator.generate_safety_case_debate(safety_context)
analysis = safety_generator.analyze_debate_results(debates, safety_context)
```

#### Inspect AI Evaluation

```python
from src.inspect_eval import run_safety_case_evaluation

results = run_safety_case_evaluation(
    "An autonomous vehicle control system",
    model_name="openai/gpt-4o"
)
```

### Example Usage

Run the example script:

```bash
python example_usage.py
```

This will generate a complete safety case evaluation and save visualizations as HTML files.

## 📋 Safety Case Framework

The system evaluates four key claims based on the alignment forum framework:

1. **Training Equilibrium**: The training process has reached an approximate global equilibrium
2. **Error Bounds**: In equilibrium, the system makes mistakes in at most an ε'-fraction of cases
3. **Deployment Stability**: Error rate won't drift past ε during deployment with online training
4. **Acceptable Risk**: The system cannot cause unacceptable outcomes given error rate ε

### Key Assumptions

- **Exploration Guarantees**: Solution to exploration hacking
- **No Obfuscated Arguments**: Debate protocol avoids computationally intractable argument flaws
- **Good Human Input**: Reliable human judgment on relevant query distributions
- **Stability**: Arguments not sensitive to small probability variations

## 🎨 Visualizations

The system generates several types of diagrams:

- **Debate Trees**: Show the hierarchical structure of debates
- **Reward Progression**: Track cumulative rewards through debate rounds
- **Argument Structure**: Visualize claim decomposition with probability estimates
- **Safety Overview**: Comprehensive dashboard with confidence scores and risk assessment
- **Probability Heatmaps**: Compare estimates across multiple debates

## 🔧 Configuration

### Model Selection

Supports multiple LLM providers through OpenRouter:

- OpenAI (GPT-4, GPT-4-turbo, GPT-3.5-turbo)
- Anthropic (Claude-3-opus, Claude-3-sonnet, Claude-3-haiku)
- Other OpenRouter-supported models

### Debate Parameters

- **Reward Ratio**: Controls exponential reward scaling (default: 2.5)
- **Max Depth**: Maximum debate recursion depth (default: 5)
- **Model Temperature**: Controls response randomness (default: 0.7)

## 📊 Output Format

The system produces structured JSON output containing:

```json
{
  "safety_context": {
    "system_description": "...",
    "deployment_context": "...",
    "safety_claims": [...],
    "assumptions": [...],
    "risk_factors": [...],
    "mitigation_strategies": [...]
  },
  "debates": [...],
  "analysis": {
    "overall_assessment": "...",
    "confidence_score": 0.75,
    "claim_assessments": [...],
    "vulnerabilities": [...],
    "recommendations": [...]
  },
  "probabilities": {
    "claim_probabilities": {...},
    "overall_safety_probability": 0.78,
    "confidence_intervals": {...}
  }
}
```

## 🧪 Testing and Evaluation

### Running Tests

```bash
# Run basic functionality test
python -m pytest tests/

# Run example evaluation
python example_usage.py

# Run Inspect AI evaluation
python -c "from src.inspect_eval import run_safety_case_evaluation; run_safety_case_evaluation('Test system')"
```

### Evaluation Metrics

- **Debate Convergence**: Whether debates reach stable conclusions
- **Probability Calibration**: Accuracy of probability estimates
- **Argument Quality**: Logical consistency and evidence strength
- **Safety Coverage**: Comprehensiveness of risk assessment

## 🔒 Security and Privacy

- API keys are handled securely through environment variables
- No data is stored permanently unless explicitly saved
- All LLM calls go through OpenRouter's secure API
- Local processing for sensitive evaluations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest

# Run linting
flake8 src/
black src/
```

## 📚 References

- [UK AISI Alignment Team: Debate Sequence](https://www.alignmentforum.org/s/NdovveRcyfxgMoujf)
- [Prover-Estimator Debate Paper](https://arxiv.org/abs/2506.13609)
- [Safety Case Sketch Paper](https://arxiv.org/abs/2505.03989)
- [Inspect AI Documentation](https://inspect.ai-safety-institute.org.uk/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- UK AISI Alignment Team for the foundational research
- OpenRouter for LLM API access
- Inspect AI team for the evaluation framework
- The AI safety research community

---

**Note**: This is a research tool for AI safety evaluation. Results should be interpreted by qualified safety researchers and not used as the sole basis for deployment decisions.
