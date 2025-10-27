#!/usr/bin/env python3
"""
Simple LO Sweep Test

This script sweeps the Arduino/LO through frequencies so you can visually
observe the sweep on a spectrum analyzer (tinySA or other).

No automated measurements - just sends frequency commands to the Arduino
and you watch the spectrum analyzer display.
"""

import serial
import time
import sys
import argparse


def find_arduino_port():
    """Find potential Arduino serial ports"""
    import serial.tools.list_ports
    
    ports = []
    for port in serial.tools.list_ports.comports():
        if any(keyword in port.description.lower() for keyword in 
               ['arduino', 'ch340', 'cp2102', 'ftdi', 'usb serial']):
            ports.append(port.device)
    
    return ports


def sweep_lo(port, freq_start=900.0, freq_stop=960.0, freq_step=0.2, 
             power=+5, dwell_time=0.2):
    """
    Sweep LO through frequency range
    
    Args:
        port: Serial port for Arduino
        freq_start: Start frequency (MHz)
        freq_stop: Stop frequency (MHz)
        freq_step: Frequency step (MHz)
        power: Output power (dBm)
        dwell_time: Time to dwell at each frequency (seconds)
    """
    
    print("="*60)
    print("LO Sweep Test - Visual Verification")
    print("="*60)
    
    # Connect to Arduino
    print(f"\nConnecting to Arduino at {port}...")
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(2)  # Wait for Arduino reset
        ser.reset_input_buffer()
        print("✓ Connected")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return False
    
    try:
        # Set power level
        print(f"\nSetting power to {power:+d} dBm...")
        ser.write(f'p {power:+d}\n'.encode())
        time.sleep(0.5)
        
        # Calculate frequencies
        import numpy as np
        num_points = int((freq_stop - freq_start) / freq_step) + 1
        frequencies = np.linspace(freq_start, freq_stop, num_points)
        
        print(f"\nSweep Parameters:")
        print(f"  Range: {freq_start:.1f} - {freq_stop:.1f} MHz")
        print(f"  Step: {freq_step:.3f} MHz")
        print(f"  Points: {len(frequencies)}")
        print(f"  Dwell time: {dwell_time:.2f} seconds")
        print(f"  Total sweep time: {len(frequencies) * dwell_time:.1f} seconds")
        print()
        print("Watch your spectrum analyzer now!")
        print("Press Ctrl+C to stop\n")
        
        time.sleep(2)  # Give user time to prepare
        
        # Sweep continuously
        sweep_count = 0
        while True:
            sweep_count += 1
            print(f"Sweep #{sweep_count}")
            
            for i, freq in enumerate(frequencies):
                # Set frequency
                ser.write(f'f {freq:.3f}\n'.encode())
                
                # Progress indicator
                if i % 10 == 0:
                    print(f"  {freq:7.2f} MHz", end='\r')
                
                # Dwell at this frequency
                time.sleep(dwell_time)
            
            print(f"  {frequencies[-1]:7.2f} MHz (completed)")
    
    except KeyboardInterrupt:
        print("\n\nSweep stopped by user")
    
    finally:
        # Return to start frequency
        print(f"\nReturning to {freq_start:.1f} MHz...")
        ser.write(f'f {freq_start:.3f}\n'.encode())
        time.sleep(0.2)
        ser.close()
        print("Disconnected")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Simple LO sweep test for visual verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  # Auto-detect Arduino and sweep default band
  python test_lo_sweep.py
  
  # Specify port and custom range
  python test_lo_sweep.py --port /dev/cu.usbserial-14110 --start 920 --stop 940
  
  # Slower sweep for easier observation
  python test_lo_sweep.py --dwell 0.5
  
  # Quick sweep
  python test_lo_sweep.py --step 1.0 --dwell 0.1
        """
    )
    
    parser.add_argument('--port', help='Arduino serial port (auto-detect if not specified)')
    parser.add_argument('--start', type=float, default=900.0, help='Start frequency (MHz)')
    parser.add_argument('--stop', type=float, default=960.0, help='Stop frequency (MHz)')
    parser.add_argument('--step', type=float, default=0.2, help='Frequency step (MHz)')
    parser.add_argument('--power', type=int, default=+5, help='Output power (dBm)')
    parser.add_argument('--dwell', type=float, default=0.2, help='Dwell time per frequency (seconds)')
    parser.add_argument('--list-ports', action='store_true', help='List available ports and exit')
    
    args = parser.parse_args()
    
    # List ports if requested
    if args.list_ports:
        ports = find_arduino_port()
        print("Available Arduino-like ports:")
        if ports:
            for p in ports:
                print(f"  {p}")
        else:
            print("  (none found)")
        return 0
    
    # Find Arduino port
    if args.port:
        port = args.port
    else:
        ports = find_arduino_port()
        if not ports:
            print("ERROR: No Arduino found. Please specify --port")
            return 1
        port = ports[0]
        if len(ports) > 1:
            print(f"Multiple ports found. Using: {port}")
            print(f"Others: {ports[1:]}")
    
    # Run sweep
    success = sweep_lo(
        port=port,
        freq_start=args.start,
        freq_stop=args.stop,
        freq_step=args.step,
        power=args.power,
        dwell_time=args.dwell
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
