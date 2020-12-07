#!/usr/bin/env python3

import logging
from argparse import ArgumentParser
from datetime import timedelta, datetime, timezone
import json
from gen_tools import (format_timedelta,
        parse_timew_config,
        parse_ext_config,
        retrieve_records,
        get_report_bounds,
        parse_freetime,
        compute_tolog,
        )

logger = logging.getLogger(__name__)





def main():
    logging.basicConfig()
    config = parse_timew_config()
    if config['debug'] == 'on':
        logging.getLogger().setLevel(logging.DEBUG)
    free_days = parse_freetime()

    relevant_records = retrieve_records(config)
    day_sums = {}
    for record in relevant_records:
        logger.debug(f'Parsing {record}')
        start = record['start']
        stop = record['end']

        logger.debug(f'Looking at {start.date()}')

        diff = stop - start
        logger.debug(f'diff: {diff}')
        day_sums[start.date()] = day_sums.get(start.date(), timedelta()) + diff

    startdate, enddate = get_report_bounds(config)
    tolog = compute_tolog(startdate, enddate)
    
    logged_total = sum(day_sums.values(), start=timedelta())
    print(f'\nLogged {format_timedelta(logged_total)} of {format_timedelta(tolog)}')
    if tolog - logged_total > timedelta():
        print(f'You are missing {format_timedelta(tolog - logged_total)}')
    else:
        print(f'You have a credit of {format_timedelta(logged_total - tolog)}')
        
if __name__ == '__main__':
    main()
