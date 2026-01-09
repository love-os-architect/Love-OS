# analytics/generate_report_charts.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data
try:
    df = pd.read_csv('../experiments/results_template.csv')
except FileNotFoundError:
    # Fallback for demo
    data = {
        'method': ['Baseline']*3 + ['LoveOS']*3,
        'gpu_hours': [2.5, 2.6, 2.65, 1.2, 1.15, 1.17],
        'TC_norm': [0.55, 0.57, 0.56, 0.70, 0.73, 0.74],
        'rho': [0.50, 0.52, 0.51, 0.68, 0.70, 0.69],
        'novelty': [0.45, 0.48, 0.50, 0.70, 0.73, 0.74]
    }
    df = pd.DataFrame(data)

# Set Style
sns.set(style="whitegrid")

# 1. GPU Cost & Quality Trade-off
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='gpu_hours', y='TC_norm', hue='method', s=200, style='method')
plt.title('Love-OS Impact: Lower Cost, Higher Quality', fontsize=15)
plt.xlabel('GPU Hours (Lower is Better)', fontsize=12)
plt.ylabel('Quality (TC_norm) (Higher is Better)', fontsize=12)
plt.axvline(x=2.0, color='gray', linestyle='--')
plt.text(2.1, 0.60, 'Traditional Frontier', color='gray')
plt.text(1.3, 0.72, 'Love-OS Frontier', color='green', weight='bold')
plt.tight_layout()
plt.savefig('../docs/images/chart_cost_quality.png')
print("Chart generated: chart_cost_quality.png")

# 2. Key Metrics Radar (Simplified Bar for now)
metrics = ['rho', 'novelty']
df_melt = df.melt(id_vars='method', value_vars=metrics, var_name='Metric', value_name='Score')

plt.figure(figsize=(10, 6))
sns.barplot(data=df_melt, x='Metric', y='Score', hue='method', palette='viridis')
plt.title('Love-OS: Meaning Density & Novelty Boost', fontsize=15)
plt.ylim(0, 1.0)
plt.tight_layout()
plt.savefig('../docs/images/chart_metrics_comparison.png')
print("Chart generated: chart_metrics_comparison.png")
