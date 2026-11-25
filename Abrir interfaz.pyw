"""Abre la ventana en Windows con doble clic."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "implementacion"))
from interfaz import main

if __name__ == "__main__":
    main()
