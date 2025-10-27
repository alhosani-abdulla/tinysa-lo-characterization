#!/usr/bin/env python3
"""
Example: Direct Usage of Controllers

This script demonstrates how to use the arduino_controller and tinysa_controller
modules directly for custom measurement workflows.
"""

import time
from arduino_controller import ArduinoLOController
from tinysa_controller import TinySAController


def example_single_measurement():
    """
    Example 1: Measure power at a single frequency
    """
    print("="*60)
    print("Example 1: Single Frequency Measurement")
    print("="*60)
    
    # Connect to Arduino
    with ArduinoLOController('/dev/cu.usbserial-14110') as arduino:
        # Connect to tinySA
        with TinySAController(port='auto') as tinysa:
            # Set frequency
            freq = 925.0  # MHz
            print(f"\nSetting LO to {freq} MHz...")
            arduino.set_frequency(freq)
            arduino.set_power(+5)
            
            # Wait for settling
            time.sleep(0.2)
            
            # Measure
            print(f"Measuring with tinySA...")
            power = tinysa.measure_power_at_frequency(
                freq_mhz=freq,
                span_mhz=1.0,
                averaging=4
            )
            
            print(f"\nResult: {power:.2f} dBm at {freq} MHz")


def example_quick_scan():
    """
    Example 2: Quick scan without changing LO
    """
    print("\n" + "="*60)
    print("Example 2: Quick Spectrum Scan")
    print("="*60)
    
    # Just use tinySA (LO already set to some frequency)
    with TinySAController(port='auto') as tinysa:
        # Scan a range
        print("\nScanning 920-930 MHz...")
        freqs, powers = tinysa.quick_scan(
            start_mhz=920.0,
            stop_mhz=930.0,
            num_points=101
        )
        
        # Find peak
        peak_idx = powers.argmax()
        peak_freq = freqs[peak_idx]
        peak_power = powers[peak_idx]
        
        print(f"\nPeak: {peak_power:.2f} dBm at {peak_freq:.2f} MHz")


def example_power_comparison():
    """
    Example 3: Compare two power levels
    """
    print("\n" + "="*60)
    print("Example 3: Power Level Comparison")
    print("="*60)
    
    freq = 930.0
    results = {}
    
    with ArduinoLOController('/dev/cu.usbserial-14110') as arduino:
        with TinySAController(port='auto') as tinysa:
            # Set frequency once
            arduino.set_frequency(freq)
            time.sleep(0.2)
            
            # Measure at +5 dBm
            print(f"\nMeasuring at +5 dBm...")
            arduino.set_power(+5)
            time.sleep(0.2)
            results['+5 dBm'] = tinysa.measure_power_at_frequency(freq)
            
            # Measure at -4 dBm
            print(f"Measuring at -4 dBm...")
            arduino.set_power(-4)
            time.sleep(0.2)
            results['-4 dBm'] = tinysa.measure_power_at_frequency(freq)
    
    # Compare
    print(f"\nResults at {freq} MHz:")
    for setting, power in results.items():
        print(f"  {setting}: {power:.2f} dBm")
    
    diff = results['+5 dBm'] - results['-4 dBm']
    print(f"\nPower difference: {diff:.2f} dB")


def example_manual_control():
    """
    Example 4: Low-level manual control
    """
    print("\n" + "="*60)
    print("Example 4: Manual Low-Level Control")
    print("="*60)
    
    # Create controller
    arduino = ArduinoLOController('/dev/cu.usbserial-14110')
    tinysa = TinySAController(port='auto')
    
    try:
        # Connect
        arduino.connect()
        tinysa.connect()
        
        # Direct tinySA commands (using tsapython library)
        print("\nSetting tinySA parameters directly...")
        tinysa.tsa.rbw(10)  # 10 kHz RBW
        tinysa.tsa.attenuate(0)  # No attenuation
        tinysa.tsa.calc("aver4")  # 4x averaging
        
        # Arduino commands
        print("Setting Arduino...")
        arduino.set_frequency(925.0)
        arduino.set_power(+5)
        
        time.sleep(0.3)
        
        # Manual measurement with peak finding
        print("Performing measurement...")
        peak_power, peak_freq = tinysa.measure_peak_power(
            center_freq_mhz=925.0,
            span_mhz=2.0,
            num_points=101,
            averaging=4
        )
        
        print(f"\nPeak: {peak_power:.2f} dBm at {peak_freq:.3f} MHz")
        
    finally:
        # Always cleanup
        arduino.disconnect()
        tinysa.disconnect()


def example_frequency_sweep():
    """
    Example 5: Mini frequency sweep
    """
    print("\n" + "="*60)
    print("Example 5: Mini Frequency Sweep")
    print("="*60)
    
    import numpy as np
    
    # Just a few points for demonstration
    frequencies = np.linspace(920.0, 930.0, 11)  # 11 points
    results = []
    
    with ArduinoLOController('/dev/cu.usbserial-14110') as arduino:
        with TinySAController(port='auto') as tinysa:
            arduino.set_power(+5)
            
            for freq in frequencies:
                print(f"Measuring {freq:.1f} MHz...", end=' ')
                
                # Set frequency
                arduino.set_frequency(freq)
                time.sleep(0.1)
                
                # Measure
                power = tinysa.measure_power_at_frequency(
                    freq_mhz=freq,
                    span_mhz=0.5,
                    averaging=1  # Quick measurement
                )
                
                results.append((freq, power))
                print(f"{power:.2f} dBm")
    
    # Show results
    print("\nSummary:")
    print("Freq (MHz)  Power (dBm)")
    print("-" * 25)
    for freq, power in results:
        print(f"{freq:8.1f}    {power:8.2f}")


if __name__ == "__main__":
    """
    Run examples
    
    Uncomment the examples you want to run.
    Make sure to update the Arduino port to match your system!
    """
    
    print("tinySA-LO Controller Examples")
    print("=" * 60)
    print("\nNOTE: Update Arduino port in code before running!")
    print("Current port: /dev/cu.usbserial-14110")
    print()
    
    try:
        # Run examples (uncomment the ones you want)
        
        example_single_measurement()
        # example_quick_scan()
        # example_power_comparison()
        # example_manual_control()
        # example_frequency_sweep()
        
        print("\n" + "="*60)
        print("Examples complete!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
