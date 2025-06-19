# ------------------------------
# bin/repeater_route.py
# ------------------------------
#!/usr/bin/env python3

import sys, os
# ensure the 'src' directory is on sys.path so the package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from repeater_route.cli import main

if __name__ == '__main__':
    main()

