#!/usr/bin/env python3

from .timew_tools import parse_ext_config, retrieve_records

def convert_time(timestr: str) -> timedelta:
    timematch = _timere.match(timestr)
    return timedelta(hours=int(timematch.group('hours')), minutes=int(timematch.group('minutes')))

def main():
    import configargparse

    parser = configargparse.ArgParser(default_config_files=['~/.timewarrior/splittime.conf'], description='split time among projects')
    parser.add('-c', '--config', is_config_file=True, help='config file path')
    parser.add('tolog', type=convert_time, help='Total time to log in period. Format: hh:mm')
    parser.add('-f', '--fill', action='store_true', help='Fill time to log exactly')
    parser.add('-p', '--project', action='update', default=set, help='projects to split time to')
    parser.add('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logging.get_logger().setLevel(logging.DEBUG if args.debug else logging.WARNING)

    relevant_records = retrieve_records()
    project_times = dict((pro, TimeDelta()) for pro in args.project)
    total_sum = TimeDelta()
    for record in relevant_records:
        logger.debug(f'Parsing {record}')
        diff = record['stop'] - record['start']
        for tag in record['tags'].intersection(args.project):
            logger.debug(f'Adding {diff} to {tag}')
            project_times[tag] += diff

    project_sum = sum(project_times.values())


    tolog = {}
    for name, time in project_times:
        newtime = time/(project_sum) * args.tolog
        hours, remainder = divmod(newtime.total_seconds(), 3600)
        tolog[name] = {'hours': hours, 'minutes': minutes}

    print(json.dump(tolog))
        



if __name__ == '__main__':
    main()
