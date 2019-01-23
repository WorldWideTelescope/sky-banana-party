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


_bootstrap_dir = os.path.dirname(__file__)

def bpath(*args):
    return os.path.join(_bootstrap_dir, *args)


def fix_polygon_handedness(x, y):
    """Make sure that the input polygon has its points listed in clockwise order,
    so that they render correctly in the UI.

    Algorithm from <https://stackoverflow.com/a/1165943/3760486>.

    X and Y are 1D coordinate arrays, here in decimal degrees (though the
    units don't matter here). The polygon is closed, with `x[0] = x[-1]`. This
    code only tested for polygons without holes and I have trouble seeing how
    it would work on a polygon *with* a hole. It should work OK with nonconvex
    polygons, though.

    Returns a tuple `(signed_area, x, y)`. The 1D coordinate arrays x and y
    might just be the inputs, or they might be a view of them with reversed
    order.

    """
    signed_area = 0

    for i in range(len(x) - 1):
        j = i + 1
        # This should have a 0.5 prefactor, but we apply it only at the end
        # for efficiency.
        signed_area += (x[j] - x[i]) * (y[j] + y[i])

    if signed_area < 0:
        x = x[::-1]
        y = y[::-1]
        signed_area *= -1

    return 0.5 * signed_area, x, y


AREA_CUTOFF_68 = 10. # deg^2
"""The LIGO tool will sometimes return localization regions that are tiny --
just a single pixel, or a handful of pixels. It's probably worth looking into
where these are coming from, but for now they must be something spurious, so
we just ditch them.

"""

def smooth_polygon(x, y):
    """Smooth the polygon returned by the LIGO contour-finding algorithm.

    The LIGO contour-finder returns polygons that are chunky, presumably with
    the resolution of the HEALPix grid used to define the probability
    contours. The program has some smoothing options but none of them give
    acceptable results, in my opinion.

    X and Y are 1D coordinate arrays, here in decimal degrees. The polygon is
    closed, with `x[0] = x[-1]`. This code only tested for polygons without
    holes and I have trouble seeing how it would work on a polygon *with* a
    hole. It should work OK with nonconvex polygons, though.

    Returns a tuple of 1D coordinate arrays `(x, y)`.

    """
    # Figure out the typical spacing of the polygon points.

    dr = np.hypot(x[1:] - x[:-1], y[1:] - y[:-1])
    spacing = np.median(dr)

    # If we hardcode the spatial resolution that we expect from LIGO, we can
    # use the typical spacing to figure out how many polygon points we
    # "actually" need.

    ligo_resolution = 2.2 # degrees; chosen via trial-and-error
    n_points = int(x.size * spacing / ligo_resolution)
    n_points = np.maximum(n_points, 8)

    # Use an interpolating, periodic spline fit to make it so that we can
    # evaluate the polygon bounds as a continuous function.

    t = np.linspace(0., 1., len(x))
    tck_x = si.splrep(t, x, per=1, s=0.)
    tck_y = si.splrep(t, y, per=1, s=0.)

    # Resample the polygon points more densely than we had before. This might
    # not actually help our interpolation since we're about to downsample,
    # but I don't think it'll hurt? We also choose the array size such that
    # we'll be able to efficiently downsample to our final array size.

    window_size = 15 # arbitrarily chosen
    window = np.hamming(window_size)
    window /= window.sum() # important normalization!
    t_resamp = np.linspace(0., 1., window_size * n_points)
    x_resamp = si.splev(t_resamp, tck_x)
    y_resamp = si.splev(t_resamp, tck_y)

    # chunk-convolve with our window

    x_resamp = (x_resamp.reshape((n_points, window_size)) * window).sum(axis=1)
    y_resamp = (y_resamp.reshape((n_points, window_size)) * window).sum(axis=1)

    # Restore the invariant that x[0] = x[-1]. This is super inefficient, but
    # meh.

    x = np.empty(x_resamp.size + 1)
    x[:-1] = x_resamp
    x[-1] = x[0]

    y = np.empty(y_resamp.size + 1)
    y[:-1] = y_resamp
    y[-1] = y[0]

    return x, y


def get_events():
    # The timing information (PeakAmpGPS) is only available in filelist.json,
    # so we need to read that file and munge its data into the records that
    # we'll emit.
    with io.open(bpath('filelist.json')) as f:
        fldata = json.load(f)

    for filename in os.listdir(_bootstrap_dir):
        if not filename.endswith('.json') or not filename.startswith('GW'):
            continue

        with io.open(bpath(filename)) as f:
            geojson = json.load(f)

        ident = filename.split('_')[0]
        flitem = fldata['data'][ident]

        yield ident, flitem, geojson


def main():
    app_dir = bpath(os.pardir, 'app')
    bootstrap_data = {}

    for ident, flitem, geojson in get_events():
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
            area, x, y = fix_polygon_handedness(x, y)

            # Suppress the tiny regions that the contour-finder sometimes
            # gives us.
            if area < AREA_CUTOFF_68:
                continue

            # Smooth the contours since they come out jagged on the healpix
            # grid used to compute the probabilities. The
            # `ligo-skymap-contour` program has various smoothing options but
            # in some fairly extensive experimentation I couldn't get them to
            # produce acceptable results.
            x, y = smooth_polygon(x, y)

            # Convert to list-of-tuples for JSON output.
            contour = [None] * len(x)
            for i in range(len(x)):
                contour[i] = (x[i], y[i])

            regions.append({'contours': {'68': contour}})

        result['regions'] = regions

    with io.open(os.path.join(app_dir, 'bootstrap_data.json'), 'wt') as f:
        json.dump(bootstrap_data, f)


if __name__ == '__main__':
    main()
