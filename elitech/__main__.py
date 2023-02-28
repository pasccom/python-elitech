try:
    from .src.main import main
except ImportError:
    from src.main import main

import sys

main(sys.argv[1:])
