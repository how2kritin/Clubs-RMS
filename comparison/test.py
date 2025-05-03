import json
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from statistics import mean, mode
import seaborn as sns

# Set up styling
sns.set(style="whitegrid")

# Helper to extract and compute stats
def extract_stats(filepath):
    with open(filepath) as f:
        data = json.load(f)
    times = data["results"][0]["times"]
    print(len(times))
    stats = {
        "min": min(times),
        "max": max(times),
        "avg": mean(times),
        "mode": mode(times),
        "times": times
    }
    return stats

# Load stats
file1 = "monolith.json"  # Replace with second file path as needed
file2 = "microservice.json"   # <- Replace this with your second file

stats1 = extract_stats(file1)
stats2 = extract_stats(file2)

labels = ["Min", "Max", "Average", "Mode"]
json1_values = [stats1["min"], stats1["max"], stats1["avg"], stats1["mode"]]
json2_values = [stats2["min"], stats2["max"], stats2["avg"], stats2["mode"]]

x = np.arange(len(labels))
width = 0.35

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width/2, json1_values, width, label='Monolith')
rects2 = ax.bar(x + width/2, json2_values, width, label='Microservice')

ax.set_ylabel('Response Time in ms (lower is better)')
ax.set_title('Comparison of Response Time Statistics')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.show()

# Optional: Histogram to compare distributions
plt.figure(figsize=(10, 6))
sns.histplot(stats1["times"], color='blue', label='Monolith', kde=True, stat="density")
sns.histplot(stats2["times"], color='orange', label='Microservice', kde=True, stat="density")
plt.title('Distribution of Response Times')
plt.xlabel('Response Time in ms (lower is better)')
plt.ylabel('Density')
plt.legend()
plt.show()
