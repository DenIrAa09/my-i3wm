#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import json

def get_moosic_current():
    """ Geth the current moosic track """
    path = subprocess.check_output(["moosic", "current"])[0:-1]
    if not path:
        return "■"
    tags = subprocess.check_output(["lltag", "--show-tags=artist,title", path])
    try:
        tags = tags.decode()
    except UnicodeDecodeError:
        return "..."
    lines = tags.split('\n')
    artist = lines[1].split("=")[-1]
    title  = lines[2].split("=")[-1]
    return " ".join(["▶",artist,"-",title,"♬"])

def percent_to_float(string):
    """ Converts 037% to 0.37 """
    return float(string.strip('%'))/100

def float_to_bars(string, vertical=False):
    """ Converts 0.37 to bars like ▁ """
    if vertical:
        #      ₁₂₃₄₅₆₇₈
        chars="▁▂▃▄▅▆▇█"
    else:
        #      ₁₂₃₄₅₆₇₈
        chars="▏▎▍▌▋▊▉█"
    scale = 1/8
    real = float(string)
    for i in range(1,8):
        if (scale * i) >= real:
            return chars[i-1] # indexes 0-7
    return chars[-1]; # XXX load isn't a percentage

def print_line(message):
    """ Non-buffered printing to stdout. """
    sys.stdout.write(message + '\n')
    sys.stdout.flush()

def read_line():
    """ Interrupted respecting reader for stdin. """
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()

def skip_line():
    print_line(read_line())

if __name__ == '__main__':
    # Skip the first line which contains the version header.
    # The second line contains the start of the infinite array.
    skip_line()
    skip_line()

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)
        # insert information into the start of the json, but could be anywhere
        # CHANGE THIS LINE TO INSERT SOMETHING ELSE
        j.insert(0, {'full_text' : get_moosic_current(), 'name' : 'moosic'})
        # replace wifi %range and proc load to nice bars
        for item in j:
            if item["name"] == "load":
                parts = item["full_text"].split()
                parts[-1] = float_to_bars(parts[-1], True)
                item["full_text"] = " ".join(parts)
            if item["name"] == "wireless":
                parts = item["full_text"].split()
                for k, val in enumerate(parts):
                    if '%' in val:
                        parts[k] = float_to_bars(percent_to_float(val), True)
                item["full_text"] = " ".join(parts)
        # and echo back new encoded json
        print_line(prefix+json.dumps(j))