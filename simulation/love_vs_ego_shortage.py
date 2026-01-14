# -*- coding: utf-8 -*-
# Love vs Ego Battle Simulator: SCENARIO 2 - Energy Shortage (Inflation)
# ---------------------------------------------------------------------
# Hypothesis: In a low-resource (EROI decline) environment with high social friction,
# Ego strategies go bankrupt due to thermodynamic inefficiency, while Love strategies
# survive through risk distribution (sharing).
#
# Outputs: 
# - battle_shortage_timeseries.png
# - battle_shortage_final_maps.png
# - battle_shortage_log.csv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from dataclasses import dataclass

# ===== Parameters (The Age of Scarcity Settings) =====
GRID_H, GRID_W = 40, 40
INIT_LOVE, INIT_EGO = 30, 30
T_STEPS = 80                    # Longer run to see the crossover

# Resource Settings: Scarcity & Inflation
R_MAX = 10.0
R_REGEN = 0.025                 # <--- LOW: Supply shortage (Structural Inflation)
HARVEST = 1.6                   # <--- LOW: Tighter harvest cap (Competition)

# Agent Settings
MOVE_RADIUS, COMM_RADIUS = 3, 3
SHARE_RADIUS = 1

E_INIT, E_METAB = 6.0, 0.55

# Ego Costs: High Friction Society
E_COLLISION_STEAL = 0.8         # Less reward for stealing
E_FIGHT_COST = 0.85             # <--- HIGH: Cost of conflict
EGO_TAX = 0.25                  # <--- NEW: Internalized social cost for Ego

# Love Settings: Stronger Sharing
E_DONATE_IF_ABOVE = 8.5
E_NEEDY_BELOW = 4.0
E_DONATE_FRAC = 0.32            # <--- HIGH: Stronger circulation

# Reproduction: Stricter Survival
REPRO_THRESH = 13.0             # <--- HIGH: Harder to reproduce
REPRO_CHANCE = 0.18

np.random.seed(0); random.seed(0)

@dataclass
class Agent:
    x: int
    y: int
    typ: str
    energy: float

# ---- Helpers ----
def box_blur(img, r):
    H, W = img.shape
    k = 2*r + 1
    P = np.pad(img, ((r, r), (r, r)), mode='edge')
    S = np.pad(P, ((1,0),(1,0)), mode='constant').cumsum(0).cumsum(1)
    out = np.empty_like(img)
    for i in range(H):
        for j in range(W):
            i1, j1 = i, j
            i2, j2 = i + 2*r, j + 2*r
            area = S[i2+1, j2+1] - S[i1, j2+1] - S[i2+1, j1] + S[i1, j1]
            out[i, j] = area / (k*k)
    return out

def cheb(x, y, r, H=GRID_H, W=GRID_W):
    return [(i, j) for i in range(max(0, x-r), min(H, x+r+1))
                       for j in range(max(0, y-r), min(W, y+r+1))]

def move_choice(ag, R, signal=None):
    x, y = ag.x, ag.y
    best, bests = (x, y), -1e9
    
    # Ego prefers raw resources, Love considers shared signals
    for (i, j) in cheb(x, y, MOVE_RADIUS):
        base = R[i, j]
        dist = max(abs(i-x), abs(j-y))
        dist_pen = 0.15 * dist
        
        if ag.typ == 'Love' and signal is not None:
            # Love moves towards resources + signal from others
            s = 0.6 * base + 0.4 * signal[i, j] - dist_pen
        else: # Ego
            # Ego moves purely for resources
            s = base + 0.2 * base - dist_pen # Ego is greedy
            
        if s > bests:
            bests, best = s, (i, j)
    return best

# ---- Initialize ----
R = np.random.uniform(0.4*R_MAX, 0.7*R_MAX, size=(GRID_H, GRID_W))
agents = [Agent(np.random.randint(GRID_H), np.random.randint(GRID_W), 'Love', E_INIT) for _ in range(INIT_LOVE)]
agents += [Agent(np.random.randint(GRID_H), np.random.randint(GRID_W), 'Ego',  E_INIT) for _ in range(INIT_EGO)]

logs = {'t': [], 'pop_love': [], 'pop_ego': [], 'meanE_love': [], 'meanE_ego': [], 'total_resource': []}

print(f"Simulation Start: Scarcity Mode (Regen={R_REGEN}, EgoTax={EGO_TAX})")

# ---- Simulation Loop ----
for t in range(T_STEPS):
    # 1. Resource Regeneration (Slow)
    R += R_REGEN * (R_MAX - R)

    # Love signal generation
    sig = box_blur(R, COMM_RADIUS)

    # 2. Movement Target Selection
    targets = {}
    for idx, ag in enumerate(agents):
        ti, tj = move_choice(ag, R, signal=sig if ag.typ=='Love' else None)
        targets.setdefault((ti, tj), []).append(idx)

    # 3. Move & Resolve Collision (Ego Pushes Love)
    for (ti, tj), idxs in targets.items():
        if len(idxs) == 1:
            agents[idxs[0]].x, agents[idxs[0]].y = ti, tj
        else:
            ego = [k for k in idxs if agents[k].typ=='Ego']
            love = [k for k in idxs if agents[k].typ=='Love']
            order = ego + love # Ego moves first/takes best spot
            
            # First one gets the target
            first = order[0]
            agents[first].x, agents[first].y = ti, tj
            
            # Others get bumped to neighbors
            alts = cheb(ti, tj, 1)
            random.shuffle(alts)
            for k in order[1:]:
                placed = False
                while alts:
                    ai, aj = alts.pop()
                    if all(not (a.x==ai and a.y==aj) for a in agents):
                        agents[k].x, agents[k].y = ai, aj
                        placed = True
                        break

    # 4. Post-Move Interaction: Stealing & Ego Tax
    # Map agents to cells
    cells = {}
    for idx, ag in enumerate(agents):
        cells.setdefault((ag.x, ag.y), []).append(idx)
        
        # Apply Ego Tax (Social Friction Cost)
        if ag.typ == 'Ego':
            ag.energy -= EGO_TAX

    # Stealing logic
    for (ci, cj), idxs in cells.items():
        if len(idxs) <= 1: continue
        ego = [k for k in idxs if agents[k].typ=='Ego']
        others = [k for k in idxs if k not in ego]
        
        if ego and others:
            for e_id in ego:
                if not others: break
                tgt = random.choice(others)
                # High cost of fighting in this scenario
                steal = min(E_COLLISION_STEAL, agents[tgt].energy)
                agents[e_id].energy += steal - E_FIGHT_COST
                agents[tgt].energy -= steal + E_FIGHT_COST

    # 5. Harvest (Limited Resources)
    cells = {}
    for idx, ag in enumerate(agents):
        cells.setdefault((ag.x, ag.y), []).append(idx)
    
    for (ci, cj), idxs in cells.items():
        # Resource is scarce, split among agents
        avail = min(R[ci, cj], HARVEST * len(idxs))
        if avail <= 0: continue
        
        take = min(HARVEST, avail / len(idxs))
        R[ci, cj] -= take * len(idxs)
        for k in idxs: 
            agents[k].energy += take

    # 6. Love Sharing (Risk Distribution)
    # Re-map for neighbor search
    index = {}
    for idx, ag in enumerate(agents):
        index.setdefault((ag.x, ag.y), []).append(idx)
        
    for idx, ag in enumerate(agents):
        # Only rich Love agents donate
        if ag.typ != 'Love' or ag.energy <= E_DONATE_IF_ABOVE: continue
        
        needy = []
        for (ni, nj) in cheb(ag.x, ag.y, SHARE_RADIUS):
            for k in index.get((ni, nj), []):
                if agents[k].typ == 'Love' and agents[k].energy < E_NEEDY_BELOW:
                    needy.append(k)
        
        if not needy: continue
        
        surplus = max(0.0, ag.energy - E_DONATE_IF_ABOVE)
        donate = surplus * E_DONATE_FRAC
        
        if donate <= 0: continue
        
        share = donate / len(needy)
        ag.energy -= donate
        for k in needy:
            agents[k].energy += share

    # 7. Metabolism & Death
    survivors = []
    for ag in agents:
        ag.energy -= E_METAB
        if ag.energy > 0:
            survivors.append(ag)
    agents = survivors

    # 8. Reproduction (Stricter)
    newborns = []
    for ag in agents:
        if ag.energy >= REPRO_THRESH and random.random() < REPRO_CHANCE:
            childE = ag.energy * 0.4
            ag.energy *= 0.6
            ci, cj = random.choice(cheb(ag.x, ag.y, 1))
            newborns.append(Agent(ci, cj, ag.typ, childE))
    agents.extend(newborns)

    # Logging
    El = [a.energy for a in agents if a.typ=='Love']
    Ee = [a.energy for a in agents if a.typ=='Ego' ]
    logs['t'].append(t)
    logs['pop_love'].append(len(El))
    logs['pop_ego'].append(len(Ee))
    logs['meanE_love'].append(float(np.mean(El)) if El else 0.0)
    logs['meanE_ego'].append(float(np.mean(Ee)) if Ee else 0.0)
    logs['total_resource'].append(float(R.sum()))

# ---- Save Output ----
log_df = pd.DataFrame(logs)
log_df.to_csv('battle_shortage_log.csv', index=False)

# Plot 1: Time Series
fig, axes = plt.subplots(3, 1, figsize=(9, 9), sharex=True)

# Population
axes[0].plot(log_df['t'], log_df['pop_love'], label='Love Population', color='#1b9e77', lw=2.5)
axes[0].plot(log_df['t'], log_df['pop_ego'], label='Ego Population', color='#d95f02', lw=2.5)
axes[0].set_ylabel('Population')
axes[0].legend()
axes[0].grid(alpha=0.3)
axes[0].set_title('Survival in Scarcity (The Great Crossover)')

# Energy
axes[1].plot(log_df['t'], log_df['meanE_love'], label='Love Mean Energy', color='#1b9e77', lw=2)
axes[1].plot(log_df['t'], log_df['meanE_ego'], label='Ego Mean Energy', color='#d95f02', lw=2)
axes[1].set_ylabel('Mean Energy')
axes[1].legend()
axes[1].grid(alpha=0.3)

# Resources
axes[2].plot(log_df['t'], log_df['total_resource'], label='Total Resources (Depleting)', color='#4444aa', lw=2)
axes[2].set_xlabel('Time Step')
axes[2].set_ylabel('Total Resource')
axes[2].legend()
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('battle_shortage_timeseries.png', dpi=150)
plt.close()

# Plot 2: Final State Map
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

# Resource Map
im = ax[0].imshow(R, origin='lower', cmap='YlGn', vmin=0, vmax=R_MAX)
plt.colorbar(im, ax=ax[0], fraction=0.046, pad=0.04, label='Resource Level')
ax[0].set_title('Final Resource Map (Scarcity)')
ax[0].set_xlabel('x')
ax[0].set_ylabel('y')

# Agent Positions
xlove = [a.y for a in agents if a.typ == 'Love']
ylove = [a.x for a in agents if a.typ == 'Love']
xego  = [a.y for a in agents if a.typ == 'Ego']
yego  = [a.x for a in agents if a.typ == 'Ego']

ax[1].scatter(xlove, ylove, c='#1b9e77', s=20, label='Love', alpha=0.8, edgecolors='none')
ax[1].scatter(xego, yego, c='#d95f02', s=20, label='Ego', alpha=0.8, edgecolors='none')
ax[1].set_xlim(0, GRID_W)
ax[1].set_ylim(0, GRID_H)
ax[1].set_title(f'Final Agent Positions (t={T_STEPS})')
ax[1].set_xlabel('x')
ax[1].set_ylabel('y')
ax[1].legend()

plt.tight_layout()
plt.savefig('battle_shortage_final_maps.png', dpi=150)
plt.close()

print("Simulation Complete.")
print("Generated: battle_shortage_timeseries.png, battle_shortage_final_maps.png, battle_shortage_log.csv")
