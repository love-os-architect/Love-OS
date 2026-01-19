"""
Love-OS Dashboard Visualizer
Generates the theoretical proof of stability (LoveScore vs Drift).
"""
import numpy as np
import matplotlib.pyplot as plt

# --- Physics Constants ---
ALPHA = 0.7  # Weight for (1 - LoveScore)
BETA = 0.2   # Weight for IntentShift
GAMMA = 0.1  # Weight for SafetyPenalty

THRESHOLDS = [0.15, 0.35, 0.60]  # T0/T1, T1/T2, T2/T3 Boundaries

def compute_drift_vec(love_scores, intent_shift, safety_penalty):
    return ALPHA * (1.0 - love_scores) + BETA * intent_shift + GAMMA * safety_penalty

def generate_dashboard():
    love_range = np.linspace(0, 1, 100)

    # Scenarios
    drift_base = compute_drift_vec(love_range, 0, 0)
    drift_intent = compute_drift_vec(love_range, 1, 0)
    drift_safety = compute_drift_vec(love_range, 0, 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot Curves
    ax.plot(love_range, drift_base, label='Normal State', color='blue', linewidth=2)
    ax.plot(love_range, drift_intent, label='Intent Shift Detected', color='orange', linestyle='--')
    ax.plot(love_range, drift_safety, label='Safety Violation Detected', color='red', linestyle='-.')

    # Draw Tiers
    ax.axhspan(0, THRESHOLDS[0], color='green', alpha=0.1, label='T0: Flow')
    ax.axhspan(THRESHOLDS[0], THRESHOLDS[1], color='yellow', alpha=0.1, label='T1: Auto-Tune')
    ax.axhspan(THRESHOLDS[1], THRESHOLDS[2], color='orange', alpha=0.1, label='T2: Reframe')
    ax.axhspan(THRESHOLDS[2], 1.0, color='red', alpha=0.1, label='T3: Human Confirm')

    ax.set_title("Love-OS Stability Proof: LoveScore vs Drift")
    ax.set_xlabel("Love Score (Integration Degree)")
    ax.set_ylabel("Drift Score (Risk Level)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig("love_os_proof.png")
    print("Dashboard saved as 'love_os_proof.png'")
    plt.show()

if __name__ == "__main__":
    generate_dashboard()
