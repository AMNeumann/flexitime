import logging
logger = logging.getLogger('timew_tools')
import os.path
import json
import sys
from datetime import datetime, timedelta, timezone, date, MINYEAR, MAXYEAR

def format_timedelta(delta):
    hours, rem = divmod(delta.total_seconds(), 3600)
    minutes = round(rem / 60, 0)
    return f'{int(hours):02}:{int(minutes):02}'

def get_script_path():
    return os.path.dirname(os.path.realpath(__file__))

def parse_ext_config(configfile):
    with open(f'{get_script_path()}/{configfile}', 'r') as conffile:
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

def get_report_bounds(config):
    report_start = config.get('temp.report.start') or datetime.min.replace(tzinfo=timezone.utc)
    report_end = config.get('temp.report.end') or datetime.max.replace(tzinfo=timezone.utc)
    return (report_start, report_end)

def retrieve_records(config):
    time_records = json.load(sys.stdin, object_hook=parse_record)
    report_start, report_end = get_report_bounds(config)

    logger.debug(f'getting records from {report_start} to {report_end}')
    logger.debug(f'got {len(time_records)} records:')
    for record in time_records:
        logger.debug(f'record: {record}')

    relevant_records = filter(lambda x: (report_start < x['start']     # start date inside report date range
                                    or x['end'] < report_end),         # end date inside report date range 
                                    time_records)
    return relevant_records

if __name__ == '__main__':
    print('not intended to run on its own')
    sys.exit(0)
