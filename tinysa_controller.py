"""
tinySA Ultra Spectrum Analyzer Controller

Provides a Python interface for measuring peak power at specific frequencies
using the tinySA Ultra spectrum analyzer.
"""

import time
import numpy as np
from typing import Optional, Tuple, List
from tsapython import tinySA


class TinySAController:
    """Controller for tinySA Ultra spectrum analyzer"""
    
    def __init__(self, port: Optional[str] = None, verbose: bool = False):
        """
        Initialize tinySA controller
        
        Args:
            port: Serial port for tinySA (None for auto-detect)
            verbose: Enable verbose output from tinySA library
        """
        self.port = port
        self.tsa = tinySA()
        self.tsa.verboseEnabled = verbose
        self.connected = False
        
    def connect(self) -> None:
        """Connect to tinySA device"""
        if self.connected:
            print("Already connected to tinySA")
            return
        
        try:
            if self.port is None or self.port.lower() == 'auto':
                print("Auto-detecting tinySA...")
                self.tsa.autoconnect()
            else:
                print(f"Connecting to tinySA at {self.port}...")
                self.tsa.connect(self.port)
            
            self.connected = True
            
            # Get device info
            info = self.tsa.info()
            print(f"Connected to tinySA")
            print(f"Device info: {info.decode('utf-8').strip()}")
            
            # Configure for spectrum analyzer mode
            self._configure_sa_mode()
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to tinySA: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from tinySA"""
        if self.connected:
            try:
                self.tsa.resume()  # Resume normal operation
                self.tsa.disconnect()
                self.connected = False
                print("Disconnected from tinySA")
            except Exception as e:
                print(f"Warning during disconnect: {e}")
    
    def _configure_sa_mode(self) -> None:
        """Configure tinySA for spectrum analyzer measurements"""
        # Set to low input mode (for RF measurements)
        self.tsa.mode("low", "input")
        
        # Set automatic gain control
        self.tsa.agc("auto")
        
        # Set automatic attenuation
        self.tsa.attenuate("auto")
        
        # Set automatic RBW
        self.tsa.rbw("auto")
        
        print("tinySA configured for spectrum analyzer mode")
    
    def measure_peak_power(
        self,
        center_freq_mhz: float,
        span_mhz: float = 1.0,
        num_points: int = 101,
        averaging: int = 1
    ) -> Tuple[float, float]:
        """
        Measure peak power at a specific frequency
        
        Args:
            center_freq_mhz: Center frequency in MHz
            span_mhz: Frequency span in MHz
            num_points: Number of measurement points
            averaging: Number of averages (1, 4, or 16)
            
        Returns:
            Tuple of (peak_power_dbm, peak_frequency_mhz)
        """
        if not self.connected:
            raise ConnectionError("Not connected to tinySA")
        
        # Convert to Hz
        center_freq_hz = int(center_freq_mhz * 1e6)
        span_hz = int(span_mhz * 1e6)
        
        # Calculate start and stop
        start_hz = int(center_freq_hz - span_hz / 2)
        stop_hz = int(center_freq_hz + span_hz / 2)
        
        # Set averaging mode
        if averaging == 4:
            self.tsa.calc("aver4")
        elif averaging == 16:
            self.tsa.calc("aver16")
        else:
            self.tsa.calc("off")
        
        # Pause sweep for measurement
        self.tsa.pause()
        
        # Perform scan
        try:
            # Get frequency array
            freq_data = self.tsa.hop(start_hz, stop_hz, num_points, 1)
            freq_values = self._parse_data(freq_data)
            
            # Get power measurements
            power_data = self.tsa.hop(start_hz, stop_hz, num_points, 2)
            power_values = self._parse_data(power_data)
            
            # Resume sweep
            self.tsa.resume()
            
            # Find peak
            if len(power_values) > 0:
                peak_idx = np.argmax(power_values)
                peak_power = power_values[peak_idx]
                peak_freq = freq_values[peak_idx] / 1e6  # Convert to MHz
                
                return (peak_power, peak_freq)
            else:
                raise ValueError("No data received from tinySA")
                
        except Exception as e:
            self.tsa.resume()
            raise RuntimeError(f"Measurement failed: {e}")
    
    def measure_power_at_frequency(
        self,
        freq_mhz: float,
        span_mhz: float = 0.5,
        averaging: int = 4
    ) -> float:
        """
        Measure peak power near a specific frequency (simplified interface)
        
        Args:
            freq_mhz: Target frequency in MHz
            span_mhz: Measurement span around target
            averaging: Number of averages
            
        Returns:
            Peak power in dBm
        """
        peak_power, peak_freq = self.measure_peak_power(
            center_freq_mhz=freq_mhz,
            span_mhz=span_mhz,
            num_points=51,  # Smaller number for faster measurements
            averaging=averaging
        )
        
        return peak_power
    
    def _parse_data(self, data_bytes: bytearray) -> np.ndarray:
        """
        Parse measurement data from tinySA
        
        Args:
            data_bytes: Raw data from tinySA
            
        Returns:
            Numpy array of parsed values
        """
        try:
            data_str = data_bytes.decode('utf-8')
            values = [float(x.strip()) for x in data_str.split() if x.strip()]
            return np.array(values)
        except Exception as e:
            raise ValueError(f"Failed to parse tinySA data: {e}")
    
    def set_attenuation(self, attenuation_db: int) -> None:
        """
        Set input attenuation
        
        Args:
            attenuation_db: Attenuation in dB (0-31 or 'auto')
        """
        if attenuation_db == 'auto':
            self.tsa.attenuate("auto")
        else:
            self.tsa.attenuate(attenuation_db)
    
    def set_rbw(self, rbw_khz: int) -> None:
        """
        Set resolution bandwidth
        
        Args:
            rbw_khz: RBW in kHz ('auto' or value)
        """
        if rbw_khz == 'auto':
            self.tsa.rbw("auto")
        else:
            self.tsa.rbw(rbw_khz)
    
    def quick_scan(
        self,
        start_mhz: float,
        stop_mhz: float,
        num_points: int = 450
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform a quick scan across frequency range
        
        Args:
            start_mhz: Start frequency in MHz
            stop_mhz: Stop frequency in MHz
            num_points: Number of points
            
        Returns:
            Tuple of (frequencies_mhz, powers_dbm)
        """
        if not self.connected:
            raise ConnectionError("Not connected to tinySA")
        
        start_hz = int(start_mhz * 1e6)
        stop_hz = int(stop_mhz * 1e6)
        
        self.tsa.pause()
        
        try:
            # Get data
            freq_data = self.tsa.scan(start_hz, stop_hz, num_points, 1)
            power_data = self.tsa.scan(start_hz, stop_hz, num_points, 2)
            
            self.tsa.resume()
            
            freqs = self._parse_data(freq_data) / 1e6  # Convert to MHz
            powers = self._parse_data(power_data)
            
            return (freqs, powers)
            
        except Exception as e:
            self.tsa.resume()
            raise RuntimeError(f"Quick scan failed: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False


if __name__ == "__main__":
    """Test script for tinySA controller"""
    import sys
    
    print("Testing tinySA Controller...")
    
    try:
        with TinySAController(port='auto', verbose=True) as tsa:
            # Test measurement at 925 MHz
            test_freq = 925.0
            print(f"\nMeasuring power at {test_freq} MHz...")
            
            power = tsa.measure_power_at_frequency(
                freq_mhz=test_freq,
                span_mhz=2.0,
                averaging=4
            )
            
            print(f"Peak power: {power:.2f} dBm")
            
            # Test quick scan
            print(f"\nPerforming quick scan from 920 to 930 MHz...")
            freqs, powers = tsa.quick_scan(920.0, 930.0, num_points=101)
            
            print(f"Scanned {len(freqs)} points")
            print(f"Frequency range: {freqs[0]:.2f} - {freqs[-1]:.2f} MHz")
            print(f"Power range: {powers.min():.2f} - {powers.max():.2f} dBm")
            
            print("\nTest complete!")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
