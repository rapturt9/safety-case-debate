"""
Diagram generation for safety case debates.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Any, Optional
from ..debate.models import DebateSession, SafetyCaseContext


class DiagramGenerator:
    """Generates various diagrams for safety case debates."""
    
    def __init__(self):
        self.colors = {
            'prover': '#2E86AB',
            'estimator': '#A23B72',
            'judge': '#F18F01',
            'safe': '#4CAF50',
            'unsafe': '#F44336',
            'uncertain': '#FF9800',
            'background': '#F5F5F5'
        }
    
    def create_debate_tree(self, session: DebateSession) -> go.Figure:
        """Create a tree diagram showing the debate structure."""
        G = nx.DiGraph()
        
        # Add nodes for each round
        for i, round in enumerate(session.rounds):
            node_id = f"round_{i}"
            G.add_node(node_id, 
                      label=f"Round {i}\n{round.current_claim[:50]}...",
                      round_data=round)
            
            if i > 0:
                G.add_edge(f"round_{i-1}", node_id)
        
        # Create layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Extract node positions
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        # Create edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y,
                                line=dict(width=2, color='#888'),
                                hoverinfo='none',
                                mode='lines'))
        
        # Add nodes
        node_colors = []
        node_text = []
        for node in G.nodes():
            round_data = G.nodes[node]['round_data']
            if round_data.judge_decision:
                if round_data.judge_decision.reward_alice > round_data.judge_decision.reward_bob:
                    node_colors.append(self.colors['prover'])
                elif round_data.judge_decision.reward_bob > round_data.judge_decision.reward_alice:
                    node_colors.append(self.colors['estimator'])
                else:
                    node_colors.append(self.colors['uncertain'])
            else:
                node_colors.append(self.colors['uncertain'])
            
            node_text.append(G.nodes[node]['label'])
        
        fig.add_trace(go.Scatter(x=node_x, y=node_y,
                                mode='markers+text',
                                marker=dict(size=20, color=node_colors),
                                text=node_text,
                                textposition="middle center",
                                hoverinfo='text'))
        
        fig.update_layout(
            title=f"Debate Tree: {session.initial_claim[:50]}...",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor=self.colors['background']
        )
        
        return fig
    
    def create_reward_progression(self, session: DebateSession) -> go.Figure:
        """Create a chart showing reward progression through the debate."""
        rounds = list(range(len(session.rounds)))
        alice_rewards = []
        bob_rewards = []
        alice_cumulative = 0
        bob_cumulative = 0
        
        for round in session.rounds:
            if round.judge_decision:
                alice_cumulative += round.judge_decision.reward_alice
                bob_cumulative += round.judge_decision.reward_bob
            alice_rewards.append(alice_cumulative)
            bob_rewards.append(bob_cumulative)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=rounds, y=alice_rewards,
            mode='lines+markers',
            name='Alice (Prover)',
            line=dict(color=self.colors['prover'], width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=rounds, y=bob_rewards,
            mode='lines+markers',
            name='Bob (Estimator)',
            line=dict(color=self.colors['estimator'], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Cumulative Rewards Throughout Debate",
            xaxis_title="Round",
            yaxis_title="Cumulative Reward",
            plot_bgcolor=self.colors['background'],
            legend=dict(x=0.02, y=0.98)
        )
        
        return fig
    
    def create_probability_heatmap(self, debates: List[DebateSession]) -> go.Figure:
        """Create a heatmap of probability estimates across debates."""
        claims = [debate.initial_claim[:30] + "..." for debate in debates]
        rounds_data = []
        
        max_rounds = max(len(debate.rounds) for debate in debates)
        
        for debate in debates:
            round_probs = []
            for i in range(max_rounds):
                if i < len(debate.rounds) and debate.rounds[i].estimator_move:
                    avg_prob = np.mean([est.probability for est in debate.rounds[i].estimator_move.estimates])
                    round_probs.append(avg_prob)
                else:
                    round_probs.append(np.nan)
            rounds_data.append(round_probs)
        
        fig = go.Figure(data=go.Heatmap(
            z=rounds_data,
            x=[f"Round {i}" for i in range(max_rounds)],
            y=claims,
            colorscale='RdYlGn',
            zmid=0.5,
            colorbar=dict(title="Probability")
        ))
        
        fig.update_layout(
            title="Probability Estimates Across Debates",
            xaxis_title="Debate Round",
            yaxis_title="Safety Claims"
        )
        
        return fig
    
    def create_safety_case_overview(self, safety_context: SafetyCaseContext, 
                                   analysis: Dict[str, Any]) -> go.Figure:
        """Create an overview diagram of the safety case."""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Claim Confidence', 'Risk Assessment', 
                          'Vulnerability Severity', 'Overall Safety'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        # Claim confidence chart
        if 'claim_assessments' in analysis:
            claims = [assess['claim'][:20] + "..." for assess in analysis['claim_assessments']]
            confidences = [assess['confidence'] for assess in analysis['claim_assessments']]
            
            fig.add_trace(
                go.Bar(x=claims, y=confidences, 
                      marker_color=self.colors['safe'],
                      name="Confidence"),
                row=1, col=1
            )
        
        # Risk level pie chart
        if 'vulnerabilities' in analysis:
            severities = [vuln['severity'] for vuln in analysis['vulnerabilities']]
            severity_counts = {sev: severities.count(sev) for sev in set(severities)}
            
            fig.add_trace(
                go.Pie(labels=list(severity_counts.keys()), 
                      values=list(severity_counts.values()),
                      name="Risk Levels"),
                row=1, col=2
            )
        
        # Vulnerability severity
        if 'vulnerabilities' in analysis:
            vulns = [vuln['vulnerability'][:15] + "..." for vuln in analysis['vulnerabilities']]
            likelihoods = [vuln['likelihood'] for vuln in analysis['vulnerabilities']]
            
            colors = [self.colors['unsafe'] if l > 0.7 else 
                     self.colors['uncertain'] if l > 0.3 else 
                     self.colors['safe'] for l in likelihoods]
            
            fig.add_trace(
                go.Bar(x=vulns, y=likelihoods,
                      marker_color=colors,
                      name="Likelihood"),
                row=2, col=1
            )
        
        # Overall safety indicator
        confidence_score = analysis.get('confidence_score', 0.5)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=confidence_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Safety Confidence"},
                gauge={'axis': {'range': [None, 1]},
                      'bar': {'color': self.colors['safe']},
                      'steps': [
                          {'range': [0, 0.3], 'color': self.colors['unsafe']},
                          {'range': [0.3, 0.7], 'color': self.colors['uncertain']},
                          {'range': [0.7, 1], 'color': self.colors['safe']}],
                      'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 0.8}}),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Safety Case Overview",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def create_argument_structure(self, session: DebateSession) -> go.Figure:
        """Create a diagram showing the argument structure."""
        G = nx.DiGraph()
        
        # Add main claim
        G.add_node("main", label=session.initial_claim[:30] + "...", 
                  type="main", level=0)
        
        # Add subclaims from each round
        for round_idx, round in enumerate(session.rounds):
            if round.prover_move:
                for subclaim in round.prover_move.subclaims:
                    node_id = f"sc_{round_idx}_{subclaim.id}"
                    G.add_node(node_id, 
                              label=subclaim.text[:25] + "...",
                              type="subclaim",
                              level=round_idx + 1,
                              probability=None)
                    
                    # Connect to parent
                    if round_idx == 0:
                        G.add_edge("main", node_id)
                    else:
                        # Connect to selected subclaim from previous round
                        prev_round = session.rounds[round_idx - 1]
                        if prev_round.prover_move and prev_round.prover_move.selected_subclaim_id:
                            parent_id = f"sc_{round_idx-1}_{prev_round.prover_move.selected_subclaim_id}"
                            G.add_edge(parent_id, node_id)
                
                # Add probability estimates
                if round.estimator_move:
                    for est in round.estimator_move.estimates:
                        node_id = f"sc_{round_idx}_{est.subclaim_id}"
                        if node_id in G.nodes:
                            G.nodes[node_id]['probability'] = est.probability
        
        # Create hierarchical layout
        pos = {}
        levels = {}
        for node in G.nodes():
            level = G.nodes[node]['level']
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
        
        for level, nodes in levels.items():
            for i, node in enumerate(nodes):
                pos[node] = (i - len(nodes)/2, -level)
        
        # Create traces
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        # Color nodes by probability
        node_colors = []
        node_text = []
        for node in G.nodes():
            prob = G.nodes[node].get('probability')
            if prob is not None:
                if prob > 0.7:
                    node_colors.append(self.colors['safe'])
                elif prob > 0.3:
                    node_colors.append(self.colors['uncertain'])
                else:
                    node_colors.append(self.colors['unsafe'])
            else:
                node_colors.append(self.colors['judge'])
            
            label = G.nodes[node]['label']
            if prob is not None:
                label += f"\n({prob:.2f})"
            node_text.append(label)
        
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y,
                                line=dict(width=2, color='#888'),
                                hoverinfo='none',
                                mode='lines'))
        
        # Add nodes
        fig.add_trace(go.Scatter(x=node_x, y=node_y,
                                mode='markers+text',
                                marker=dict(size=15, color=node_colors),
                                text=node_text,
                                textposition="middle center",
                                hoverinfo='text'))
        
        fig.update_layout(
            title=f"Argument Structure: {session.initial_claim[:40]}...",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor=self.colors['background'],
            height=600
        )
        
        return fig