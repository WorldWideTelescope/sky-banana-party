#! /usr/bin/env python
# Copyright 2019 Peter Williams
# Licensed under the MIT License

"""Validate the `config.json` file.

This script should be run locally before uploading a new version of the config
file -- it's just a safety check to make sure that we don't accidentally
upload something busted.

"""

# note: Python 2.x compat not tested
from __future__ import absolute_import, division, print_function

import io
import json
import os.path
import time


_frontend_dir = os.path.dirname(__file__)

def frontend_path(*args):
    return os.path.join(_frontend_dir, *args)


def die(fmt, *args):
    import sys

    if len(args):
        text = fmt % args
    else:
        text = str(fmt)

    print('error:', text, file=sys.stderr)
    sys.exit(1)


def main():
    # Maybe the biggest test: is it valid JSON?
    with io.open(frontend_path('config.json')) as f:
        config = json.load(f)

    ligo_mode = config.get('ligo_mode')
    if not isinstance(ligo_mode, str):
        die('ligo_mode should be a str')

    if ligo_mode == "off":
        ligo_turn_on_unix_ms = config.get('ligo_turn_on_unix_ms')
        if not isinstance(ligo_turn_on_unix_ms, int):
            die('if ligo_mode==off, ligo_turn_on_unix_ms should be an int')

        if ligo_turn_on_unix_ms < 1548258899000: # 2019 Jan 23 in Unix-time millisecs
            die('ligo_turn_on_unix_ms suspiciously small')

        if ligo_turn_on_unix_ms > 3294825889900: # 2119 Jan 23 or so
            die('ligo_turn_on_unix_ms suspiciously large')

        ligo_turn_on_html_frag = config.get('ligo_turn_on_html_frag')
        if not isinstance(ligo_turn_on_html_frag, str):
            die('if not ligo_running, ligo_turn_on_html_frag should be a str')
    else:
        die('unexpected value for ligo_mode: %r', ligo_mode)

    # If we made it here ...
    print('config looks OK')


if __name__ == '__main__':
    main()
