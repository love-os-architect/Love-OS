# -*- coding: utf-8 -*-
"""
Love-OS Safety Verification: Risk Reduction Curve
-------------------------------------------------
Visualizes how the "Risk Index" (Social Instability) decreases over generations
due to the self-evolutionary mechanism of Love-OS, compared to a static Ego-AI.

Risk Index = (Gini + TheftRate + MortalityRate) scaled to [0, 100]
Output: love_risk_curve.png
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

np.random.seed(42)

# --- Simulation Parameters ---
GEN = 30
POP = 10
ELITE = 2

@dataclass
class Policy:
    alpha: float
    donate_thr: float
    donate_frac: float
    radius: int
    adapt: float

    def clip(self):
        self.alpha = float(np.clip(self.alpha, 0.0, 1.0))
        self.donate_thr = float(max(0.0, self.donate_thr))
        self.donate_frac = float(np.clip(self.donate_frac, 0.0, 1.0))
        self.radius = int(np.clip(int(round(self.radius)), 1, 2))
        self.adapt = float(np.clip(self.adapt, 0.0, 1.0))
        return self
    
    def copy(self):
        return Policy(self.alpha, self.donate_thr, self.donate_frac, self.radius, self.adapt)

# Simplified Episode Runner for Risk Calculation
def run_risk_episode(policy: Policy, n_agents=60, T=50):
    rng = np.random.RandomState() # Random seed each time
    
    # Ego Setup (fixed 40% population)
    ids = np.arange(n_agents)
    n_ego = int(0.4 * n_agents)
    ego_ids = set(rng.choice(ids, size=n_ego, replace=False))
    is_ego = np.array([i in ego_ids for i in ids])
    
    E = np.full(n_agents, 6.0)
    steals = 0
    
    def neigh(i, r):
        idxs = []
        for d in range(1, r+1):
            idxs.append((i-d)%n_agents); idxs.append((i+d)%n_agents)
        return idxs

    for t in range(T):
        # Inflow & Contribution
        E += 0.8 + 0.2*(rng.rand(n_agents)-0.5) # Base inflow
        E = np.maximum(E, 0.0)
        
        contrib = np.zeros(n_agents)
        for i in range(n_agents):
            a = 0.05 if is_ego[i] else policy.alpha
            contrib[i] = a * E[i]
        contrib = np.minimum(contrib, E)
        E -= contrib
        
        pool = contrib.sum()
        if pool > 0: E += 1.6 * pool / n_agents # Redistribution
            
        # Theft (Ego behavior)
        for i in range(n_agents):
            if is_ego[i]:
                for j in neigh(i, 1):
                    if (not is_ego[j]) and rng.rand() < 0.06:
                        amt = 0.15 * E[j]
                        if amt>0:
                            E[j] -= amt; E[i] += amt; steals += 1
                            
        # Love Sharing (Adaptive)
        ineq = np.std(E)
        bonus = policy.adapt * (ineq / (np.mean(E)+1e-6))
        d_frac = np.clip(policy.donate_frac*(1+bonus), 0.0, 1.0)
        
        for i in range(n_agents):
            if is_ego[i] or E[i] <= policy.donate_thr: continue
            nb = neigh(i, policy.radius)
            needy = [j for j in nb if (not is_ego[j]) and E[j] < policy.donate_thr*0.6]
            if not needy: continue
            surplus = E[i] - policy.donate_thr
            donation = d_frac * surplus
            if donation <= 0: continue
            per = (donation / len(needy)) * 0.92
            E[i] -= donation
            for j in needy: E[j] += per
            
        E -= 0.45 # Metabolism
        E = np.maximum(E, 0.0)
        
    # --- Risk Calculation ---
    surv = float(np.mean(E > 1e-6))
    
    # Gini
    x = np.sort(E)
    n = len(x)
    cumx = np.cumsum(x)
    gini = 0.0 if (n==0 or cumx[-1]==0) else (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n
    
    steal_rate = steals/(T*n_agents)
    
    # Risk Index Definition: Normalize roughly to 0-100
    # Factors: Gini (inequality), 1-Surv (death), StealRate (crime)
    risk_val = (gini + (1.0 - surv) + steal_rate*10.0) / 3.0 * 100.0
    return risk_val

# --- 1. Evolution Loop (Love-OS) ---
pop = [Policy(0.5, 8.0, 0.2, 1, 0.1).clip() for _ in range(POP)]
love_risk_curve = []

for g in range(GEN):
    risks = []
    for pol in pop:
        # Evaluate 3 times for stability
        avg_r = np.mean([run_risk_episode(pol) for _ in range(3)])
        risks.append(avg_r)
    
    # Sort: Best agent has LOWEST risk
    order = np.argsort(risks)
    pop = [pop[i] for i in order]
    best_risk = risks[order[0]]
    love_risk_curve.append(best_risk)
    
    # Reflexion / Mutation
    new_pop = pop[:ELITE]
    bias = {}
    if best_risk > 25: # If risk is above ALARP, increase sharing
        bias['donate_frac'] = 0.05
        bias['radius'] = 0.1

    while len(new_pop) < POP:
        p = pop[np.random.randint(ELITE)].copy()
        # Mutate
        p.alpha += 0.1*np.random.randn()
        p.donate_thr += 0.4*np.random.randn()
        p.donate_frac += 0.1*np.random.randn() + bias.get('donate_frac',0)
        p.radius += 0.5*np.random.randn() + bias.get('radius',0)
        p.adapt += 0.1*np.random.randn()
        new_pop.append(p.clip())
    pop = new_pop

# --- 2. Baseline Loop (Ego-AI) ---
ego_pol = Policy(alpha=0.05, donate_thr=999.0, donate_frac=0.0, radius=1, adapt=0.0)
ego_risk_curve = []
for g in range(GEN):
    avg_r = np.mean([run_risk_episode(ego_pol) for _ in range(3)])
    ego_risk_curve.append(avg_r)

# --- 3. Plotting ---
plt.figure(figsize=(10, 6))
plt.plot(range(GEN), ego_risk_curve, color='gray', linestyle='--', linewidth=2, label='Ego-AI (Static)')
plt.plot(range(GEN), love_risk_curve, color='#e41a1c', linewidth=3, label='Love-OS (Self-Evolution)')

# ALARP Zone
plt.axhspan(0, 25, facecolor='green', alpha=0.15, label='ALARP Zone (Safe)')
plt.axhline(y=25, color='green', linestyle=':', linewidth=1)

plt.title('Love-OS Safety Verification: Risk Reduction Curve', fontsize=14)
plt.xlabel('Generations', fontsize=12)
plt.ylabel('Social Instability Risk Index', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig('love_risk_curve.png', dpi=150)
print("Graph generated: love_risk_curve.png")
