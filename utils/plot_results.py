#!/usr/bin/env python3
"""
Plot LO Power Sweep Results

Simple plotting utility for visualizing power vs frequency measurements
from the tinySA-LO characterization system.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_single_sweep(csv_file: Path, ax=None, label=None, **kwargs):
    """
    Plot a single power sweep
    
    Args:
        csv_file: Path to CSV file
        ax: Matplotlib axis (creates new if None)
        label: Label for plot legend
        **kwargs: Additional plot arguments
    """
    # Read data
    df = pd.read_csv(csv_file)
    
    # Extract columns
    freqs = df['frequency_mhz'].values
    powers = df['power_dbm'].values
    
    # Create axis if needed
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    # Determine label from filename if not provided
    if label is None:
        label = csv_file.stem
    
    # Plot
    ax.plot(freqs, powers, marker='o', markersize=2, linewidth=1, 
            label=label, **kwargs)
    
    return ax


def plot_comparison(csv_files: list, output_file: Path = None):
    """
    Plot multiple sweeps for comparison
    
    Args:
        csv_files: List of CSV file paths
        output_file: Optional output file for figure
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(csv_files)))
    
    for csv_file, color in zip(csv_files, colors):
        plot_single_sweep(csv_file, ax=ax, color=color)
    
    ax.set_xlabel('Frequency (MHz)', fontsize=12)
    ax.set_ylabel('Output Power (dBm)', fontsize=12)
    ax.set_title('LO Output Power vs Frequency', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {output_file}")
    
    plt.show()


def plot_power_comparison(csv_p1: Path, csv_p2: Path, output_file: Path = None):
    """
    Plot two power levels side by side for calibration comparison
    
    Args:
        csv_p1: First power level CSV
        csv_p2: Second power level CSV
        output_file: Optional output file
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))
    
    # Read data
    df1 = pd.read_csv(csv_p1)
    df2 = pd.read_csv(csv_p2)
    
    freqs1 = df1['frequency_mhz'].values
    powers1 = df1['power_dbm'].values
    label1 = f"{df1['lo_power_setting'].iloc[0]:+d} dBm"
    
    freqs2 = df2['frequency_mhz'].values
    powers2 = df2['power_dbm'].values
    label2 = f"{df2['lo_power_setting'].iloc[0]:+d} dBm"
    
    # Plot 1: Both power levels
    ax1.plot(freqs1, powers1, 'b-', marker='o', markersize=2, 
             linewidth=1, label=label1)
    ax1.plot(freqs2, powers2, 'r-', marker='o', markersize=2, 
             linewidth=1, label=label2)
    ax1.set_xlabel('Frequency (MHz)')
    ax1.set_ylabel('Output Power (dBm)')
    ax1.set_title('LO Output Power Comparison', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Power difference
    if len(freqs1) == len(freqs2) and np.allclose(freqs1, freqs2):
        power_diff = powers1 - powers2
        ax2.plot(freqs1, power_diff, 'g-', marker='o', markersize=2, linewidth=1)
        ax2.axhline(y=power_diff.mean(), color='k', linestyle='--', 
                   label=f'Mean: {power_diff.mean():.2f} dB')
        ax2.set_xlabel('Frequency (MHz)')
        ax2.set_ylabel('Power Difference (dB)')
        ax2.set_title(f'Power Difference ({label1} - {label2})', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Plot 3: Histogram of power difference
        ax3.hist(power_diff, bins=50, edgecolor='black', alpha=0.7)
        ax3.axvline(x=power_diff.mean(), color='r', linestyle='--', 
                   label=f'Mean: {power_diff.mean():.2f} dB')
        ax3.axvline(x=power_diff.mean() - power_diff.std(), color='orange', 
                   linestyle=':', label=f'±σ: {power_diff.std():.2f} dB')
        ax3.axvline(x=power_diff.mean() + power_diff.std(), color='orange', 
                   linestyle=':')
        ax3.set_xlabel('Power Difference (dB)')
        ax3.set_ylabel('Count')
        ax3.set_title('Power Difference Distribution', fontweight='bold')
        ax3.legend()
    else:
        ax2.text(0.5, 0.5, 'Frequency arrays do not match\nCannot compute difference', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax3.text(0.5, 0.5, 'Frequency arrays do not match\nCannot compute difference', 
                ha='center', va='center', transform=ax3.transAxes, fontsize=12)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {output_file}")
    
    plt.show()


def print_statistics(csv_file: Path):
    """Print statistics for a sweep"""
    df = pd.read_csv(csv_file)
    
    print(f"\nStatistics for: {csv_file.name}")
    print("=" * 60)
    print(f"Total points: {len(df)}")
    print(f"Frequency range: {df['frequency_mhz'].min():.2f} - {df['frequency_mhz'].max():.2f} MHz")
    print(f"Power range: {df['power_dbm'].min():.2f} - {df['power_dbm'].max():.2f} dBm")
    print(f"Mean power: {df['power_dbm'].mean():.2f} dBm")
    print(f"Std deviation: {df['power_dbm'].std():.3f} dB")
    print(f"Peak-to-peak: {df['power_dbm'].max() - df['power_dbm'].min():.2f} dB")
    
    if 'lo_power_setting' in df.columns:
        print(f"LO setting: {df['lo_power_setting'].iloc[0]:+d} dBm")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Plot LO power sweep results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Plot single sweep:
  python plot_results.py results/sweep_+5dBm.csv
  
  # Compare multiple sweeps:
  python plot_results.py results/sweep_+5dBm.csv results/sweep_-4dBm.csv
  
  # Dual power comparison with difference plot:
  python plot_results.py --compare results/sweep_+5dBm.csv results/sweep_-4dBm.csv
  
  # Just print statistics:
  python plot_results.py --stats-only results/sweep.csv
        """
    )
    
    parser.add_argument('files', nargs='+', help='CSV file(s) to plot')
    parser.add_argument('--output', '-o', help='Save figure to file')
    parser.add_argument('--compare', action='store_true',
                       help='Comparison plot for dual power measurements')
    parser.add_argument('--stats-only', action='store_true',
                       help='Print statistics only (no plot)')
    
    args = parser.parse_args()
    
    # Convert to Path objects
    csv_files = [Path(f) for f in args.files]
    
    # Check files exist
    for f in csv_files:
        if not f.exists():
            print(f"ERROR: File not found: {f}")
            return 1
    
    # Print statistics
    for f in csv_files:
        print_statistics(f)
    
    if args.stats_only:
        return 0
    
    # Determine output file
    output_file = Path(args.output) if args.output else None
    
    # Plot based on mode
    if args.compare:
        if len(csv_files) != 2:
            print("ERROR: --compare requires exactly 2 files")
            return 1
        plot_power_comparison(csv_files[0], csv_files[1], output_file)
    else:
        plot_comparison(csv_files, output_file)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
