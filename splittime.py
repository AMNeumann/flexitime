#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

from datetime import timedelta
import json
import re
from gen_tools import parse_ext_config, parse_timew_config, retrieve_records

def convert_time(timestr: str) -> timedelta:
    _timere = re.compile('(?P<hours>[0-9]*):(?P<minutes>[0-9]{2})')
    timematch = _timere.match(timestr)
    return timedelta(hours=int(timematch.group('hours')), minutes=int(timematch.group('minutes')))

def main():
    logging.basicConfig()

    extconfig = parse_ext_config('st.conf')
    config = parse_timew_config()
    if config['debug'] == 'on':
        logging.getLogger().setLevel(logging.DEBUG)

    relevant_records = retrieve_records(config)
    project_times = dict((pro, timedelta()) for pro in extconfig['projects'])
    total_recorded = timedelta()
    for record in relevant_records:
        logger.debug(f'Parsing {record}')
        diff = record['end'] - record['start']
        for tag in record['tags'].intersection(extconfig['projects']):
            logger.debug(f'Adding {diff} to {tag}')
            project_times[tag] += diff
        total_recorded += diff

    project_sum = sum(project_times.values(), start=timedelta())

    if 'tolog' in config:
        relto = convert_time(config['tolog'])
    else:
        relto = total_recorded

    tolog = {}
    for name, time in project_times.items():
        newtime = time/(project_sum) * relto
        hours, remainder = divmod(newtime.total_seconds(), 3600)
        minutes = remainder / 60
        tolog[name] = {'hours': int(hours), 'minutes': int(minutes)}

    print(json.dumps(tolog))
        



if __name__ == '__main__':
    main()
