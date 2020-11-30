#!/bin/bash

install -D  -m 755 flexitime.py ~/.timewarrior/extensions/flexitime.py
[[ ! -f ~/.timewarrior/extensions/ft.conf ]] && install  -m 644 ft.conf ~/.timewarrior/extensions/ft.conf
[[ ! -f ~/.timewarrior/freedays.txt ]] && install  -m 644 freedays.txt ~/.timewarrior/freedays.txt
install -D  -m 755 splittime.py ~/.timewarrior/extensions/splittime.py
install -D  -m 755 gen_tools.py ~/.timewarrior/extensions/gen_tools.py
