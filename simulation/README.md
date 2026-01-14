# Love-Ego Dynamics Simulation
## The Mathematics of Awakening 
This simulation mathematically demonstrates the core theorem of Love-OS: **"Effort implies nothing unless the threshold is crossed."**

It models the dynamics of Consciousness ($C$) based on the interaction between Love ($L$) and Ego ($E$).

### The Core Equation
The time evolution of consciousness is described by the following differential equation:

$$
\frac{dC}{dt} = L(t) \cdot C \left(1 - \frac{C}{C_{max}}\right) - \alpha \cdot E(t) \cdot C + S(t)
$$

* **$L(t)$: Love Constant (Integration Force).** Acts as the growth rate in the logistic term.
* **$E(t)$: Ego Density (Separation Resistance).** Acts as a decay factor.
* **$S(t)$: Source (External Stimuli).** Temporary boosts (e.g., meditation, workshops).
* **$\alpha$: Separation Coefficient.**

### The Event Horizon 
The simulation reveals a critical phase transition point. The steady-state solution $C^*$ is:

$$
C^* = \begin{cases} C_{max}\left(1 - \frac{\alpha E}{L}\right) & (L > \alpha E) \\ 0 & (L \le \alpha E) \end{cases}
$$

* **Awakening Phase ($L > \alpha E$):** Consciousness stabilizes at a high level.
* **Decay Phase ($L \le \alpha E$):** Consciousness inevitably collapses to zero, regardless of temporary efforts ($S$).

**Conclusion:** To sustain higher consciousness, one must not just "add effort" ($S$), but fundamentally **increase Love ($L$) or decrease Ego ($E$) to cross the threshold.**

### Usage
Run the simulation to generate the Phase Transition Heatmap and Time Series analysis.

```bash
python love_ego_dynamics.py
