# tinySA-LO Characterization Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   cd /Users/majhool/Projects/highz/tinysa-lo-characterization
   pip install -r requirements.txt
   ```

2. **Prepare Arduino:**
   - Open Arduino IDE
   - Load `ManualControl.ino` from `../adf4351-controller/examples/ManualControl/`
   - Select your Arduino board (e.g., Arduino Nano)
   - Select correct port (e.g., `/dev/cu.usbserial-14110`)
   - Upload sketch
   - Open Serial Monitor (115200 baud) and verify it's responding to commands

3. **Connect Hardware:**
   ```
   Arduino/LO ──[RF Cable]──> tinySA Ultra Input
       │                           │
       └──[USB]──> Computer <──[USB]┘
   ```

## Quick Test

Run the test script to verify everything works:

```bash
python test_system.py
```

This will:
- Find your Arduino automatically
- Test frequency and power commands
- Test tinySA connectivity and measurements
- Report if system is ready

## Running a Measurement

### Basic sweep (uses config.yaml defaults):
```bash
python lo_power_sweep.py
```

### Specify ports explicitly:
```bash
python lo_power_sweep.py \
    --arduino /dev/cu.usbserial-14110 \
    --tinysa auto
```

### Custom frequency range:
```bash
python lo_power_sweep.py \
    --freq-start 920 \
    --freq-stop 940 \
    --freq-step 0.5 \
    --output custom_sweep.csv
```

### Dual power calibration (like your filterbank setup):
```bash
python lo_power_sweep.py \
    --dual-power +5 -4 \
    --output-dir calibration_data/
```

This will create two files:
- `calibration_data/lo_power_sweep_TIMESTAMP_+5dBm.csv`
- `calibration_data/lo_power_sweep_TIMESTAMP_-4dBm.csv`

## Configuration

Edit `config.yaml` to set your default parameters:

```yaml
# Your Arduino port
arduino_port: /dev/cu.usbserial-14110

# Frequency sweep (matches your filter band)
freq_start: 900.0   # MHz
freq_stop: 960.0    # MHz
freq_step: 0.2      # MHz (301 points)

# LO power setting
lo_power: +5        # dBm

# Timing
settling_time: 0.1  # seconds after freq change

# tinySA settings
span: 1.0           # MHz
averaging: 4        # 1, 4, or 16
```

## Troubleshooting

### "No Arduino found"
```bash
# List all USB devices
ls /dev/cu.*

# If you see your device, specify it:
python lo_power_sweep.py --arduino /dev/cu.usbserial-XXXXX
```

### "tinySA not connecting"
```bash
# Install/update tinySA library
pip install --upgrade tsapython

# Test connection
python -c "from tsapython import tinySA; tsa = tinySA(); tsa.autoconnect(); print('OK')"
```

### Arduino not responding
1. Check baud rate is 115200
2. Verify ManualControl.ino is uploaded
3. Test with Arduino Serial Monitor first
4. Try unplugging/replugging USB

### Low power measurements
- Ensure RF cable is properly connected
- Check cable quality (use short, good quality cable)
- Verify tinySA input attenuation is appropriate
- Try manually: `tsa.set_attenuation(0)` for max sensitivity

## Output Format

CSV file with columns:
- `timestamp`: ISO 8601 timestamp
- `frequency_mhz`: Frequency in MHz
- `power_dbm`: Measured peak power in dBm
- `lo_power_setting`: LO output power setting

Example:
```csv
timestamp,frequency_mhz,power_dbm,lo_power_setting
2025-10-26T10:30:45.123,900.0,-12.34,+5
2025-10-26T10:30:45.234,900.2,-12.28,+5
```

## Expected Performance

- **Speed**: ~2-3 points per second (301 points in ~2-3 minutes)
- **Accuracy**: ±0.5 dB typical (depends on tinySA settings)
- **Frequency accuracy**: Limited by ADF4351 PLL lock (~kHz level)

## Next Steps

Once you have power sweep data:
1. Compare +5 dBm and -4 dBm measurements
2. Look for any frequency-dependent variations
3. Use data to calibrate your filterbank measurements
4. Plot results: `python plot_results.py results/sweep.csv`

## Help

```bash
# Show all options
python lo_power_sweep.py --help

# List available ports
python lo_power_sweep.py --list-ports
```
