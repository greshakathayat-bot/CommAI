#!/usr/bin/env bash
# CommAi backend dev environment setup
# Run from the project root: bash backend/setup_dev.sh
set -e

cd "$(dirname "$0")"

echo ""
echo "=== CommAi Backend Setup ==="
echo ""

# ─── 1. Resolve Python 3.11+ ────────────────────────────────────────────────
PYTHON_BIN=""

# Activate Homebrew if available (covers Apple Silicon /opt/homebrew and Intel /usr/local)
for brew_prefix in /opt/homebrew /usr/local; do
  if [ -f "$brew_prefix/bin/brew" ]; then
    eval "$("$brew_prefix/bin/brew" shellenv)" 2>/dev/null || true
    break
  fi
done

# Check common binary names on PATH
for candidate in python3.13 python3.12 python3.11 python3.10; do
  if command -v "$candidate" &>/dev/null; then
    PYTHON_BIN="$candidate"
    break
  fi
done

# Check explicit Homebrew paths in case PATH isn't updated yet
if [ -z "$PYTHON_BIN" ]; then
  for brew_py in /opt/homebrew/bin/python3.11 /opt/homebrew/bin/python3.12 \
                 /usr/local/bin/python3.11 /usr/local/bin/python3.12; do
    if [ -x "$brew_py" ]; then
      PYTHON_BIN="$brew_py"
      break
    fi
  done
fi

# If still nothing, install via Homebrew (fast — downloads a pre-built bottle, ~seconds)
if [ -z "$PYTHON_BIN" ]; then
  if command -v brew &>/dev/null; then
    echo "Installing Python 3.11 via Homebrew (pre-built bottle)..."
    brew install python@3.11
    PYTHON_BIN="$(brew --prefix python@3.11)/bin/python3.11"
  else
    echo "ERROR: Python 3.10+ not found and Homebrew is not installed."
    echo "Install Homebrew first: https://brew.sh, then re-run this script."
    exit 1
  fi
fi

PYTHON_VERSION=$("$PYTHON_BIN" --version)
echo "✔  Using $PYTHON_VERSION at $PYTHON_BIN"

# ─── 2. Recreate venv with the correct Python ───────────────────────────────
if [ -d ".venv" ]; then
  echo "Removing old .venv..."
  rm -rf .venv
fi

echo "Creating virtual environment..."
"$PYTHON_BIN" -m venv .venv

# Activate
source .venv/bin/activate

# ─── 3. Upgrade pip & install dependencies ──────────────────────────────────
echo "Upgrading pip..."
pip install --upgrade pip -q

echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "✔  All dependencies installed."
echo ""

# ─── 4. Seed the database ───────────────────────────────────────────────────
if python -c "import app.data.seed" 2>/dev/null; then
  echo "Seeding database..."
  python -m app.data.seed
  echo "✔  Database seeded."
fi

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To start the dev server:"
echo "  source backend/.venv/bin/activate"
echo "  cd backend && uvicorn app.main:app --reload --port 8000"
echo ""
echo "Or just run:  bash backend/start.sh"
