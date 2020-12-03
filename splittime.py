#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

from datetime import timedelta
import json
import re
from gen_tools import (parse_ext_config,
        parse_timew_config,
        retrieve_records,
        parse_freetime,
        day_range,
        get_report_bounds,
        compute_tolog,
        )

def convert_time(timestr: str) -> timedelta:
    _timere = re.compile('(?P<hours>[0-9]*):(?P<minutes>[0-9]{2})')
    timematch = _timere.match(timestr)
    return timedelta(hours=int(timematch.group('hours')), minutes=int(timematch.group('minutes')))

def timedelta_to_print(td: timedelta) -> str:
    minutes = int(td.total_seconds() / 60 % 60)
    hours = int(td.total_seconds() / 3600)
    return f'{hours}:{minutes:02d}'

def main():
    logging.basicConfig()

    extconfig = parse_ext_config('st.conf')
    config = parse_timew_config()
    if config['debug'] == 'on':
        logging.getLogger().setLevel(logging.DEBUG)

    if 'tolog_tol' in config:
        tolog_tol = convert_time(config['tolog_tol'])
    else:
        tolog_tol = timedelta(hours=8)


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

    abw_time = timedelta()
    if 'tolog' in config:
        # Check if the number of days worked matches tolog, more or less
        startdate, enddate = get_report_bounds(config)
        comp_tolog = compute_tolog(startdate, enddate)
        tolog = convert_time(config['tolog'])
        logger.debug(f'computed time to log to {comp_tolog}, passed in was {config["tolog"]}')
        abw_time = abs(comp_tolog - tolog)
        if abw_time > tolog_tol:
            logger.warning(f'difference between computed, {timedelta_to_print(comp_tolog)}, and passed-in, {timedelta_to_print(tolog)}, tolog times exceeds tolerance {timedelta_to_print(tolog_tol)}')

            relto = comp_tolog
        else:
            relto = tolog
    else:
        relto = total_recorded

    tolog = {}
    for name, time in project_times.items():
        newtime = time/(project_sum) * relto
        hours, remainder = divmod(newtime.total_seconds(), 3600)
        minutes = remainder / 60
        tolog[name] = {'hours': int(hours), 'minutes': int(minutes)}

    if abw_time:
        tolog['abwesend'] = {
                'hours': int(abw_time.total_seconds() / 3600), 
                'minutes': int(abw_time.total_seconds() / 60 % 60)
        }

    print(json.dumps(tolog))
        



if __name__ == '__main__':
    main()
