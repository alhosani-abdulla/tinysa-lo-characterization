#!/usr/bin/env python3
"""
Local Oscillator Power Sweep Measurement

Automated measurement of ADF4351 LO output power across frequency range
using tinySA Ultra spectrum analyzer.

This script coordinates:
1. Arduino/ADF4351 to generate RF at each frequency
2. tinySA Ultra to measure peak power at that frequency
3. Data collection and storage to CSV or FITS format
"""

import argparse
import sys
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import numpy as np

from arduino_controller import ArduinoLOController, find_arduino_ports
from tinysa_controller import TinySAController


class LOPowerSweep:
    """Main class for coordinating LO power sweep measurements"""
    
    def __init__(self, config: Dict):
        """
        Initialize sweep measurement system
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.arduino: Optional[ArduinoLOController] = None
        self.tinysa: Optional[TinySAController] = None
        self.results: List[Dict] = []
        
    def setup(self) -> None:
        """Initialize hardware connections"""
        print("=" * 60)
        print("LO Power Sweep Measurement Setup")
        print("=" * 60)
        
        # Connect to Arduino
        arduino_port = self.config['arduino_port']
        print(f"\nConnecting to Arduino at {arduino_port}...")
        self.arduino = ArduinoLOController(arduino_port)
        self.arduino.connect()
        
        # Set initial power level
        lo_power = self.config['lo_power']
        print(f"Setting LO power to {lo_power} dBm...")
        self.arduino.set_power(lo_power)
        
        # Connect to tinySA
        tinysa_port = self.config['tinysa_port']
        print(f"\nConnecting to tinySA...")
        self.tinysa = TinySAController(port=tinysa_port)
        self.tinysa.connect()
        
        # Apply tinySA settings
        if self.config.get('rbw') != 'auto':
            self.tinysa.set_rbw(self.config['rbw'])
        
        if self.config.get('attenuation') != 'auto':
            self.tinysa.set_attenuation(self.config['attenuation'])
        
        print("\n" + "=" * 60)
        print("Setup complete. Ready for measurements.")
        print("=" * 60 + "\n")
    
    def generate_frequency_list(self) -> np.ndarray:
        """
        Generate list of frequencies to measure
        
        Returns:
            Array of frequencies in MHz
        """
        freq_start = self.config['freq_start']
        freq_stop = self.config['freq_stop']
        freq_step = self.config['freq_step']
        
        # Generate frequency array
        num_points = int((freq_stop - freq_start) / freq_step) + 1
        frequencies = np.linspace(freq_start, freq_stop, num_points)
        
        return frequencies
    
    def measure_single_frequency(self, freq_mhz: float) -> Dict:
        """
        Measure power at a single frequency
        
        Args:
            freq_mhz: Frequency in MHz
            
        Returns:
            Dictionary with measurement results
        """
        # Set Arduino to this frequency
        if not self.arduino.set_frequency(freq_mhz):
            raise RuntimeError(f"Failed to set Arduino frequency to {freq_mhz} MHz")
        
        # Wait for settling
        time.sleep(self.config['settling_time'])
        
        # Measure with tinySA
        peak_power = self.tinysa.measure_power_at_frequency(
            freq_mhz=freq_mhz,
            span_mhz=self.config['span'],
            averaging=self.config['averaging']
        )
        
        # Record measurement
        measurement = {
            'timestamp': datetime.now().isoformat(),
            'frequency_mhz': freq_mhz,
            'power_dbm': peak_power,
            'lo_power_setting': self.config['lo_power']
        }
        
        return measurement
    
    def run_sweep(self) -> None:
        """Execute full frequency sweep"""
        frequencies = self.generate_frequency_list()
        total_points = len(frequencies)
        
        print(f"Starting sweep: {frequencies[0]:.1f} - {frequencies[-1]:.1f} MHz")
        print(f"Total points: {total_points}")
        print(f"Step size: {self.config['freq_step']:.3f} MHz")
        print(f"LO Power: {self.config['lo_power']} dBm")
        print(f"Span: {self.config['span']} MHz")
        print(f"Averaging: {self.config['averaging']}x")
        print()
        
        start_time = time.time()
        
        for i, freq in enumerate(frequencies, 1):
            try:
                # Measure this frequency
                measurement = self.measure_single_frequency(freq)
                self.results.append(measurement)
                
                # Progress update
                power = measurement['power_dbm']
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                eta = (total_points - i) / rate if rate > 0 else 0
                
                print(f"[{i:3d}/{total_points}] "
                      f"{freq:7.2f} MHz: {power:7.2f} dBm  "
                      f"({rate:.1f} pt/s, ETA: {eta:.0f}s)")
                
            except Exception as e:
                print(f"ERROR at {freq:.2f} MHz: {e}")
                # Record error but continue
                self.results.append({
                    'timestamp': datetime.now().isoformat(),
                    'frequency_mhz': freq,
                    'power_dbm': np.nan,
                    'lo_power_setting': self.config['lo_power'],
                    'error': str(e)
                })
        
        elapsed_total = time.time() - start_time
        print(f"\nSweep completed in {elapsed_total:.1f} seconds")
        print(f"Average rate: {total_points / elapsed_total:.2f} points/second")
    
    def save_results(self, output_path: Optional[Path] = None) -> Path:
        """
        Save results to file
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to saved file
        """
        if not self.results:
            raise ValueError("No results to save")
        
        # Generate output filename if not provided
        if output_path is None:
            timestamp = datetime.now().strftime(self.config['timestamp_format'])
            output_dir = Path(self.config['output_dir'])
            output_dir.mkdir(exist_ok=True)
            
            lo_power = self.config['lo_power']
            filename = f"lo_power_sweep_{timestamp}_{lo_power:+d}dBm.csv"
            output_path = output_dir / filename
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to DataFrame
        df = pd.DataFrame(self.results)
        
        # Save based on format
        if output_path.suffix.lower() == '.csv':
            df.to_csv(output_path, index=False)
            print(f"\nResults saved to: {output_path}")
        elif output_path.suffix.lower() in ['.fits', '.fit']:
            try:
                from astropy.table import Table
                table = Table.from_pandas(df)
                table.write(output_path, format='fits', overwrite=True)
                print(f"\nResults saved to: {output_path}")
            except ImportError:
                print("ERROR: astropy not installed. Saving as CSV instead.")
                output_path = output_path.with_suffix('.csv')
                df.to_csv(output_path, index=False)
                print(f"Results saved to: {output_path}")
        else:
            df.to_csv(output_path, index=False)
            print(f"\nResults saved to: {output_path}")
        
        # Print statistics
        valid_powers = df['power_dbm'].dropna()
        if len(valid_powers) > 0:
            print(f"\nMeasurement Statistics:")
            print(f"  Valid measurements: {len(valid_powers)}/{len(df)}")
            print(f"  Power range: {valid_powers.min():.2f} to {valid_powers.max():.2f} dBm")
            print(f"  Mean power: {valid_powers.mean():.2f} dBm")
            print(f"  Std deviation: {valid_powers.std():.2f} dB")
        
        return output_path
    
    def cleanup(self) -> None:
        """Cleanup hardware connections"""
        print("\nCleaning up...")
        
        if self.arduino is not None:
            try:
                self.arduino.disconnect()
            except Exception as e:
                print(f"Warning during Arduino disconnect: {e}")
        
        if self.tinysa is not None:
            try:
                self.tinysa.disconnect()
            except Exception as e:
                print(f"Warning during tinySA disconnect: {e}")
    
    def run(self, output_path: Optional[Path] = None) -> Path:
        """
        Run complete measurement sequence
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to results file
        """
        try:
            self.setup()
            self.run_sweep()
            output_file = self.save_results(output_path)
            return output_file
        finally:
            self.cleanup()


def load_config(config_file: Optional[Path] = None) -> Dict:
    """Load configuration from file"""
    if config_file is None:
        config_file = Path(__file__).parent / 'config.yaml'
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Return defaults
        return {
            'arduino_port': '/dev/cu.usbserial-14110',
            'tinysa_port': 'auto',
            'freq_start': 900.0,
            'freq_stop': 960.0,
            'freq_step': 0.2,
            'lo_power': +5,
            'settling_time': 0.1,
            'measurement_time': 0.05,
            'span': 1.0,
            'rbw': 'auto',
            'averaging': 4,
            'attenuation': 'auto',
            'output_format': 'csv',
            'output_dir': 'results',
            'timestamp_format': '%Y%m%d_%H%M%S'
        }


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Automated LO power sweep measurement with tinySA Ultra',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic sweep with defaults from config.yaml:
  python lo_power_sweep.py
  
  # Specify ports explicitly:
  python lo_power_sweep.py --arduino /dev/cu.usbserial-14110 --tinysa auto
  
  # Custom frequency range:
  python lo_power_sweep.py --freq-start 920 --freq-stop 940 --freq-step 0.5
  
  # Dual power measurement:
  python lo_power_sweep.py --dual-power +5 -4
        """
    )
    
    # Hardware
    parser.add_argument('--arduino', type=str, help='Arduino serial port')
    parser.add_argument('--tinysa', type=str, help='tinySA serial port (or "auto")')
    parser.add_argument('--list-ports', action='store_true', 
                       help='List available serial ports and exit')
    
    # Frequency sweep
    parser.add_argument('--freq-start', type=float, help='Start frequency (MHz)')
    parser.add_argument('--freq-stop', type=float, help='Stop frequency (MHz)')
    parser.add_argument('--freq-step', type=float, help='Frequency step (MHz)')
    
    # Power settings
    parser.add_argument('--power', type=int, help='LO output power (dBm)')
    parser.add_argument('--dual-power', type=int, nargs=2, metavar=('P1', 'P2'),
                       help='Run two sweeps at different power levels')
    
    # Timing
    parser.add_argument('--settling-time', type=float, 
                       help='Settling time after frequency change (seconds)')
    
    # tinySA settings
    parser.add_argument('--span', type=float, help='Measurement span (MHz)')
    parser.add_argument('--averaging', type=int, choices=[1, 4, 16],
                       help='Number of averages')
    parser.add_argument('--rbw', help='Resolution bandwidth (kHz or "auto")')
    parser.add_argument('--attenuation', help='Input attenuation (dB or "auto")')
    
    # Output
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    parser.add_argument('--output-dir', type=str, help='Output directory')
    parser.add_argument('--config', type=str, help='Configuration file')
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # List ports and exit if requested
    if args.list_ports:
        print("Available Arduino-like ports:")
        ports = find_arduino_ports()
        if ports:
            for port in ports:
                print(f"  {port}")
        else:
            print("  (none found)")
        return 0
    
    # Load configuration
    config_file = Path(args.config) if args.config else None
    config = load_config(config_file)
    
    # Override with command-line arguments
    if args.arduino:
        config['arduino_port'] = args.arduino
    if args.tinysa:
        config['tinysa_port'] = args.tinysa
    if args.freq_start:
        config['freq_start'] = args.freq_start
    if args.freq_stop:
        config['freq_stop'] = args.freq_stop
    if args.freq_step:
        config['freq_step'] = args.freq_step
    if args.power:
        config['lo_power'] = args.power
    if args.settling_time:
        config['settling_time'] = args.settling_time
    if args.span:
        config['span'] = args.span
    if args.averaging:
        config['averaging'] = args.averaging
    if args.rbw:
        config['rbw'] = args.rbw if args.rbw == 'auto' else int(args.rbw)
    if args.attenuation:
        config['attenuation'] = args.attenuation if args.attenuation == 'auto' else int(args.attenuation)
    if args.output_dir:
        config['output_dir'] = args.output_dir
    
    # Handle dual power measurement
    if args.dual_power:
        print("Dual power measurement mode")
        power_levels = args.dual_power
        
        for power in power_levels:
            config['lo_power'] = power
            print(f"\n{'='*60}")
            print(f"Measurement at {power:+d} dBm")
            print(f"{'='*60}\n")
            
            sweep = LOPowerSweep(config)
            
            # Generate output path
            if args.output:
                base_path = Path(args.output)
                output_path = base_path.parent / f"{base_path.stem}_{power:+d}dBm{base_path.suffix}"
            else:
                output_path = None
            
            sweep.run(output_path)
    else:
        # Single power measurement
        sweep = LOPowerSweep(config)
        output_path = Path(args.output) if args.output else None
        sweep.run(output_path)
    
    print("\nAll measurements complete!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nMeasurement interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
