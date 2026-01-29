"""
Extended-Physics-LoveOS
Module: metrics.py

This module implements the mathematical Key Performance Indicators (KPIs) 
for the Love-OS framework. It quantifies the efficiency of converting 
Resistance (R) into Complex Energy (E = Er + iEl).

Mathematical Basis:
    dE/dt = (-gamma + i*alpha) * R(t) * E(t)

Author: Love-OS Architect
License: Lila Public License
"""

import numpy as np

class LoveMetrics:
    def __init__(self, dt=1.0, beta=1.0, delta=1.0):
        """
        Initialize the Metrics Calculator.
        
        Args:
            dt (float): Time step interval.
            beta (float): Coefficient for Entropy generation from Resistance.
            delta (float): Coefficient for Entropy reduction from Imaginary Potential.
        """
        self.dt = dt
        self.beta = beta
        self.delta = delta

    def _analyze_series(self, R_series, E_series):
        """
        Helper to derive fundamental physical quantities from time-series data.
        """
        # Ensure numpy arrays
        R = np.array(R_series)
        E = np.array(E_series)
        
        # 1. Total Accumulated Resistance (The "Work" input)
        total_R = np.sum(R) * self.dt
        
        # 2. Phase Dynamics (Unwrap to handle 2pi jumps)
        phases = np.unwrap(np.angle(E))
        d_phi = phases[-1] - phases[0]
        
        # 3. Norm Dynamics (Energy Magnitude)
        norms = np.abs(E)
        norm_start = norms[0]
        norm_end = norms[-1]
        
        # 4. Imaginary Energy Average (Potential)
        El_avg = np.mean(E.imag)
        R_avg = np.mean(R)

        return {
            "total_R": total_R,
            "d_phi": d_phi,
            "norm_start": norm_start,
            "norm_end": norm_end,
            "El_avg": El_avg,
            "R_avg": R_avg,
            "phases": phases,
            "norms": norms
        }

    def estimate_parameters(self, R_series, E_series):
        """
        Reverse-engineers the Architect's internal parameters (alpha, gamma)
        based on observed history.
        
        Returns:
            dict: {'alpha': float, 'gamma': float}
        """
        data = self._analyze_series(R_series, E_series)
        
        # Avoid divide by zero
        if data["total_R"] < 1e-9:
            return {"alpha": 0.0, "gamma": 0.0}

        # Alpha (Phase Rotation Efficiency) ~ d_phi / Integral(R)
        estimated_alpha = data["d_phi"] / data["total_R"]
        
        # Gamma (Dissipation Factor) ~ -ln(|E_end|/|E_start|) / Integral(R)
        # Derived from: |E(t)| = |E(0)| * exp(-gamma * total_R)
        ratio = data["norm_end"] / (data["norm_start"] + 1e-9)
        estimated_gamma = -np.log(ratio) / data["total_R"]
        
        return {
            "alpha": estimated_alpha, 
            "gamma": max(0.0, estimated_gamma) # Gamma cannot be negative in this model
        }

    def calculate_kpis(self, R_series, E_series, manifestation_events=None):
        """
        Calculates the 5 Core Efficiency Metrics for a single dataset.
        
        Args:
            R_series: Array of Resistance values.
            E_series: Array of Complex Energy values.
            manifestation_events: List of indices where 'Projection' (E -> |E|) occurred.
        
        Returns:
            dict: The computed KPIs.
        """
        data = self._analyze_series(R_series, E_series)
        total_R = data["total_R"]
        epsilon = 1e-9

        # --- KPI 1: Phase Efficiency (eta_phi) ---
        # How much rotation per unit of resistance?
        eta_phi = data["d_phi"] / (total_R + epsilon)

        # --- KPI 2: Manifestation Yield (eta_man) ---
        # How much Real Energy (Er) was gained during projection events?
        yield_amount = 0.0
        if manifestation_events:
            E = np.array(E_series)
            for idx in manifestation_events:
                if idx > 0 and idx < len(E):
                    # Gain = Post-event Real - Pre-event Real
                    # Assuming projection: Er_new = |E_old|
                    d_Er = np.abs(E[idx-1]) - E[idx-1].real
                    if d_Er > 0: yield_amount += d_Er
        
        eta_man = yield_amount / (total_R + epsilon)

        # --- KPI 3: Time-to-Threshold (Calculated in comparison usually) ---
        # Here we just return the time to reach phase pi/2 (Quarter turn)
        target_phase = np.pi / 2
        try:
            # Find first index where phase >= target
            idx_crit = np.where(data["phases"] - data["phases"][0] >= target_phase)[0][0]
            time_to_crit = idx_crit * self.dt
        except IndexError:
            time_to_crit = -1.0 # Threshold not reached

        # --- KPI 4: Norm Retention (eta_norm) ---
        # Ratio of energy kept vs initial
        eta_norm = data["norm_end"] / (data["norm_start"] + epsilon)

        # --- KPI 5: Entropy Balance (S_dot_avg) ---
        # S_dot = beta * R - delta * El
        # We want this to be negative (Order creation)
        s_dot_avg = (self.beta * data["R_avg"]) - (self.delta * data["El_avg"])

        return {
            "Phase_Efficiency": eta_phi,
            "Manifestation_Yield": eta_man,
            "Time_To_Threshold": time_to_crit,
            "Norm_Retention": eta_norm,
            "Entropy_Rate": s_dot_avg
        }

    def calculate_efficiency_gain(self, R_before, E_before, R_after, E_after):
        """
        Compares two datasets (Before vs After) and determines if 'Efficiency' occurred.
        """
        kpi_b = self.calculate_kpis(R_before, E_before)
        kpi_a = self.calculate_kpis(R_after, E_after)

        # Calculate Gains (Improvement %)
        def safe_gain(new, old):
            if abs(old) < 1e-9: return 0.0
            return (new - old) / abs(old)

        # Logic: 
        # For Entropy Rate, Lower is Better (so we invert the gain calc)
        # For Time to Threshold, Lower is Better
        
        gains = {
            "Gain_Phase": safe_gain(kpi_a["Phase_Efficiency"], kpi_b["Phase_Efficiency"]),
            "Gain_Norm": safe_gain(kpi_a["Norm_Retention"], kpi_b["Norm_Retention"]),
            "Reduction_Entropy": safe_gain(kpi_b["Entropy_Rate"], kpi_a["Entropy_Rate"]), # Inverse
            "Speedup_Time": 0.0 
        }

        # Speedup Calculation (Handle -1 cases)
        tb, ta = kpi_b["Time_To_Threshold"], kpi_a["Time_To_Threshold"]
        if tb > 0 and ta > 0:
            gains["Speedup_Time"] = (tb - ta) / tb
        
        # Composite Love Score (Weighted)
        # Weights: Phase(30%), Norm(30%), Entropy(20%), Speed(20%)
        love_score_delta = (
            0.3 * gains["Gain_Phase"] +
            0.3 * gains["Gain_Norm"] +
            0.2 * gains["Reduction_Entropy"] +
            0.2 * gains["Speedup_Time"]
        )

        return {
            "Is_More_Efficient": love_score_delta > 0,
            "Love_Score_Delta": love_score_delta,
            "Details": gains
        }

# --- Example Usage ---
if __name__ == "__main__":
    # 1. Simulate "Before" (Ego-driven: High decay, Low rotation)
    t = np.linspace(0, 10, 100)
    R = np.random.uniform(0.5, 1.5, 100) # Constant struggle
    # Low alpha (0.1), High gamma (0.3)
    E_before = np.exp((-0.3 + 0.1j) * np.cumsum(R) * 0.1) 

    # 2. Simulate "After" (Love-OS: Low decay, High rotation)
    # High alpha (0.5), Low gamma (0.05)
    E_after = np.exp((-0.05 + 0.5j) * np.cumsum(R) * 0.1)

    # 3. Calculate metrics
    metrics = LoveMetrics(dt=0.1)
    
    # Estimate Parameters
    params_b = metrics.estimate_parameters(R, E_before)
    params_a = metrics.estimate_parameters(R, E_after)
    
    print(f"--- Calibration Check ---")
    print(f"Before (Ego): Alpha={params_b['alpha']:.3f}, Gamma={params_b['gamma']:.3f}")
    print(f"After (Love): Alpha={params_a['alpha']:.3f}, Gamma={params_a['gamma']:.3f}")

    # Calculate Gain
    result = metrics.calculate_efficiency_gain(R, E_before, R, E_after)
    
    print(f"\n--- Efficiency Report ---")
    print(f"Efficient State Achieved: {result['Is_More_Efficient']}")
    print(f"Love Score Delta: {result['Love_Score_Delta']:.4f}")
    print(f"Details: {result['Details']}")
