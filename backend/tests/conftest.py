import sys
from pathlib import Path

# Allow "from app.xxx import yyy" in tests run from backend/
sys.path.insert(0, str(Path(__file__).parent.parent))
