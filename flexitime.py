#!/usr/bin/env python3

import logging
#logging.basicConfig(level=logging.DEBUG)

from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone, date
import json
import os
from pprint import pprint
import re
import sys

logger = logging.getLogger(__name__)

def format_timedelta(delta):
    hours, rem = divmod(delta.total_seconds(), 3600)
    minutes = round(rem / 60, 0)
    return f'{int(hours):02}:{int(minutes):02}'

def get_script_path():
    return os.path.dirname(os.path.realpath(__file__))

def parse_ext_config():
    with open(f'{get_script_path()}/ft.conf', 'r') as conffile:
        return json.load(conffile)

def parse_timew_config():
    config = {}
    for line in sys.stdin:
        if not line.strip():
            break
        tokens = line.split(':', maxsplit=1)
        key = tokens[0]
        if key in ('temp.report.start', 'temp.report.end'):
            value = parse_timew_timestamp(tokens[1].strip())
        elif not tokens[1]:
            value = None
        else:
            value = tokens[1].strip()
        config[key] = value
    return config

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
    while current < (stop + timedelta(days=1 if inclusive else 0)):
        yield current
        current += timedelta(days=1)

def parse_timew_timestamp(string):
    if not string:
        return None
    else:
        dt = datetime.strptime(string, '%Y%m%dT%H%M%SZ')
        return dt.replace(tzinfo=timezone.utc)
    

def parse_record(obj):
    obj['start'] = parse_timew_timestamp(obj['start'])
    if 'end' in obj and obj['end']:
        obj['end'] = parse_timew_timestamp(obj['end'])
    else: 
        logger.debug(f'parsing empty end for record starting at {obj["start"]}')
        obj['end'] = datetime.now(tz=timezone.utc)
    return obj

def main():
    extconfig = parse_ext_config()
    config = parse_timew_config()
    time_records = json.load(sys.stdin, object_hook=parse_record)
    free_days = parse_freetime(config['temp.db'] + '/freedays.txt')

    relevant_records = filter(lambda x: (x['start'] >= config.get('temp.report.start', datetime.min)    # start date inside report date range
                                    or x['end'] <= config.get('temp.report.end', datetime.max)),        # end date inside report date range 
                                    time_records)

    day_sums = {}
    for record in relevant_records:
        logger.debug(f'Parsing {record}')
        start = record['start']
        stop = record['end']

        logger.debug(f'Looking at {start.date()}')

        diff = stop - start
        logger.debug(f'diff: {diff}')
        day_sums[start.date()] = day_sums.get(start.date(), timedelta()) + diff

    startdate = config.get('temp.report.start')
    enddate = config.get('temp.report.end') or datetime.now(tz=timezone.utc)

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
