#!/usr/bin/env python3

import logging
from argparse import ArgumentParser
from datetime import timedelta, datetime, timezone
import json
from pprint import pprint
import re
from gen_tools import format_timedelta, get_script_path, parse_timew_config, parse_ext_config, retrieve_records, get_report_bounds

logger = logging.getLogger(__name__)


def parse_freetime(filename):
    free_days = []
    with open(filename, 'r') as ifp:
        for line in ifp:
            logger.debug(line)
            if line.startswith('#'):
                continue
            datere = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
            rangere = re.compile(f'(?P<start>{datere})( - (?P<end>{datere}))?')
            m = re.match(rangere, line)

            if not m:
                raise Exception('no match')
            logger.debug(f'Matched date re with groups: {m.groups()}')

            start = date.fromisoformat(m.group('start'))
            end = date.fromisoformat(m.group('end')) if m.group('end') else start
            free_days.extend(day_range(start, end, True))

    logger.debug(f'free days: {free_days}')
    return free_days

def day_range(start, stop, inclusive=False):
    current = start
    maxdate = datetime.max.replace(tzinfo=timezone.utc)
    if maxdate - timedelta(days=1) <= stop:
        end = maxdate - timedelta(days=1)
    else:
        end = stop + timedelta(days=1 if inclusive else 0)
    while current < end:
        yield current
        current += timedelta(days=1)


def main():
    logging.basicConfig()
    extconfig = parse_ext_config('ft.conf')
    config = parse_timew_config()
    if config['debug'] == 'on':
        logging.getLogger().setLevel(logging.DEBUG)
    free_days = parse_freetime(config['temp.db'] + '/freedays.txt')

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

    tolog = timedelta()
    for day in day_range(startdate, enddate):
        if day.date() not in free_days:
            hours, minutes = extconfig['times'][day.weekday()].split(':')
            delta = timedelta(hours=int(hours), minutes=int(minutes))
            logger.debug(f'{day}: Adding {delta}')
            tolog += delta

    
    logged_total = sum(day_sums.values(), start=timedelta())
    print(f'\nLogged {format_timedelta(logged_total)} of {format_timedelta(tolog)}')
    if tolog - logged_total > timedelta():
        print(f'You are missing {format_timedelta(tolog - logged_total)}')
    else:
        print(f'You have a credit of {format_timedelta(logged_total - tolog)}')
        
if __name__ == '__main__':
    main()
