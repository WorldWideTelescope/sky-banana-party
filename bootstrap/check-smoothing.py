#! /usr/bin/env python
# Copyright 2019 Peter Williams
# Licensed under the MIT License

"""Plot smoothed contours to see how well our algorithm works.

This uses `omegaplot`, a plotting package used by Peter Williams and pretty
much nobody else. Sorry.

"""

# note: Python 2.x compat not tested
from __future__ import absolute_import, division, print_function

import omega as om
import numpy as np

import postprocess


def main():
    pg = om.makeDisplayPager()

    for ident, flitem, geojson in postprocess.get_events():
        for ftnum, feature in enumerate(geojson['features'][0]['geometry']['coordinates']):
            x_orig = np.array([t[0] for t in feature])
            y_orig = np.array([t[1] for t in feature])
            area, x, y = postprocess.fix_polygon_handedness(x_orig, y_orig)

            if area < postprocess.AREA_CUTOFF_68:
                print('skipping %s+%d: A=%.1f' % (ident, ftnum + 1, area))
                continue

            x, y = postprocess.smooth_polygon(x, y)

            p = om.quickXY(x_orig, y_orig, 'Original %s+%d: A=%.1f' % (ident, ftnum + 1, area))
            p.addXY(x, y, 'Smoothed')
            pg.send(p)

    pg.done()


if __name__ == '__main__':
    main()
