import numpy as np
import matplotlib.pyplot as plt

# --- Love-OS v1.3 Parameters ---
gamma = 1.5
delta = 2.0
zeta  = 0.5
alpha_A = 2.0
theta_A = 0.6
s_A     = 10.0
beta_R  = 1.5

# Fixed Assumptions for this Cross-section
TC_norm = 0.9  # High Trust
C_info  = 1.0  # High Communication Capacity
N       = 0.1  # Low Noise

# --- Functions ---
def phi_A(A):
    # Sigmoid Amplification
    return (A ** alpha_A) / (1 + np.exp(-s_A * (A - theta_A)))

def potential_V(A, R):
    # V = Attraction(Well) + Repulsion(Wall) + Noise
    term_attraction = -gamma * phi_A(A) * C_info * TC_norm
    term_repulsion  = delta * (R ** beta_R)
    term_noise      = zeta * N
    return term_attraction + term_repulsion + term_noise

# --- Grid Generation ---
A_vals = np.linspace(0.01, 1.0, 100) # Awakening 0 to 100%
R_vals = np.linspace(0.01, 1.0, 100) # Resistance 0 to 100%
A_grid, R_grid = np.meshgrid(A_vals, R_vals)

V_grid = potential_V(A_grid, R_grid)

# --- Visualization ---
plt.figure(figsize=(10, 8))

# Contour Plot (Potential Landscape)
# Levels: Lower V is better (Stable)
cp = plt.contourf(A_grid, R_grid, V_grid, levels=20, cmap='coolwarm_r') # Reverse coolwarm: Blue=Low(Stable), Red=High(Unstable)
plt.colorbar(cp, label='Potential Energy V (Lower is More Stable)')

# Add Annotations
plt.axvline(x=0.6, color='white', linestyle='--', alpha=0.7, label='Phase Transition (A=0.6)')
plt.text(0.75, 0.1, 'Target Zone\n(Deep Well)', color='white', fontweight='bold', ha='center',
         bbox=dict(facecolor='blue', alpha=0.3))
plt.text(0.2, 0.8, 'Danger Zone\n(High R, Low A)', color='black', fontweight='bold', ha='center',
         bbox=dict(facecolor='red', alpha=0.3))

# Labels
plt.title('Love-OS v1.3 Stability Map: The "Well" of Love', fontsize=14)
plt.xlabel('Awakening Level (A)', fontsize=12)
plt.ylabel('Internal Resistance (R)', fontsize=12)
plt.legend(loc='upper right')
plt.grid(False)

# Invert Y axis to imply "Lower Resistance is falling down" or keep standard?
# Standard plot: R increases upwards. Target is Bottom-Right.

plt.tight_layout()
plt.show()
