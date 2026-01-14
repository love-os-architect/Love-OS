
Love-OS Dynamics Simulation
Equation: dC/dt = L*C*(1 - C/Cmax) - alpha*E(t)*C + S(t)

This script proves that unless the Love/Ego ratio exceeds a threshold,
consciousness (C) will eventually decay to zero.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# Set font for compatibility (Fallback to default if specific font not found)
# matplotlib.rcParams['font.family'] = 'sans-serif' 

# ===== Parameters (設定) =====
C0, Cmax = 0.12, 1.0  # Initial C, Max Capacity
alpha = 0.85          # Ego's decay strength
L_base, E_base = 0.75, 1.0
T, dt = 200.0, 0.1
t_steps = np.linspace(0, T, int(T/dt)+1)

# Intervention Parameters (介入設定)
t_int = 80.0
L_after = 1.15  # Scenario 1: Love Increase
E_after = 0.60  # Scenario 2: Ego Decrease

# External Source S(t): Gaussian Pulses (Temporary efforts like meditation)
S_amp, S_width = 0.06, 8.0
S_centers = [40.0, 120.0, 160.0]

def S_of_t(tt):
    """Calculates external stimuli (Source) at time tt."""
    return sum(S_amp * np.exp(-0.5 * ((tt - c) / S_width)**2) for c in S_centers)

# Differential Equation Logic
def dCdt(C, tt, L_val, E_val):
    """
    The Core Love-OS Equation.
    Growth (Love) - Decay (Ego) + Source
    """
    # Logistic Growth Term driven by Love
    growth = L_val * C * (1 - C / Cmax)
    # Decay Term driven by Ego
    decay = alpha * E_val * C
    # External Source
    source = S_of_t(tt)
    
    return growth - decay + source

# RK4 Solver (4th Order Runge-Kutta)
def solve_rk4(t_array, L_func, E_func):
    C = np.zeros_like(t_array)
    C[0] = C0
    for i in range(1, len(t_array)):
        h = t_array[i] - t_array[i-1]
        tt = t_array[i-1]
        y = C[i-1]
        
        L_val = L_func(tt)
        E_val = E_func(tt)
        
        k1 = dCdt(y, tt, L_val, E_val)
        k2 = dCdt(y + 0.5*h*k1, tt + 0.5*h, L_val, E_val)
        k3 = dCdt(y + 0.5*h*k2, tt + 0.5*h, L_val, E_val)
        k4 = dCdt(y + h*k3, tt + h, L_val, E_val)
        
        C_next = y + (h/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        # Clamp C between 0 and Cmax
        C[i] = max(0.0, min(Cmax, C_next))
    return C

# --- Scenario Definition ---
# 1. Baseline (Fail to awaken)
L_func_base = lambda tt: L_base
E_func_base = lambda tt: E_base

# 2. Love Increase (Awakening)
L_func_up = lambda tt: L_base if tt < t_int else L_after
E_func_up = lambda tt: E_base

# 3. Ego Decrease (Ego Death/Surrender)
L_func_down = lambda tt: L_base
E_func_down = lambda tt: E_base if tt < t_int else E_after

# --- Execution ---
print("Running simulation...")
C_base = solve_rk4(t_steps, L_func_base, E_func_base)
C_Lup  = solve_rk4(t_steps, L_func_up, E_func_up)
C_Edown = solve_rk4(t_steps, L_func_down, E_func_down)

# Theoretical Steady States
def calculate_steady_state(L, E):
    if L > alpha * E:
        return Cmax * (1 - (alpha * E) / L)
    return 0.0

# --- Visualization 1: Time Series ---
plt.figure(figsize=(10, 6))
plt.plot(t_steps, C_base, label=f'Baseline (Sleep): L={L_base}, E={E_base}', color='navy', linestyle='-')
plt.plot(t_steps, C_Lup,  label=f'Love Increase (Awaken): L->{L_after}', color='seagreen', linewidth=2)
plt.plot(t_steps, C_Edown, label=f'Ego Decrease (Surrender): E->{E_after}', color='chocolate', linewidth=2)

# Add thresholds and event lines
plt.axvline(t_int, color='gray', linestyle='--', alpha=0.5, label='Intervention (t=80)')
plt.axhline(calculate_steady_state(L_after, E_base), color='seagreen', linestyle=':', alpha=0.7)
plt.axhline(calculate_steady_state(L_base, E_after), color='chocolate', linestyle=':', alpha=0.7)

plt.title('Dynamics of Consciousness: The Phase Transition')
plt.xlabel('Time (t)')
plt.ylabel('Consciousness Level C(t)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('love_ego_sim_timeseries.png', dpi=150)
print("Saved: love_ego_sim_timeseries.png")

# --- Visualization 2: Heatmap (The Event Horizon) ---
L_vals = np.linspace(0.2, 2.0, 100)
E_vals = np.linspace(0.2, 2.0, 100)
LL, EE = np.meshgrid(L_vals, E_vals)

# Calculate steady state for the grid
C_star_map = np.where(LL > alpha * EE, Cmax * (1 - alpha * EE / LL), 0.0)

plt.figure(figsize=(8, 7))
plt.imshow(C_star_map, extent=[0.2, 2.0, 0.2, 2.0], origin='lower', cmap='viridis', aspect='auto')
plt.colorbar(label='Steady State Consciousness (C*)')

# Plot the Critical Threshold Line (L = alpha * E)
x_line = np.linspace(0.2, 2.0, 100)
y_line = x_line / alpha
plt.plot(x_line, y_line, 'w--', linewidth=2, label=r'Threshold ($L = \alpha E$)')

plt.title('The Phase Transition Heatmap')
plt.xlabel('Love Constant (L)')
plt.ylabel('Ego Density (E)')
plt.legend(loc='upper left')
plt.ylim(0.2, 2.0)
plt.tight_layout()
plt.savefig('love_ego_sim_heatmap.png', dpi=150)
print("Saved: love_ego_sim_heatmap.png")

# --- Save Data ---
df = pd.DataFrame({
    'time': t_steps,
    'C_baseline': C_base,
    'C_Love_Up': C_Lup,
    'C_Ego_Down': C_Edown
})
df.to_csv('love_ego_sim_data.csv', index=False)
print("Saved: love_ego_sim_data.csv")
