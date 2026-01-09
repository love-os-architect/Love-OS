# core/intuition_selector.py
# -*- coding: utf-8 -*-
"""
Love-OS Intuition Selector (The Corpus Callosum)
================================================
This module acts as the bridge between the Right Brain (Generative/Chaotic) 
and the Left Brain (Logical/Training).

It selects the best candidates from the latent space based on the 
Love-Ising Meta Theory, prioritizing 'Novelty', 'Meaning Density', 
and 'High-Density Exceptions' (mistakes in the script).

Preset: CREATIVITY-FIRST (CREATIVE_MAX)
"""

from typing import List, Dict, Any, Tuple
import numpy as np

# ==========================================
# 1. Configuration: Creativity-First Preset
# ==========================================
CREATIVE_MAX_CONFIG = {
    "weights": {
        "novelty": 0.25,   # Newness (Most Important)
        "rho":     0.20,   # Meaning Density (Short & Deep)
        "sigma":   0.15,   # Re-combinability (Fuel for next step)
        "d":       0.10,   # Reachability (1 - distance)
        "gamma":   0.10,   # Resonance (Image-Text Harmony)
        "lambda":  0.10,   # Shortness/Simplicity
        "beta":    0.05,   # Aesthetic Alignment
        "M":       0.05    # Binding Score
    },
    "hard_constraints": {
        "beta_min":  0.35, # Minimum Aesthetic
        "gamma_min": 0.30, # Minimum Resonance
        "phi_tol":   0.65  # Phase Tolerance (Wide for exploration)
    },
    "diversity_alpha": 0.65, # MMR Balance (Higher = More Diversity)
    "exception_boost": 1.35, # Boost factor for 'Exceptions'
    "time_decay":      0.85, # Decay for old R-buffer stats
    "K":               5     # Number of items to select
}

# ==========================================
# 2. Main Logic: Intuition Selector
# ==========================================
def intuition_selector(candidates: List[Any], 
                       r_buffer: Any, 
                       tc_norm: Any, 
                       config: Dict = CREATIVE_MAX_CONFIG) -> Tuple[List[Any], List[Dict]]:
    """
    Selects 'Intuitive' candidates by optimizing for shortest path to binding principles,
    while treating 'Exceptions' as high-density meaning points.
    """
    
    # --- 0. Setup ---
    w = config["weights"]
    hard = config["hard_constraints"]
    alpha = config["diversity_alpha"]
    exc_boost = config["exception_boost"]
    K = config["K"]

    # --- 1. Preprocessing & Normalization ---
    # Fill missing metrics using R-buffer stats and Normalize to [0,1]
    # (Implementation of helper functions assumed)
    # fill_missing_metrics_with_R_stats(candidates, r_buffer)
    # normalize_candidates(candidates) 

    # Invert 'lambda' and 'd' (Lower is better -> Higher score)
    for c in candidates:
        c.lambda_score = 1.0 - getattr(c, 'lambda_norm', 0.5)
        c.reachability = 1.0 - getattr(c, 'd_norm', 0.5)

    # --- 2. Novelty & Exception Boosting (Right-Brain Logic) ---
    # Calculate Novelty based on distance from R-buffer center
    # r_repr = compute_R_representatives(r_buffer, config["time_decay"])
    
    for c in candidates:
        # Placeholder for embedding distance logic
        # c.novelty = embedding_distance_to_R(c.v, c.t, r_repr)
        
        # KEY LOGIC: "Mistakes" are valid resources
        if getattr(c, 'is_exception', False):
            c.rho_norm = min(1.0, c.rho_norm * exc_boost)
            c.novelty  = min(1.0, c.novelty * exc_boost)

    # --- 3. Hard Constraint Filtering ---
    filtered = []
    for c in candidates:
        if c.beta_norm < hard["beta_min"]: continue
        if c.gamma_norm < hard["gamma_min"]: continue
        if abs(c.phi_norm) > hard["phi_tol"]: continue
        filtered.append(c)

    # Fallback: Relax constraints if too strict
    if not filtered:
        # filtered = relax_constraints(candidates, hard)
        filtered = candidates # Temporary fallback

    # --- 4. Composite Scoring (Creativity Weighted) ---
    for c in filtered:
        c.composite = (
            w['novelty'] * c.novelty      +
            w['rho']     * c.rho_norm     +
            w['sigma']   * c.sigma_norm   +
            w['d']       * c.reachability +
            w['gamma']   * c.gamma_norm   +
            w['lambda']  * c.lambda_score +
            w['beta']    * c.beta_norm    +
            w['M']       * getattr(c, 'M_norm', 0)
        )

    # --- 5. Diversity Selection (Pareto + MMR) ---
    # Sort by Score first
    remaining = sorted(filtered, key=lambda x: x.composite, reverse=True)
    s_top = []

    while len(s_top) < K and remaining:
        # Pick the absolute best first
        if not s_top:
            s_top.append(remaining.pop(0))
            continue
            
        # For subsequent picks, use MMR (Score - Similarity penalty)
        best_idx = -1
        best_mmr_val = -float('inf')

        for i, cand in enumerate(remaining):
            # sim_to_S = max(similarity(cand, s) for s in s_top)
            sim_to_S = 0.5 # Placeholder
            
            mmr = alpha * cand.composite - (1.0 - alpha) * sim_to_S
            
            if mmr > best_mmr_val:
                best_mmr_val = mmr
                best_idx = i
        
        if best_idx != -1:
            s_top.append(remaining.pop(best_idx))

    # --- 6. Audit Log & Feedback ---
    audit_log = []
    for c in s_top:
        log_entry = {
            'id': getattr(c, 'id', 'unknown'),
            'composite': round(c.composite, 4),
            'rho': getattr(c, 'rho_norm', 0),
            'novelty': getattr(c, 'novelty', 0),
            'is_exception': getattr(c, 'is_exception', False),
            'reason': explain_choice(c)
        }
        audit_log.append(log_entry)

    # Update TC_norm and Write back to R-buffer (The Cycle)
    # update_TC_norm(tc_norm, s_top, audit_log)
    # for c in s_top:
    #     write_back_to_R(r_buffer, c)

    return s_top, audit_log

# --- Helper: Explain the Choice (The "Translator") ---
def explain_choice(c: Any) -> str:
    """Generates a natural language explanation for the Left Brain."""
    text = (
        f"Selected for High Novelty ({c.novelty:.2f}) & Density (rho={c.rho_norm:.2f}). "
        f"Re-combinability (sigma={c.sigma_norm:.2f}) fuels the next cycle. "
        f"Reachability (1-d={c.reachability:.2f}) is sufficient. "
    )
    if getattr(c, 'is_exception', False):
        text += " [LOVE-OS]: Identified as a High-Density Exception Point (Script Deviation)."
    return text
