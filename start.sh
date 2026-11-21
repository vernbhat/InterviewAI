#!/usr/bin/env bash
# One-command launcher for InterviewAI (macOS and Linux).
#   ./start.sh            set up everything that is missing, then open http://localhost:8000
#   ./start.sh --key      (re)enter your Groq API key
# Safe to run again: each step is skipped when it is already done.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
PORT="${PORT:-8000}"

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!!\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31mxx\033[0m %s\n' "$*" >&2; exit 1; }

IS_MAC=0; [[ "$(uname -s)" == "Darwin" ]] && IS_MAC=1
if [[ $IS_MAC == 1 && -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
if [[ $IS_MAC == 1 && -x /usr/local/bin/brew ]]; then eval "$(/usr/local/bin/brew shellenv)"; fi

brew_need() {  # brew_need <formula>
  if [[ $IS_MAC == 1 ]]; then
    command -v brew >/dev/null || die "Homebrew is missing. Install it from https://brew.sh (one command), then run ./start.sh again."
    say "Installing $1 with Homebrew (one time only)..."
    brew install "$1"
  else
    die "Please install $1 with your package manager, then run ./start.sh again."
  fi
}

# ---------------------------------------------------------------- Python 3.11+
pick_python() {
  for c in python3.13 python3.12 python3.11 python3; do
    if command -v "$c" >/dev/null && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
      echo "$c"; return
    fi
  done
}
PY="$(pick_python || true)"
if [[ -z "$PY" ]]; then brew_need python@3.12; PY="$(pick_python)"; fi
[[ -n "$PY" ]] || die "Python 3.11 or newer is required."

# ---------------------------------------------------------------- Node 20+
node_ok() { command -v node >/dev/null && node -e 'process.exit(+process.versions.node.split(".")[0] >= 20 ? 0 : 1)'; }
node_ok || brew_need node
node_ok || die "Node.js 20 or newer is required."

# ---------------------------------------------------------------- GCC (C++ problems)
have_gcc() {
  if [[ $IS_MAC == 1 ]]; then compgen -c | grep -qE '^g\+\+-[0-9]+$'; else command -v g++ >/dev/null; fi
}
if ! have_gcc; then
  if [[ $IS_MAC == 1 ]]; then brew_need gcc; else warn "g++ not found: C++ problems will not run (Python still works)."; fi
fi

# ---------------------------------------------------------------- .env and Groq key
if [[ ! -f .env ]]; then cp .env.example .env; say "Created .env from .env.example"; fi
current_key="$(grep -E '^GROQ_API_KEY=' .env | head -1 | cut -d= -f2- || true)"
if [[ -z "$current_key" || "${1:-}" == "--key" ]]; then
  echo
  echo "Paste your Groq API key (starts with gsk_) and press Enter."
  echo "Get one free at https://console.groq.com/keys. Press Enter without typing to skip (offline mode)."
  read -r -s -p "Groq key: " new_key; echo
  if [[ -n "$new_key" ]]; then
    GROQ_KEY="$new_key" "$PY" - <<'PYEOF'
import os, re
p = ".env"; key = os.environ["GROQ_KEY"].strip()
s = open(p).read()
s = re.sub(r"(?m)^GROQ_API_KEY=.*$", "GROQ_API_KEY=" + key, s) if re.search(r"(?m)^GROQ_API_KEY=", s) else s + "\nGROQ_API_KEY=" + key + "\n"
open(p, "w").write(s)
PYEOF
    say "Saved the key to .env (this file is git-ignored, so it never gets committed)."
  else
    warn "No key entered: the interviewer will use the offline script. Run ./start.sh --key later to add one."
  fi
fi

# ---------------------------------------------------------------- Python deps
if [[ ! -x .venv/bin/python ]]; then say "Creating Python environment (.venv)..."; "$PY" -m venv .venv; fi
REQ_HASH="$("$PY" -c 'import hashlib;print(hashlib.sha1(open("services/ai/requirements.txt","rb").read()).hexdigest()[:12])')"
if [[ "$(cat .venv/.req-hash 2>/dev/null || true)" != "$REQ_HASH" ]]; then
  say "Installing Python packages..."
  .venv/bin/python -m pip install -q --upgrade pip
  .venv/bin/python -m pip install -q -r services/ai/requirements.txt
  echo "$REQ_HASH" > .venv/.req-hash
fi

# ---------------------------------------------------------------- Web app build
if [[ ! -d node_modules ]] || [[ package-lock.json -nt node_modules ]]; then
  say "Installing web packages (first run takes a minute)..."
  npm install --no-audit --no-fund --loglevel=error
  touch node_modules
fi
DIST=apps/web/dist/index.html
if [[ ! -f "$DIST" ]] || [[ -n "$(find apps/web/src apps/web/index.html apps/web/vite.config.ts -newer "$DIST" 2>/dev/null | head -1)" ]]; then
  say "Building the web app..."
  npm run build --silent >/dev/null
fi

# ---------------------------------------------------------------- Run
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  die "Port $PORT is already in use (is InterviewAI already running?). Close it, or run: PORT=8001 ./start.sh"
fi
URL="http://localhost:$PORT"
say "Starting InterviewAI at $URL  (press Ctrl+C to stop)"
( sleep 2; if [[ $IS_MAC == 1 ]]; then open "$URL"; elif command -v xdg-open >/dev/null; then xdg-open "$URL" >/dev/null 2>&1 || true; fi ) &
cd services/ai
exec "$ROOT/.venv/bin/python" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT"
