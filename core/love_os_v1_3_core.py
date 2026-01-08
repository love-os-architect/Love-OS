import numpy as np
from scipy.stats import beta, entropy
from typing import List, Dict, Tuple

class LoveConfig:
    """System Configuration Parameters (Hyperparameters)"""
    def __init__(self):
        # Weighting factors for Potential Function V
        self.gamma = 1.5   # Gain for Information Capacity
        self.delta = 2.0   # Penalty for Entropy (Resistance)
        self.zeta  = 0.5   # Penalty for Noise
        
        # Awakening Sigmoid Parameters
        self.alpha_A = 2.0 # Non-linearity factor
        self.theta_A = 0.6 # Threshold for Phase Transition
        self.s_A     = 10.0 # Steepness
        
        # Resistance Non-linearity
        self.beta_R  = 1.5 
        
        # Maximum Information Capacities (Bit)
        self.KL_max = 5.0  # Max divergence for normalization
        
class UnresolvedItem:
    """
    Represents an element of U_t (Unresolved Logic/Doubt).
    Managed via Beta Distribution for Bayesian Updating.
    """
    def __init__(self, name: str, alpha=1.0, beta=1.0):
        self.name = name
        self.alpha = alpha # Count of positive evidence
        self.beta = beta   # Count of negative evidence
        
    def update(self, evidence: float):
        """Bayesian Update: evidence > 0 is positive, < 0 is negative"""
        if evidence > 0:
            self.alpha += abs(evidence)
        else:
            self.beta += abs(evidence)
            
    def get_entropy(self) -> float:
        """Calculates Differential Entropy of the belief distribution"""
        # Lower entropy means higher certainty (resolved)
        return beta.entropy(self.alpha, self.beta)

class LoveControlSystem:
    """
    Love-OS v1.3 Kernel
    Dynamics based on Information Theory & Adaptive Control
    """
    def __init__(self, config: LoveConfig):
        self.cfg = config
        
        # System State Variables
        self.A_t = 0.1          # Awakening Level (0.0 - 1.0)
        self.weights = np.array([0.25, 0.25, 0.25, 0.25]) # Channel Weights
        
        # Unresolved Items (U_t) -> Source of Resistance R
        # Initial state: High Uncertainty (Uniform Distribution alpha=1, beta=1)
        self.U_t: List[UnresolvedItem] = [
            UnresolvedItem("Trust_Mechanism"),
            UnresolvedItem("Value_Alignment"),
            UnresolvedItem("Future_Safety")
        ]
        
    def _phi_A(self, A: float) -> float:
        """Awakening Amplification Function (Sigmoid)"""
        numerator = A ** self.cfg.alpha_A
        denominator = 1 + np.exp(-self.cfg.s_A * (A - self.cfg.theta_A))
        return numerator / denominator

    def _calculate_R(self) -> float:
        """Calculate Total Resistance (Sum of Entropies of U_t)"""
        total_entropy = sum([item.get_entropy() for item in self.U_t])
        # Normalize/Scale logic (simplified)
        return max(0, total_entropy)

    def _calculate_TC_norm(self, P_dist, Q_dist) -> float:
        """Calculate Normalized Trust Consistency based on KL Divergence"""
        # epsilon added for numerical stability
        kl = np.sum(P_dist * np.log(P_dist / (Q_dist + 1e-9)))
        tc = 1.0 - (kl / self.cfg.KL_max)
        return max(0, min(1.0, tc))

    def process_step(self, 
                     I_values: np.ndarray, 
                     P_dist: np.ndarray, 
                     Q_dist: np.ndarray, 
                     Evidence_vector: List[float], 
                     Noise_N: float) -> Dict:
        """
        Execute one control cycle (Time step t -> t+1)
        """
        # 1. Bayesian Update of Unresolved Items (Reduces R)
        for i, ev in enumerate(Evidence_vector):
            if i < len(self.U_t):
                self.U_t[i].update(ev)
        
        # 2. Compute Metrics
        C_info = np.dot(self.weights, I_values) # Weighted Channel Capacity
        TC_norm = self._calculate_TC_norm(P_dist, Q_dist)
        R_t = self._calculate_R()
        
        # 3. Compute Potential V (The Objective Function)
        phi_A_val = self._phi_A(self.A_t)
        phi_R_val = R_t ** self.cfg.beta_R
        
        # V = -Term1(Attraction) + Term2(Repulsion) + Term3(Noise)
        V_t = -self.cfg.gamma * phi_A_val * C_info * TC_norm \
              + self.cfg.delta * phi_R_val \
              + self.cfg.zeta * Noise_N
              
        # 4. Compute Gravity Force (Simulated Gradient)
        # G_love is essentially the magnitude of "Negative V" (Depth of the well)
        G_love = -V_t 
        
        # 5. Internal State Update (Awakening Dynamics)
        # Awakening increases as R decreases and C_info increases (Feedback loop)
        dA = 0.05 * (C_info * TC_norm) - 0.02 * R_t
        self.A_t = max(0.0, min(1.0, self.A_t + dA))
        
        return {
            "Time_Step_Analysis": {
                "Potential_V": round(V_t, 4),
                "Gravity_G": round(G_love, 4),
                "Resistance_R": round(R_t, 4),
                "Awakening_A": round(self.A_t, 4),
                "Amplifier_phiA": round(phi_A_val, 4),
                "Capacity_C": round(C_info, 4)
            }
        }

# --- Demonstration Sequence ---
if __name__ == "__main__":
    # Initialize System
    config = LoveConfig()
    os_kernel = LoveControlSystem(config)
    
    print(f"--- Love-OS v1.3 Kernel Initialized ---")
    print(f"Initial Entropy (Uncertainty) of Items: {[u.get_entropy() for u in os_kernel.U_t]}")
    
    # Simulating a Sequence of Interaction (10 Steps)
    # Scenario: User actively "Discloses" and "Verifies" (Evidence > 0)
    
    # Mock Data for Information Inputs
    I_inputs = np.array([0.5, 0.6, 0.4, 0.5]) # Moderate Mutual Information
    P_expt = np.array([0.2, 0.8]) # Expectation
    Q_real = np.array([0.25, 0.75]) # Reality (Slightly off but close)
    
    print("\n--- Starting Control Loop ---")
    for t in range(1, 6):
        # User provides positive evidence to resolve uncertainty
        # (e.g., "I explained my feeling" -> Evidence +1.0)
        evidence = [1.0, 0.8, 0.5] 
        
        result = os_kernel.process_step(
            I_values=I_inputs,
            P_dist=P_expt,
            Q_dist=Q_real,
            Evidence_vector=evidence,
            Noise_N=0.1
        )
        
        metrics = result["Time_Step_Analysis"]
        print(f"Step {t}: R={metrics['Resistance_R']} -> G={metrics['Gravity_G']} (Amp={metrics['Amplifier_phiA']})")
        
        # Simulation of J-Curve effect: 
        # As R drops, A rises. Once A hits theta_A (0.6), Amp shoots up.
        
    print("\n--- Final State ---")
    print(f"Final Entropy of Items: {[round(u.get_entropy(),3) for u in os_kernel.U_t]}")
    print("Status: System Stabilized in Deep Potential Well.")
