"""
Visualization Service Module.
Uses Matplotlib to generate charts based on pipeline results.
"""
import os
import json
import matplotlib.pyplot as plt
from typing import Dict, List, Any

# Create output folder
OUTPUT_DIR = "visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_pc_distribution(results: List[Dict[str, Any]], filename="pc_distribution.png"):
    """Plots a histogram of the calculated collision probabilities."""
    pcs = [r.get("calculated_pc", 0) for r in results if r.get("calculated_pc")]
    
    if not pcs:
        return
        
    plt.figure(figsize=(8, 5))
    plt.hist(pcs, bins=10, color='skyblue', edgecolor='black')
    plt.title("Probability of Collision Distribution")
    plt.xlabel("PC Value")
    plt.ylabel("Count")
    plt.grid(axis='y', alpha=0.7)

    plt.savefig(f"{OUTPUT_DIR}/{filename}")
    plt.close()


def plot_pipeline_summary(results: List[Dict[str, Any]], filename="pipeline_summary.png"):
    """Plots a summary of Delta-V and Risk decisions."""
    x = list(range(len(results)))
    dv_values = [r.get("delta_v_kms", 0) for r in results]
    risk_levels = [1 if r.get("risk_level") == "HIGH RISK" else 0 for r in results] # 1 for HIGH, 0 for LOW

    plt.figure(figsize=(10, 6))
    
    plt.subplot(2, 1, 1)
    plt.plot(x, dv_values, marker="o", color='darkgreen', linestyle='-', label="Delta-V (km/s)")
    plt.title("Maneuver Delta-V Over Time")
    plt.ylabel("Delta-V (km/s)")
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.plot(x, risk_levels, marker="x", color='red', linestyle='--', label="Risk Level (1=High)")
    plt.xlabel("CDM Index")
    plt.ylabel("Risk Level")
    plt.yticks([0, 1], ['LOW', 'HIGH'])
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/{filename}")
    plt.close()


def generate_all_visualizations(pipeline_results: List[Dict[str, Any]]):
    """Entry point to generate all required plots."""
    print(f"\n[Visualization] Generating plots and saving to {OUTPUT_DIR}/...")
    plot_pc_distribution(pipeline_results)
    plot_pipeline_summary(pipeline_results)
    print("[Visualization] Plots generated successfully.")