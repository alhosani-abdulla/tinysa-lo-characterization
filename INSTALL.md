# Virtual Environment Setup for tinySA-LO Characterization

## Python Version Requirement

**This project requires Python 3.10 or higher** for the `tsapython` package.

Current system Python: 3.9.6 ❌ (too old)

## Installation Options

### Option 1: Install Python 3.10+ (Recommended)

#### Using Homebrew (macOS):
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11 (or 3.10, 3.12)
brew install python@3.11

# Verify installation
python3.11 --version
```

#### Using pyenv (Alternative):
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.0
pyenv local 3.11.0

# Verify
python --version
```

#### Then create virtual environment:
```bash
cd /Users/majhool/Projects/highz/tinysa-lo-characterization

# Remove old venv
rm -rf venv

# Create new venv with Python 3.10+
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 2: Install tsapython from GitHub (Workaround)

If you want to try with Python 3.9 (might work despite the requirement):

```bash
cd /Users/majhool/Projects/highz/tinysa-lo-characterization

# Activate existing venv
source venv/bin/activate

# Try installing from GitHub directly
pip install git+https://github.com/LC-Linkous/tinySA_python.git#subdirectory=tsapython

# Install other requirements
pip install pyserial numpy pandas pyyaml matplotlib
```

### Option 3: Use System Python with --user flag (Not recommended)

```bash
# Install globally with --user flag (no venv)
pip3 install --user -r requirements.txt
```

## Verification

After installation, test that everything works:

```bash
# Activate venv
source venv/bin/activate

# Check Python version
python --version  # Should be 3.10+

# Check tsapython installed
python -c "from tsapython import tinySA; print('tsapython OK')"

# Run system test
python test_system.py
```

## Current Status

```
✓ Virtual environment created: venv/
✓ pip upgraded to latest version
❌ tsapython installation failed (Python 3.9 < 3.10 requirement)
```

## Next Steps

1. **Install Python 3.10 or higher** (see Option 1 above)
2. **Recreate virtual environment** with new Python version
3. **Install requirements**: `pip install -r requirements.txt`
4. **Test system**: `python test_system.py`

## Notes

- The `tsapython` package requires Python >= 3.10 due to type hints and modern Python features
- Using a virtual environment is best practice to avoid conflicts with system packages
- All scripts in this project will work once tsapython is properly installed
