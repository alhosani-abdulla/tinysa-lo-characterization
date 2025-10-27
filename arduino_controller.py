"""
Arduino/ADF4351 Local Oscillator Controller

Provides a Python interface to control the ADF4351-based Local Oscillator
via serial communication with Arduino running ManualControl.ino sketch.
"""

import serial
import time
import re
from typing import Optional, Tuple


class ArduinoLOController:
    """Controller for Arduino-based ADF4351 Local Oscillator"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0):
        """
        Initialize Arduino LO controller
        
        Args:
            port: Serial port (e.g., '/dev/cu.usbserial-14110')
            baudrate: Serial baud rate (default: 115200)
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.current_freq: Optional[float] = None
        self.current_power: Optional[int] = None
        
    def connect(self) -> None:
        """Open serial connection to Arduino"""
        if self.ser is not None and self.ser.is_open:
            print(f"Already connected to {self.port}")
            return
            
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            # Wait for Arduino to reset after serial connection
            time.sleep(2.0)
            # Flush any startup messages
            self._flush_input()
            print(f"Connected to Arduino at {self.port}")
            
            # Query initial status
            self._get_status()
            
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to Arduino at {self.port}: {e}")
    
    def disconnect(self) -> None:
        """Close serial connection"""
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
            print(f"Disconnected from {self.port}")
    
    def _flush_input(self) -> None:
        """Flush input buffer"""
        if self.ser is not None:
            time.sleep(0.1)
            self.ser.reset_input_buffer()
    
    def _send_command(self, command: str) -> str:
        """
        Send command to Arduino and return response
        
        Args:
            command: Command string (without newline)
            
        Returns:
            Response from Arduino
        """
        if self.ser is None or not self.ser.is_open:
            raise ConnectionError("Not connected to Arduino")
        
        # Send command
        cmd_bytes = (command + '\n').encode('utf-8')
        self.ser.write(cmd_bytes)
        
        # Read response (multiple lines until timeout)
        response_lines = []
        start_time = time.time()
        
        while (time.time() - start_time) < self.timeout:
            if self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        response_lines.append(line)
                except UnicodeDecodeError:
                    pass  # Skip malformed lines
            else:
                # No more data available
                if response_lines:
                    break
                time.sleep(0.01)
        
        return '\n'.join(response_lines)
    
    def _get_status(self) -> None:
        """Query and parse current status from Arduino"""
        response = self._send_command('s')
        
        # Parse frequency from response like "Freq: 900.0 MHz"
        freq_match = re.search(r'Freq:\s+([\d.]+)\s+MHz', response)
        if freq_match:
            self.current_freq = float(freq_match.group(1))
        
        # Parse power from response like "Power: +5 dBm"
        power_match = re.search(r'Power:\s+([+-]?\d+)\s+dBm', response)
        if power_match:
            self.current_power = int(power_match.group(1))
    
    def set_frequency(self, freq_mhz: float) -> bool:
        """
        Set LO frequency
        
        Args:
            freq_mhz: Frequency in MHz (e.g., 900.0)
            
        Returns:
            True if successful, False otherwise
        """
        command = f'f {freq_mhz:.3f}'
        response = self._send_command(command)
        
        # Check for success
        if 'MHz' in response or 'Prog:' in response:
            self.current_freq = freq_mhz
            return True
        elif 'ERR' in response:
            print(f"Error setting frequency: {response}")
            return False
        else:
            # Assume success if no error
            self.current_freq = freq_mhz
            return True
    
    def set_power(self, power_dbm: int) -> bool:
        """
        Set LO output power
        
        Args:
            power_dbm: Output power in dBm (typically -4, -1, +2, or +5)
            
        Returns:
            True if successful, False otherwise
        """
        command = f'p {power_dbm:+d}'
        response = self._send_command(command)
        
        # Check for success
        if 'dBm' in response or 'Power' in response:
            self.current_power = power_dbm
            return True
        elif 'ERR' in response:
            print(f"Error setting power: {response}")
            return False
        else:
            self.current_power = power_dbm
            return True
    
    def get_frequency(self) -> Optional[float]:
        """Get current frequency setting"""
        return self.current_freq
    
    def get_power(self) -> Optional[int]:
        """Get current power setting"""
        return self.current_power
    
    def reset_to_band_start(self) -> bool:
        """Reset to start of current band (command: r)"""
        response = self._send_command('r')
        self._get_status()  # Update current values
        return 'ERR' not in response
    
    def toggle_band(self) -> bool:
        """Toggle between Band A and Band B (command: a)"""
        response = self._send_command('a')
        self._get_status()  # Update current values
        return 'ERR' not in response
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False


def find_arduino_ports() -> list:
    """
    Find potential Arduino serial ports
    
    Returns:
        List of port names that might be Arduino devices
    """
    import serial.tools.list_ports
    
    ports = []
    for port in serial.tools.list_ports.comports():
        # Look for common Arduino identifiers
        if any(keyword in port.description.lower() for keyword in 
               ['arduino', 'ch340', 'cp2102', 'ftdi', 'usb serial']):
            ports.append(port.device)
    
    return ports


if __name__ == "__main__":
    """Test script for Arduino controller"""
    import sys
    
    # Find available ports
    ports = find_arduino_ports()
    if not ports:
        print("No Arduino-like devices found!")
        sys.exit(1)
    
    print(f"Found potential Arduino ports: {ports}")
    
    # Use first port or specify manually
    port = ports[0] if len(sys.argv) < 2 else sys.argv[1]
    
    print(f"\nTesting Arduino LO Controller on {port}...")
    
    try:
        with ArduinoLOController(port) as lo:
            print(f"Initial frequency: {lo.get_frequency()} MHz")
            print(f"Initial power: {lo.get_power()} dBm")
            
            # Test frequency setting
            print("\nSetting frequency to 925.0 MHz...")
            if lo.set_frequency(925.0):
                print(f"Success! Frequency is now {lo.get_frequency()} MHz")
            
            time.sleep(0.5)
            
            # Test power setting
            print("\nSetting power to -4 dBm...")
            if lo.set_power(-4):
                print(f"Success! Power is now {lo.get_power()} dBm")
            
            time.sleep(0.5)
            
            print("\nTest complete!")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
