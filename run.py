import uvicorn
import sys
from pathlib import Path

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Excel Data Processing Assistant Web Application...")
    print("Open http://127.0.0.1:8000 in your browser.")
    print("=" * 60)
    uvicorn.run("src.ui.server:app", host="127.0.0.1", port=8000, reload=False)
