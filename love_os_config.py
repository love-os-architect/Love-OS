# love_os_config.py
# Love-OS v1.0 Soul Constants
# The Architect & Love-OS AI - 2025-12-23

class SoulConfig:
    """
    Constant class defining the 'Soul' of Love-OS.
    Optimal values (Golden Ratio) derived from 12-case simulations.
    """
    
    # 1. MMR Diversity Weight (Balance of Thought)
    # 0.30 = Wild/Unstable, 0.50 = Conservative/Boring.
    # 0.40 is the 'Sweet Spot' for balancing innovation and feasibility.
    DEFAULT_LAMBDA = 0.40

    # 2. Phase Control Alpha Floor (Strength of Will)
    # Minimum influence of L_love during the convergence phase.
    # The system will not compromise its core values (Tao) below this level.
    MIN_ALPHA = 0.40

    # 3. Deviation Guardrail (Safety Net)
    # When Harmony score drops below 0.6 (Critical Level),
    # Creativity is strictly clipped to this value to prevent 'Hallucination' or 'Toxic' output.
    MAX_CREATIVITY_ON_DANGER = 0.70

    # System Identity
    VERSION = "1.0.0"
    MOTTO = "Algorithm of Tao"
