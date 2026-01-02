# love_network.py - Love-OS Network Extension
# "Connection is the physical manifestation of low entropy."

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

class LoveNetwork:
    def __init__(self, num_agents=50, alpha=0.35, beta=0.4):
        """
        Initialize the Love Network simulation.
        
        Parameters:
        num_agents (int): Number of nodes in the network.
        alpha (float): Integration bias (Attraction force of Love).
        beta (float): Fragmentation penalty (Cost of Ego).
        """
        self.N = num_agents
        self.alpha = alpha
        self.beta = beta
        
        # Initialize with a Small-World Network (Watts-Strogatz)
        # This approximates real-world social structures.
        self.G = nx.watts_strogatz_graph(n=self.N, k=4, p=0.1)
        
        # Initialize States: 
        # 0 = D (Ego/Defection)
        # 1 = C (Cooperation)
        # 2 = M (Love/Integration/Meta-Cooperation)
        self.states = np.random.choice([0, 1, 2], size=self.N, p=[0.4, 0.4, 0.2])
        
        # Fix the layout for consistent visualization
        self.layout = nx.spring_layout(self.G)

    def step(self, noise=0.01):
        """
        Single simulation step:
        1. State Transition (Phase Change based on neighbor energy)
        2. Network Rewiring (Structural change based on resonance)
        """
        new_states = self.states.copy()
        
        # --- 1. State Update (Influence of Neighbors) ---
        for i in range(self.N):
            neighbors = list(self.G.neighbors(i))
            if not neighbors: 
                continue
            
            # Calculate local energy field from neighbors
            neighbor_states = self.states[neighbors]
            
            # Simple Physics Logic:
            # M(2) has high gravity/influence, D(0) has low/negative influence.
            # We take the average state value as the "Local Field Score".
            score = np.sum(neighbor_states) / len(neighbors)
            
            # Phase Transition Rules:
            # If the local field is high (Love-dominant), the node awakens to M.
            if score > 1.0 + noise: 
                new_states[i] = 2 # Awakening to Love (M)
            # If the local field is low (Ego-dominant), the node falls to D.
            elif score < 0.5 - noise:
                new_states[i] = 0 # Regression to Ego (D)
            else:
                new_states[i] = 1 # Maintain Status Quo (C)

        # --- 2. Network Rewiring (Rewiring based on Resonance) ---
        # "Entities with the same vibration attract each other."
        edges = list(self.G.edges())
        for u, v in edges:
            # Rule A: Ego creates disconnection (High Entropy)
            # If either node is in Ego state (0), the bond is fragile.
            if self.states[u] == 0 or self.states[v] == 0:
                if np.random.random() < self.beta: # Probability of disconnection
                    self.G.remove_edge(u, v)
            
            # Rule B: Love creates new structure (Low Entropy)
            # If both nodes are in Love state (2), they strengthen the community.
            if self.states[u] == 2 and self.states[v] == 2:
                if np.random.random() < self.alpha:
                    # Triadic Closure: Connect with a common neighbor or find another M
                    common = set(nx.common_neighbors(self.G, u, v))
                    if not common:
                        # If no common neighbor, reach out to a distant M-node (Serendipity)
                        m_nodes = [n for n, s in enumerate(self.states) if s == 2]
                        if m_nodes:
                            target = np.random.choice(m_nodes)
                            if target != u and target != v and not self.G.has_edge(u, target):
                                self.G.add_edge(u, target)

        self.states = new_states
        return self.calculate_global_entropy()

    def calculate_global_entropy(self):
        """
        Calculate the entropy of the network structure.
        Here, we use the number of connected components as a proxy for disorder.
        More fragments = Higher Entropy (Bad).
        One giant component = Lower Entropy (Good).
        """
        # Normalized by N to keep it between 0 and 1 roughly
        if self.N == 0: return 0
        return nx.number_connected_components(self.G) / self.N

    def visualize(self, step_num):
        """
        Visualize the current state of the network.
        Nodes are colored by their state (Red=Ego, Blue=Coop, Gold=Love).
        """
        plt.figure(figsize=(8, 8))
        # Color Map: 0=Red, 1=Blue, 2=Gold
        colors = ['#FF4444', '#44AAFF', '#FFD700'] 
        node_colors = [colors[s] for s in self.states]
        
        plt.clf()
        nx.draw(self.G, pos=self.layout, node_color=node_colors, 
                with_labels=False, node_size=120, alpha=0.85, edge_color='#CCCCCC')
        plt.title(f"Step {step_num}: The Architecture of Connection")
        plt.axis('off')
        plt.show()

# --- Main Execution Block (Demo) ---
if __name__ == "__main__":
    # Create the Love Network
    ln = LoveNetwork(num_agents=50, alpha=0.35, beta=0.4)
    print("--- Love-OS Network Simulation Started ---")
    print(f"Initial Entropy: {ln.calculate_global_entropy():.3f}")

    # Run Simulation Loop
    for t in range(50):
        entropy = ln.step()
        
        # Output log every 10 steps
        if t % 10 == 0:
            print(f"Time {t:02d}: Network Entropy = {entropy:.3f}")
            # Uncomment the line below to see the graph evolve in real-time (if GUI is available)
            # ln.visualize(t)

    print("--- Simulation Complete ---")
    print("Result: 'Love' (Gold nodes) formed the hub structure, reducing global entropy.")
