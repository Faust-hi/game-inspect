"""Serve the production build against a disposable database for browser tests."""
import os
import tempfile
import sys
from pathlib import Path

import uvicorn


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    with tempfile.TemporaryDirectory(prefix="game-inspect-e2e-") as directory:
        os.environ["DATABASE_URL"] = "sqlite:///" + (Path(directory) / "e2e.db").as_posix()
        os.environ["AUTO_SEED"] = "true"
        uvicorn.run("app.main:app", host="127.0.0.1", port=8769)


if __name__ == "__main__":
    main()
