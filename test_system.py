#!/usr/bin/env python3
"""
Quick Test Script for tinySA-LO Characterization System

This script performs basic connectivity tests for both Arduino and tinySA
to ensure everything is properly configured before running full sweeps.
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from arduino_controller import ArduinoLOController, find_arduino_ports
from tinysa_controller import TinySAController


def test_arduino(port: str) -> bool:
    """Test Arduino connectivity and basic commands"""
    print("\n" + "="*60)
    print("Testing Arduino Controller")
    print("="*60)
    
    try:
        print(f"Connecting to Arduino at {port}...")
        lo = ArduinoLOController(port)
        lo.connect()
        
        print(f"✓ Connected successfully")
        print(f"  Current frequency: {lo.get_frequency()} MHz")
        print(f"  Current power: {lo.get_power()} dBm")
        
        # Test frequency command
        test_freq = 925.0
        print(f"\nTesting frequency command: {test_freq} MHz...")
        if lo.set_frequency(test_freq):
            print(f"✓ Frequency set successfully")
            time.sleep(0.5)
        else:
            print(f"✗ Failed to set frequency")
            return False
        
        # Test power command
        test_power = +5
        print(f"\nTesting power command: {test_power} dBm...")
        if lo.set_power(test_power):
            print(f"✓ Power set successfully")
            time.sleep(0.5)
        else:
            print(f"✗ Failed to set power")
            return False
        
        lo.disconnect()
        print("\n✓ Arduino test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Arduino test FAILED: {e}")
        return False


def test_tinysa(port: str = 'auto') -> bool:
    """Test tinySA connectivity and basic measurements"""
    print("\n" + "="*60)
    print("Testing tinySA Controller")
    print("="*60)
    
    try:
        print(f"Connecting to tinySA...")
        tsa = TinySAController(port=port)
        tsa.connect()
        
        print(f"✓ Connected successfully")
        
        # Test single frequency measurement
        test_freq = 925.0
        print(f"\nTesting measurement at {test_freq} MHz...")
        power = tsa.measure_power_at_frequency(
            freq_mhz=test_freq,
            span_mhz=2.0,
            averaging=1  # Quick test
        )
        print(f"✓ Measured power: {power:.2f} dBm")
        
        tsa.disconnect()
        print("\n✓ tinySA test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ tinySA test FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("tinySA-LO Characterization System - Quick Test")
    print("="*60)
    
    # Find Arduino ports
    print("\nSearching for Arduino...")
    arduino_ports = find_arduino_ports()
    
    if not arduino_ports:
        print("✗ No Arduino-like devices found!")
        print("\nAvailable ports:")
        import serial.tools.list_ports
        for port in serial.tools.list_ports.comports():
            print(f"  {port.device}: {port.description}")
        print("\nPlease check:")
        print("  1. Arduino is connected via USB")
        print("  2. Arduino has ManualControl.ino sketch uploaded")
        print("  3. Correct USB driver is installed")
        return 1
    
    print(f"Found potential Arduino ports: {arduino_ports}")
    
    # Use first port
    arduino_port = arduino_ports[0]
    if len(arduino_ports) > 1:
        print(f"\nMultiple ports found. Using first: {arduino_port}")
        print(f"If this is wrong, specify port with: --arduino <port>")
    
    # Test Arduino
    arduino_ok = test_arduino(arduino_port)
    
    # Test tinySA
    tinysa_ok = test_tinysa('auto')
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Arduino:  {'✓ PASS' if arduino_ok else '✗ FAIL'}")
    print(f"tinySA:   {'✓ PASS' if tinysa_ok else '✗ FAIL'}")
    
    if arduino_ok and tinysa_ok:
        print("\n✓ All tests PASSED - System ready for measurements!")
        print("\nNext steps:")
        print("  1. Connect RF cable from LO to tinySA input")
        print("  2. Run: python lo_power_sweep.py")
        return 0
    else:
        print("\n✗ Some tests FAILED - Please fix issues before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
