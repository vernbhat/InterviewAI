import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
os.environ.setdefault("EXECUTOR", "local")
os.environ["INTERVIEWAI_NO_DOTENV"] = "1"  # never let a developer .env (API keys) change test behaviour
