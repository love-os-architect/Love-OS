import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- Love-OS Parameters ---
g = 1.0         # Internal Gain (Love Source)
alpha = 1.0     # Saturation (Stability)
K = 0.4         # Base Coupling Strength (Field Permeability)
phi_c = 0.0     # Coupling Phase (Ideal alignment)

# Range for Simulation
# X-axis: Difference in nature (Detuning)
d_omega_range = np.linspace(0, 1.0, 50) 
# Y-axis: Ego Resistance (Surrender level)
R_A_range = np.linspace(0, 0.9, 50)  

# Result Grid (1 = Sync, 0 = Async)
sync_map = np.zeros((len(R_A_range), len(d_omega_range)))

def love_dynamics(t, y, wA, wB, RA, RB):
    # Unpack state (Real, Imag parts for A and B)
    psiA = y[0] + 1j*y[1]
    psiB = y[2] + 1j*y[3]
    
    # Coupled Stuart-Landau Equations
    # A controls only RA. B is fixed (RB=0.5).
    d_psiA = (g - RA)*psiA + 1j*wA*psiA - alpha*(np.abs(psiA)**2)*psiA + K*(psiB*np.exp(1j*phi_c) - psiA)
    d_psiB = (g - 0.5)*psiB + 1j*wB*psiB - alpha*(np.abs(psiB)**2)*psiB + K*(psiA*np.exp(1j*phi_c) - psiB)
    
    return [d_psiA.real, d_psiA.imag, d_psiB.real, d_psiB.imag]

print("Simulating Love-OS Synchronization Map...")

for i, RA in enumerate(R_A_range):
    for j, dw in enumerate(d_omega_range):
        wA = 1.0
        wB = 1.0 + dw # Partner is "different" by dw
        
        # Solve ODE
        sol = solve_ivp(love_dynamics, [0, 100], [0.1, 0, 0.1, 0], args=(wA, wB, RA, 0.5), t_eval=np.linspace(50, 100, 200))
        
        # Calculate Phase Difference
        phaseA = np.angle(sol.y[0] + 1j*sol.y[1])
        phaseB = np.angle(sol.y[2] + 1j*sol.y[3])
        phase_diff = np.unwrap(phaseA - phaseB)
        
        # Check Synchronization (Phase Locking)
        # If the slope of phase difference is near zero, they are synced.
        slope, _ = np.polyfit(sol.t, phase_diff, 1)
        
        if np.abs(slope) < 0.01: # Threshold for sync
            sync_map[i, j] = 1 # Sync Achieved

# Visualization
plt.figure(figsize=(8, 6))
# Invert Y axis so R=0 (Surrender) is at the top or emphasized as the goal
# But logically, R=0 means High Amplitude => High Effective Coupling.
# Usually Arnold tongue: Y=Coupling. Here Coupling depends on R.
# Let's plot typical image: X=Detuning, Y=Resistance (Low is better)
extent = [d_omega_range[0], d_omega_range[-1], R_A_range[0], R_A_range[-1]]
plt.imshow(sync_map, origin='lower', extent=extent, aspect='auto', cmap='Blues', alpha=0.8)

plt.xlabel('Incompatibility ($\Delta \omega$)\n[How different the partner is]', fontsize=12)
plt.ylabel('My Ego Resistance ($R_A$)\n[0 = Surrender, 1 = High Ego]', fontsize=12)
plt.title('The Physics of Unconditional Love\n(Arnold Tongue of Love-OS)', fontsize=14)
plt.axhline(y=0.9, color='red', linestyle='--', label='Critical Ego Boundary')
plt.text(0.1, 0.1, 'SYNC REGION\n(True Love)', color='blue', fontweight='bold', fontsize=14)
plt.text(0.6, 0.7, 'ASYNC REGION\n(Separation)', color='gray', fontweight='bold', fontsize=14)
plt.colorbar(label='Synchronization State')
plt.legend()
plt.tight_layout()
plt.show()
