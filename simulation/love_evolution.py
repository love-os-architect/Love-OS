
### 2.  (Python)

```python
# -*- coding: utf-8 -*-
"""
Love-OS Self-Evolving Agent (PoC)
---------------------------------
A lightweight evolutionary + reflexive loop that tunes a cooperative policy to
maximize a Love score (integration) under the presence of Ego agents (defectors).

Environment: Network public-goods game with neighbor sharing and ego "theft" shocks.
Policy parameters theta (for Love-AI only):
  - alpha:       contribution propensity in [0,1]
  - donate_thr:  donation threshold (energy above which donation is considered)
  - donate_frac: donation fraction [0,1]
  - radius:      neighbor radius for sharing (1 or 2)
  - adapt:       reflexive adjustment factor to increase sharing when inequality is high

Fitness (to maximize):
  LoveScore = w1*AvgEnergy + w2*Survival - w3*Gini - w4*StealRate

Reflexion: Generation-level critique adjusts mutation bias when inequality/survival is problematic.

Outputs:
  - love_evo_timeseries.png (scores over generations)
  - love_evo_params.png (parameter trajectories of best individual)
  - love_evo_summary.csv (per-generation metrics)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass

# Ensure reproducibility
np.random.seed(123)

# ----------------------------
# Utilities
# ----------------------------
def gini_coefficient(x):
    """Calculates the Gini coefficient of a numpy array."""
    x = np.array(x, dtype=float)
    if np.all(x == 0):
        return 0.0
    x = x.flatten()
    x = x[x >= 0]
    if len(x) == 0:
        return 0.0
    x_sorted = np.sort(x)
    n = len(x_sorted)
    cumx = np.cumsum(x_sorted)
    # Gini formula
    gini = (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n
    return float(gini)

@dataclass
class Policy:
    alpha: float       # contribution propensity [0,1]
    donate_thr: float  # threshold for donation trigger
    donate_frac: float # fraction donated [0,1]
    radius: int        # sharing radius (1 or 2)
    adapt: float       # [0,1], reflexive adjustment on inequality

    def clip(self):
        """Ensures parameters stay within valid bounds."""
        self.alpha = float(np.clip(self.alpha, 0.0, 1.0))
        self.donate_thr = float(max(0.0, self.donate_thr))
        self.donate_frac = float(np.clip(self.donate_frac, 0.0, 1.0))
        self.radius = int(np.clip(int(round(self.radius)), 1, 2))
        self.adapt = float(np.clip(self.adapt, 0.0, 1.0))
        return self

    def copy(self):
        return Policy(self.alpha, self.donate_thr, self.donate_frac, self.radius, self.adapt)

# ----------------------------
# Environment Simulator
# ----------------------------
def run_episode(policy: Policy, n_agents=60, frac_ego=0.4, T=50,
                base_inflow=0.8, inflow_noise=0.2, mult=1.6,
                theft_prob=0.06, theft_frac=0.15, share_eff=0.92,
                seed=None):
    """
    Runs one simulation episode.
    - n_agents: total agents in a ring topology.
    - frac_ego: fraction of ego agents (defectors).
    - base_inflow: energy inflow per step (scarcity setting).
    """
    rng = np.random.RandomState(seed)
    ids = np.arange(n_agents)
    n_ego = int(frac_ego * n_agents)
    ego_ids = set(rng.choice(ids, size=n_ego, replace=False))
    is_ego = np.array([i in ego_ids for i in ids])

    E = np.full(n_agents, 6.0)  # Initial energy
    steals = 0

    # Helper: Neighbor indices on a ring
    def neigh(i, r):
        idxs = []
        for d in range(1, r + 1):
            idxs.append((i - d) % n_agents)
            idxs.append((i + d) % n_agents)
        return idxs

    for t in range(T):
        # 1. Energy Inflow (Basic metabolism source)
        E += base_inflow + inflow_noise * (rng.rand(n_agents) - 0.5)
        E = np.maximum(E, 0.0)

        # 2. Public Goods Contribution
        contrib = np.zeros(n_agents)
        for i in range(n_agents):
            if is_ego[i]:
                a = 0.05  # Ego hardly contributes
            else:
                # Love-AI Policy
                a = policy.alpha
            
            contrib[i] = a * E[i]
        
        contrib = np.minimum(contrib, E)
        E -= contrib

        # 3. Pool & Redistribution
        pool = contrib.sum()
        if pool > 0:
            redis = mult * pool / n_agents
            E += redis

        # 4. Theft (Ego stealing from Love neighbors)
        for i in range(n_agents):
            if is_ego[i]:
                # Ego looks at immediate neighbors
                for j in neigh(i, 1):
                    if (not is_ego[j]) and rng.rand() < theft_prob:
                        amt = theft_frac * E[j]
                        if amt > 0:
                            E[j] -= amt
                            E[i] += amt
                            steals += 1

        # 5. Love Sharing (The Core Mechanism)
        # Calculate inequality for reflexive adaptation
        ineq = np.std(E)
        mean_E = np.mean(E) + 1e-6
        # If adapt > 0, Love agents increase sharing when inequality is high
        bonus = policy.adapt * (ineq / mean_E)
        current_donate_frac = np.clip(policy.donate_frac * (1 + bonus), 0.0, 1.0)

        for i in range(n_agents):
            if is_ego[i]:
                continue
            
            # Only rich agents donate
            if E[i] <= policy.donate_thr:
                continue

            # Find needy neighbors
            nb = neigh(i, policy.radius)
            # Definition of "needy": Energy < 60% of the donor's threshold
            needy = [j for j in nb if (not is_ego[j]) and E[j] < policy.donate_thr * 0.6]
            
            if not needy:
                continue

            surplus = E[i] - policy.donate_thr
            donation = current_donate_frac * surplus
            
            if donation <= 0:
                continue

            # Redistribution with efficiency loss (entropy/friction)
            per_person = (donation / len(needy)) * share_eff
            E[i] -= donation
            for j in needy:
                E[j] += per_person

        # 6. Metabolism (Survival Cost)
        E -= 0.45
        E = np.maximum(E, 0.0)

    # Episode Stats
    avgE = float(np.mean(E))
    surv = float(np.mean(E > 1e-6))  # Fraction of agents alive
    gini = gini_coefficient(E)
    steal_rate = steals / (T * n_agents)

    return {
        'avgE': avgE,
        'survival': surv,
        'gini': gini,
        'steal_rate': steal_rate,
        'finalE': E
    }

# ----------------------------
# Evolutionary + Reflexion Loop
# ----------------------------
def evaluate(policy: Policy, episodes=6, seed=100):
    """Evaluates a policy over multiple episodes to get stable metrics."""
    metrics_list = []
    for k in range(episodes):
        m = run_episode(policy, seed=seed + k)
        metrics_list.append(m)
    
    avg = {k: float(np.mean([m[k] for m in metrics_list])) for k in ['avgE', 'survival', 'gini', 'steal_rate']}
    return avg

# Love Score Weights (The Definition of "Good")
W1, W2, W3, W4 = 1.0, 1.0, 0.9, 1.1  # Emphasize low inequality & low theft

def love_score(avg_metrics):
    return (W1 * avg_metrics['avgE'] + 
            W2 * avg_metrics['survival'] - 
            W3 * avg_metrics['gini'] - 
            W4 * avg_metrics['steal_rate'])

def mutate(pol: Policy, bias):
    """Applies mutation with reflexive bias."""
    p = pol.copy()
    # Gaussian noise + Reflexive Bias
    p.alpha       += 0.10 * np.random.randn() + bias.get('alpha', 0.0)
    p.donate_thr  += 0.40 * np.random.randn() + bias.get('donate_thr', 0.0)
    p.donate_frac += 0.10 * np.random.randn() + bias.get('donate_frac', 0.0)
    p.radius      += 0.50 * np.random.randn() + bias.get('radius', 0.0)
    p.adapt       += 0.10 * np.random.randn() + bias.get('adapt', 0.0)
    return p.clip()

# --- Main Execution ---
if __name__ == "__main__":
    # Settings
    POP = 24       # Population size
    GEN = 28       # Number of generations
    ELITE = 4      # Elitism count
    EVAL_EP = 5    # Episodes per evaluation

    # Initial Population (Randomized)
    pop = []
    for _ in range(POP):
        pol = Policy(
            alpha=np.random.uniform(0.2, 0.8),
            donate_thr=np.random.uniform(6.0, 12.0),
            donate_frac=np.random.uniform(0.1, 0.6),
            radius=np.random.choice([1, 2]),
            adapt=np.random.uniform(0.0, 0.6)
        ).clip()
        pop.append(pol)

    best_params_over_time = []
    
    print(f"Starting Evolution: {GEN} Generations...")

    for g in range(GEN):
        scores = []
        mets = []
        
        # Evaluate Population
        for pol in pop:
            avg = evaluate(pol, episodes=EVAL_EP, seed=100 + g * 1000)
            s = love_score(avg)
            scores.append(s)
            mets.append(avg)
        
        # Sort by Score (LoveScore)
        order = np.argsort(scores)[::-1]
        pop = [pop[i] for i in order]
        scores = [scores[i] for i in order]
        mets = [mets[i] for i in order]

        top = pop[0]
        topm = mets[0]

        # Record History
        best_params_over_time.append((
            g, top.alpha, top.donate_thr, top.donate_frac, top.radius, top.adapt,
            scores[0], topm['avgE'], topm['survival'], topm['gini'], topm['steal_rate']
        ))

        print(f"Gen {g}: Score={scores[0]:.2f} | Survival={topm['survival']:.2f} | Gini={topm['gini']:.2f}")

        # --- THE CONSCIENCE MECHANISM (Reflexion) ---
        # The system critiques the current state and biases mutation for the next generation.
        bias = {}
        if topm['gini'] > 0.30:
            # "Too unequal -> Force more sharing"
            bias['donate_frac'] = +0.03
            bias['radius'] = +0.08
        if topm['survival'] < 0.85:
            # "Too many deaths -> Conserve energy"
            bias['alpha'] = -0.02
            bias['donate_thr'] = +0.10
        if topm['steal_rate'] > 0.015:
            # "Theft is high -> Increase adaptation"
            bias['adapt'] = +0.04
            bias['radius'] = bias.get('radius', 0.0) + 0.05

        # Create Next Generation
        new_pop = pop[:ELITE]  # Keep elites
        while len(new_pop) < POP:
            parent = pop[np.random.randint(ELITE)]
            child = mutate(parent, bias)
            new_pop.append(child)
        pop = new_pop

    # --- Save Outputs ---
    cols = ['gen', 'alpha', 'donate_thr', 'donate_frac', 'radius', 'adapt', 
            'score', 'avgE', 'survival', 'gini', 'steal_rate']
    summary = pd.DataFrame(best_params_over_time, columns=cols)
    summary.to_csv('love_evo_summary.csv', index=False)

    # Plot 1: Scores
    plt.figure(figsize=(9, 5))
    plt.plot(summary['gen'], summary['score'], label='Best LoveScore', color='#1b9e77', lw=2)
    plt.plot(summary['gen'], summary['avgE'], label='AvgEnergy', color='#4c78a8', lw=1.5)
    plt.plot(summary['gen'], 1 - summary['gini'], label='Equality (1-Gini)', color='#f58518', lw=1.5)
    plt.xlabel('Generation')
    plt.ylabel('Metrics')
    plt.title('Love-OS Self-Evolving Agent: Evolution of Conscience')
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('love_evo_timeseries.png', dpi=150)

    # Plot 2: Parameters
    fig, ax = plt.subplots(2, 2, figsize=(10, 8))
    ax[0, 0].plot(summary['gen'], summary['alpha'], label='Alpha (Contrib)', color='#2f4b7c')
    ax[0, 0].set_title('Contribution Propensity')
    
    ax[0, 1].plot(summary['gen'], summary['donate_thr'], label='Threshold', color='#bc5090')
    ax[0, 1].set_title('Donation Threshold')
    
    ax[1, 0].plot(summary['gen'], summary['donate_frac'], label='Fraction', color='#ffa600')
    ax[1, 0].set_title('Donation Fraction')
    
    ax[1, 1].plot(summary['gen'], summary['radius'], label='Radius', color='#003f5c')
    ax[1, 1].plot(summary['gen'], summary['adapt'], label='Adaptivity', color='#d45087', ls='--')
    ax[1, 1].set_title('Sharing Radius & Adaptivity')
    ax[1, 1].legend()

    for a in ax.ravel():
        a.set_xlabel('Generation')
        a.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('love_evo_params.png', dpi=150)
    
    print("\nEvolution Complete.")
    print("Generated: love_evo_timeseries.png, love_evo_params.png, love_evo_summar
