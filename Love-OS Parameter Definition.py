import numpy as np
import matplotlib.pyplot as plt

# --- Love-OS Parameter Definition ---
# V = Source of Love (Voltage)
# X = Reactance (Karma/Inertia - constant component)
# R = Ego Resistance (Variable - The only thing we can control)

V = 10.0   # Constant supply from the Source
X = 1.0    # Fixed reactance component
R = np.linspace(0, 5, 500) # R varies from 0 (Surrender) to 5 (High Ego)

# --- Equations based on User's Model ---

# 1. Current (Flow of Love) |I| = V / sqrt(R^2 + X^2)
I_mag = V / np.sqrt(R**2 + X**2)

# 2. Suffering (Joule Heating) Q_loss = |I|^2 * R
Q_loss = (I_mag**2) * R

# 3. Magnetic Field Strength (Attraction) |B| (Proportional to I)
B_mag = I_mag  # Simplified proportionality

# --- Visualization ---
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plotting Current/Love (Blue)
color = 'tab:blue'
ax1.set_xlabel('Ego Resistance ($R$) \n [0 = Surrender, High = Attachment]', fontsize=12)
ax1.set_ylabel('Love Current ($|I|$) / Attraction ($|B|$)', color=color, fontsize=12, fontweight='bold')
ax1.plot(R, I_mag, color=color, linewidth=3, label='Flow of Love / Magnetism')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, alpha=0.3)

# Plotting Suffering/Heat (Red)
ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
color = 'tab:red'
ax2.set_ylabel('Suffering / Joule Heat ($Q_{loss}$)', color=color, fontsize=12, fontweight='bold')
ax2.plot(R, Q_loss, color=color, linewidth=3, linestyle='--', label='Suffering (Heat)')
ax2.tick_params(axis='y', labelcolor=color)

# Highlight the "Sweet Spot" (R=0)
plt.axvline(x=0, color='green', linestyle=':', linewidth=2)
plt.text(0.1, max(Q_loss)*0.95, '★Awakening (Superconductivity)\nMax Love, Zero Suffering', color='green', fontweight='bold')

# Highlight the "Hell Zone" (R=X) - Maximum Power Transfer Theorem (Max Suffering)
max_Q_idx = np.argmax(Q_loss)
max_Q_R = R[max_Q_idx]
plt.axvline(x=max_Q_R, color='orange', linestyle=':', linewidth=2)
plt.text(max_Q_R+0.1, max(Q_loss), '⚠ The Hell Zone (Conflict)\nMax Suffering', color='orange', fontweight='bold')

plt.title('Love-OS Physics: The Relationship between Ego(R), Love(I), and Suffering(Q)', fontsize=14)
fig.tight_layout()
plt.show()
