
#!/usr/bin/env python3
import os
import sys
# ensure project src directory is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from pprint import pprint

from repeaterbook import RepeaterBook

def main():
    # Ensure config values are set

    # Instantiate RepeaterBook client
    client = RepeaterBook()

    # CLI for state FIPS code
    parser = argparse.ArgumentParser(
        description='Query RepeaterBook export for a given state FIPS code.'
    )
    parser.add_argument(
        '-s', '--state',
        type=int,
        default=27,
        help='State FIPS code to query (default from config)'
    )
    args = parser.parse_args()
    state_id = args.state

    print(f'Querying RepeaterBook export for state FIPS {state_id}...')
    try:
        response = client.export(state_id)
    except Exception as e:
        sys.exit(f'API error: {e}')

    print('Full API response:')
    pprint(response)

if __name__ == '__main__':
    main()
