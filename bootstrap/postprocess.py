#! /usr/bin/env python
# Copyright 2019 Peter Williams
# Licensed under the MIT License

"""Postprocess the GeoJSON files emitted by `ligo-skymap-contour` to tidy them
up for use on the web.

NOTE: when we start getting LIGO events this code might need to be folded into
the running web app.

"""

# note: Python 2.x compat not tested
from __future__ import absolute_import, division, print_function

import io
import json
import numpy as np
import os.path
import scipy.interpolate as si


def fix_polygon_handedness(x, y):
    """Make sure that the input polygon has its points listed in clockwise order,
    so that they render correctly in the UI.

    Algorithm from <https://stackoverflow.com/a/1165943/3760486>.

    X and Y are coordinates, here in decimal degrees. The polygon is closed,
    with `x[0] = x[-1]`. This code only tested for polygons without holes and
    I have trouble seeing how it would work on a polygon *with* a hole. It
    should work OK with nonconvex polygons, though.

    Returns a tuple `(x, y)`. This might just be the inputs, or it might be a
    view of them with reversed order.

    """
    signed_area = 0

    for i in range(len(x) - 1):
        j = i + 1
        signed_area += (x[j] - x[i]) * (y[j] + y[i])

    if signed_area < 0:
        x = x[::-1]
        y = y[::-1]

    return x, y


def smooth_polygon(x, y):
    """X and Y are coordinates, here in decimal degrees. The polygon is closed,
    with `x[0] = x[-1]`. This code only tested for polygons without holes and
    I have trouble seeing how it would work on a polygon *with* a hole. It
    should work OK with nonconvex polygons, though.

    Returns a list of points, each of which is a 2-tuple of `(x, y)` for a
    smoothed version of the input polygon -- this output is meant to be
    JSON-friendly.

    """
    # XXX chosen manually! The results of the spline fit can be very sensitive
    # to this value so I hope this choice works well for one-size-fits-all!
    smoothing = 5

    t = np.linspace(0., 1., len(x))
    tck_x = si.splrep(t, x, per=1, s=smoothing)
    tck_y = si.splrep(t, y, per=1, s=smoothing)

    # Create the same number of output points as input points -- seems like
    # the most robust approach? I'm not confident that we can generically
    # expect to be able to reduce the number, actually.
    x = si.splev(t, tck_x)
    y = si.splev(t, tck_y)

    # Output as a list-of-tuples.
    result = [None] * len(x)
    for i in range(len(x)):
        result[i] = (x[i], y[i])
    return result


def main():
    bootstrap_dir = os.path.dirname(__file__)
    def bpath(*args):
        return os.path.join(bootstrap_dir, *args)

    app_dir = bpath(os.pardir, 'app')

    # The timing information (PeakAmpGPS) is only available in filelist.json,
    # so we need to read that file and munge its data into the records that
    # we'll emit.
    with io.open(bpath('filelist.json')) as f:
        fldata = json.load(f)

    bootstrap_data = {}

    for filename in os.listdir(bootstrap_dir):
        if not filename.endswith('.json') or not filename.startswith('GW'):
            continue

        with io.open(bpath(filename)) as f:
            geojson = json.load(f)

        ident = filename.split('_')[0]
        flitem = fldata['data'][ident]

        result = dict(
            ident = ident,
            peak_gps = flitem['files']['PeakAmpGPS'],
        )
        bootstrap_data[ident] = result

        # NOTE: hardcoding that we extract only the 68% contours right now.
        # We structure the data to make it possible to attach metadata to
        # individual localization regions (e.g., a centroid)

        regions = []

        for feature in geojson['features'][0]['geometry']['coordinates']:
            x = np.array([t[0] for t in feature])
            y = np.array([t[1] for t in feature])

            # Make sure that the points are in clockwise order so that WWT
            # renders them correctly.
            x, y = fix_polygon_handedness(x, y)

            # Smooth the contours since they come out jagged on the healpix
            # grid used to compute the probabilities. The
            # `ligo-skymap-contour` program has various smoothing options but
            # in some fairly extensive experimentation I couldn't get them to
            # produce acceptable results.
            contour = smooth_polygon(x, y)

            regions.append({'contours': {'68': contour}})

        result['regions'] = regions

    with io.open(os.path.join(app_dir, 'bootstrap_data.json'), 'wt') as f:
        json.dump(bootstrap_data, f)


if __name__ == '__main__':
    main()
