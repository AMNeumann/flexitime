#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)
import requests
import datetime
import sys
from pprint import pprint

def main():
    logging.basicConfig()

    import argparse

    parser = argparse.ArgumentParser(description='Get german holidays and emit list of dates')
    parser.add_argument('-o', '--output', help='output filename. Contents will not be clobbered unless -c is also specified')
    parser.add_argument('-c', '--clobber', action='store_true', default=False, help='Clobber output file')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Make output verbose')
    parser.add_argument('-s', '--state', choices=['BW', 'BY', 'BE', 'BB', 'HB', 'HH', 'HE', 'MV', 'NI', 'NW', 'RP', 'SL', 'SN', 'ST', 'SH', 'TH'], default=None, help='State ("Bundesland")')
    parser.add_argument('-y', '--year', default=datetime.date.today().year)
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.debug('starting request')
    params={'nur_daten': 1, 'jahr': args.year}
    if args.state is not None:
        params['nur_land'] = args.state

    r = requests.get('https://feiertage-api.de/api/', params=params)

    if r.status_code != 200:
        logger.error(f'Could not fetch holidays, status code {r.status_code}')
        sys.exit(1)

    outdata = '\n'.join(h for h in r.json().values())
    if args.output:
        with open(args.output, 'w' if args.clobber else 'a') as ofp:
            ofp.write('\n')
            ofp.write(outdata)
    else:
        print(outdata)




if __name__ == '__main__':
    main()
