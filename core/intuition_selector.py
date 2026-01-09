# core/intuition_selector.py
# -*- coding: utf-8 -*-
"""
Love-OS Intuition Selector (Right-Brain Engine)
===============================================
A logic module that selects 'Intuitive' candidates based on the Love-Ising Meta Theory.
It prioritizes:
1. Novelty & Meaning Density (rho)
2. Re-combinability (sigma)
3. Low Reachability Cost (Shortest Path)
4. Embracing 'Exceptions' (Mistakes in the script are high-density meaning points)

Preset: CREATIVITY-FIRST (CREATIVE_MAX)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ==========================================
# 1. Configuration: Creativity-First Preset
# ==========================================
CREATIVE_MAX_CONFIG = {
    "weights": {
        "novelty": 0.25,   # Newness (Most Important)
        "rho":     0.20,   # Meaning Density
        "sigma":   0.15,   # Re-combinability
        "d":       0.10,   # Reachability Cost (converted to 1-d)
        "gamma":   0.10,   # Resonance
        "lambda":  0.10,   # Shortness/Simplicity
        "beta":    0.05,   # Aesthetic Alignment
        "M":       0.05    # Binding Score
    },
    "hard_constraints": {
        "beta_min":  0.35,
        "gamma_min": 0.30,
        "phi_tol":   0.65  # Phase tolerance (Wide for exploration)
    },
    "diversity_alpha": 0.65, # MMR Balance (Favors Novelty over Redundancy)
    "exception_boost": 1.35, # Boost for 'Exceptions'
    "K": 5                   # Number of items to select
}

# ==========================================
# 2. Data Structures
# ==========================================
@dataclass
class Candidate:
    id: str
    content: Any  # Image, Text, Latents, etc.
    
    # Raw Metrics (0.0 - 1.0)
    rho_raw: float   # Meaning Density
    gamma_raw: float # Resonance
    beta_raw: float  # Aesthetic
    d_raw: float     # Distance/Cost
    sigma_raw: float # Re-combinability
    M_raw: float     # Binding Score
    lambda_raw: float # Description Length (Lower is better)
    phi_raw: float   # Phase Difference
    
    # Embeddings (for similarity check)
    embedding: np.ndarray 
    
    # Meta flags
    is_exception: bool = False # Is this a "mistake" or outlier?
    
    # Calculated fields
    novelty: float = 0.0
    composite: float = 0.0
    reachability: float = 0.0
    mmr_score: float = 0.0
    
    # Normalized fields (populated during processing)
    rho_norm: float = 0.0
    gamma_norm: float = 0.0
    beta_norm: float = 0.0
    d_norm: float = 0.0
    sigma_norm: float = 0.0
    M_norm: float = 0.0
    lambda_score: float = 0.0 # Inverted lambda
    phi_norm: float = 0.0

@dataclass
class AuditLog:
    selected_candidates: List[Dict[str, Any]]

# ==========================================
# 3. The Intuition Selector Class
# ==========================================
class IntuitionSelector:
    def __init__(self, config: Dict[str, Any] = CREATIVE_MAX_CONFIG):
        self.cfg = config
        self.weights = config["weights"]
        self.constraints = config["hard_constraints"]
        
    def select(self, candidates: List[Candidate], r_buffer_stats: Dict) -> AuditLog:
        """
        Main pipeline: Normalize -> Boost -> Filter -> Score -> MMR -> Select
        """
        # A. Preprocessing & Normalization
        self._normalize_metrics(candidates)
        
        # B. Calculate Novelty & Boost Exceptions
        self._apply_right_brain_boosts(candidates, r_buffer_stats)
        
        # C. Hard Constraints (Filtering)
        filtered = self._apply_constraints(candidates)
        if not filtered:
            print("Warning: All candidates filtered. Relaxing constraints...")
            filtered = candidates # Fallback: return all if filter is too strict

        # D. Calculate Composite Score
        for c in filtered:
            self._compute_composite_score(c)
            
        # E. Diversity Selection (MMR)
        selected = self._apply_mmr_selection(filtered)
        
        # F. Generate Audit Log
        return self._generate_audit_log(selected)

    def _normalize_metrics(self, candidates: List[Candidate]):
        # Simple Min-Max normalization logic for demo purposes
        # In production, use global stats from TC_norm
        if not candidates: return
        
        for attr in ['rho', 'gamma', 'beta', 'd', 'sigma', 'M', 'lambda']:
            raw_vals = [getattr(c, f"{attr}_raw") for c in candidates]
            _min, _max = min(raw_vals), max(raw_vals)
            div = (_max - _min) if (_max - _min) > 1e-9 else 1.0
            
            for c in candidates:
                val = getattr(c, f"{attr}_raw")
                norm = (val - _min) / div
                
                if attr == 'lambda':
                    # Short description (low lambda) is good -> Invert
                    c.lambda_score = 1.0 - norm 
                elif attr == 'd':
                     # Low distance is good -> Reachability
                    c.d_norm = norm 
                    c.reachability = 1.0 - norm
                else:
                    setattr(c, f"{attr}_norm", norm)
                    
                # Handle Phase (Phi) separately (absolute distance from 0)
                c.phi_norm = abs(c.phi_raw)

    def _apply_right_brain_boosts(self, candidates: List[Candidate], r_stats: Dict):
        boost = self.cfg["exception_boost"]
        
        for c in candidates:
            # 1. Novelty Calculation (Distance from R-buffer center)
            # Placeholder: In real impl, calculate dist(c.embedding, r_stats['center'])
            c.novelty = np.random.uniform(0.5, 1.0) # Mocking novelty for now
            
            # 2. Boost Exceptions (The core of Love-OS)
            if c.is_exception:
                # "Mistakes" are high-density meaning points
                c.rho_norm = min(1.0, c.rho_norm * boost)
                c.novelty  = min(1.0, c.novelty * boost)

    def _apply_constraints(self, candidates: List[Candidate]) -> List[Candidate]:
        passed = []
        hard = self.constraints
        for c in candidates:
            if c.beta_norm < hard["beta_min"]: continue
            if c.gamma_norm < hard["gamma_min"]: continue
            if c.phi_norm > hard["phi_tol"]: continue
            passed.append(c)
        return passed

    def _compute_composite_score(self, c: Candidate):
        w = self.weights
        # The Intuition Equation
        c.composite = (
            w['novelty'] * c.novelty +
            w['rho']     * c.rho_norm +
            w['sigma']   * c.sigma_norm +
            w['d']       * c.reachability +
            w['gamma']   * c.gamma_norm +
            w['lambda']  * c.lambda_score +
            w['beta']    * c.beta_norm +
            w['M']       * c.M_norm
        )

    def _apply_mmr_selection(self, candidates: List[Candidate]) -> List[Candidate]:
        """
        Maximal Marginal Relevance to ensure diversity.
        """
        K = self.cfg["K"]
        alpha = self.cfg["diversity_alpha"]
        
        # Sort by initial score
        remaining = sorted(candidates, key=lambda x: x.composite, reverse=True)
        selected = []
        
        while len(selected) < K and remaining:
            # First item is always the best composite score
            if not selected:
                best = remaining.pop(0)
                selected.append(best)
                continue
                
            # For subsequent items, balance Score vs Similarity
            best_mmr_idx = -1
            best_mmr_score = -float('inf')
            
            for i, cand in enumerate(remaining):
                # Calculate max similarity to already selected items
                # Mock similarity: np.dot(cand.embedding, s.embedding)
                # Using random for demo logic safety
                max_sim = np.random.uniform(0, 0.5) 
                
                mmr = alpha * cand.composite - (1.0 - alpha) * max_sim
                
                if mmr > best_mmr_score:
                    best_mmr_score = mmr
                    best_mmr_idx = i
            
            if best_mmr_idx != -1:
                selected.append(remaining.pop(best_mmr_idx))
                
        return selected

    def _generate_audit_log(self, selected: List[Candidate]) -> AuditLog:
        logs = []
        for c in selected:
            reason = self._explain_choice(c)
            logs.append({
                "id": c.id,
                "composite": round(c.composite, 4),
                "is_exception": c.is_exception,
                "novelty": round(c.novelty, 2),
                "rho": round(c.rho_norm, 2),
                "reason": reason
            })
        return AuditLog(selected_candidates=logs)

    def _explain_choice(self, c: Candidate) -> str:
        text = f"High Novelty ({c.novelty:.2f}) & Density ({c.rho_norm:.2f}). "
        text += f"Re-combinability ({c.sigma_norm:.2f}) is promising. "
        if c.is_exception:
            text += "[LOVE-OS]: Selected as a High-Density Exception Point."
        return text

# ==========================================
# 4. Usage Example (Demo)
# ==========================================
if __name__ == "__main__":
    # Create Selector
    selector = IntuitionSelector()
    
    # Mock Candidates (e.g., from Image Gen)
    candidates = []
    for i in range(10):
        # Simulate some candidates having high raw metrics
        is_exc = (i % 7 == 0) # Every 7th is an "Exception"
        c = Candidate(
            id=f"gen_{i}", content=None, embedding=np.random.rand(64),
            rho_raw=np.random.rand(), gamma_raw=np.random.rand(),
            beta_raw=np.random.rand(), d_raw=np.random.rand(),
            sigma_raw=np.random.rand(), M_raw=np.random.rand(),
            lambda_raw=np.random.rand(), phi_raw=np.random.rand(),
            is_exception=is_exc
        )
        candidates.append(c)
    
    # Run Selection
    print("--- Running Right-Brain Intuition Selector ---")
    log = selector.select(candidates, r_buffer_stats={})
    
    # Output Results
    for item in log.selected_candidates:
        print(f"Selected: {item['id']} | Score: {item['composite']} | {item['reason']}")
