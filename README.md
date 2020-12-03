# Timewarrior timekeeping plugins

This repository contains timewarrior plugins for managing logged times.

## splittime

This plugin splits the logged time up into times for projects. It uses the tags
on the entries to determine projects, the projects are configured in
~/.timewarrior/extensions/st.conf in json format:

    {
        "projects": ["foo", "bar"]
    }

It increases the times logged for each project such that if you sum them up,
the result is equal to the sum of all logged times. If you pass the
command-line option 'rc.tolog=158:00', it increases the project times such that
their sum is equal to the time given.

## flexitime

This plugin computes the time logged in relation to a time you configure in
~/.timewarrior/extensions/ft.conf in json format:

   {
       "times": [
           "7:36",
           "7:36",
           "7:36",
           "7:36",
           "7:36",
           "0:0",
           "0:0"
      ]
   }

Each field in the 'times' array indicates a weekday; the example configuration
is such that 7h36min are expected for each day monday through friday. The
report indicates the time logged, the expected time and the difference.

The plugin takes into account free days that you may have. To configure them,
use ~/.timewarrior/freedays.txt:

   # Format: Either single date or date range in the formats
   #   2020-09-01
   #   2020-09-01 - 2020-09-03
   # Comments can be marked with '#'
   #
   # Copy this file to your timewarrior db directory, usually ~/.timewarrior

## get_holidays

This stand-alone script fetches german bank holidays that can be put into
freedays.txt directly, i.e. the format matches.
