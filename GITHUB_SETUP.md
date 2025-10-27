# GitHub Repository Setup

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `tinysa-lo-characterization` (or your preferred name)
3. Description: "Automated power characterization system for ADF4351 LO using tinySA Ultra spectrum analyzer"
4. Choose: **Public** or **Private** (your choice)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Push to GitHub

After creating the repository on GitHub, run these commands:

```bash
cd /Users/majhool/Projects/highz/tinysa-lo-characterization

# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/tinysa-lo-characterization.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Clone on Your Other Laptop

On your other laptop:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/tinysa-lo-characterization.git
cd tinysa-lo-characterization

# Set up Python environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test the system
python test_system.py
```

## Project Status

✅ Git repository initialized
✅ Initial commit created
✅ All source files committed
✅ Virtual environment and cache files ignored
✅ Ready to push to GitHub

## What's Included

- `arduino_controller.py` - Serial interface to Arduino/ADF4351
- `tinysa_controller.py` - tinySA Ultra measurement wrapper
- `lo_power_sweep.py` - Main automated sweep script
- `test_lo_sweep.py` - Visual verification script (no measurements)
- `test_system.py` - Hardware connectivity test
- `plot_results.py` - Data visualization
- `examples.py` - Usage examples
- `config.yaml` - Configuration defaults
- `requirements.txt` - Python dependencies
- Complete documentation (README, QUICKSTART, INSTALL, PROJECT_SUMMARY)

## Notes

- The `venv/` directory is not included (each machine should create its own)
- The `results/` directory structure is preserved but data files are ignored
- Python 3.10+ required (3.11+ recommended)
