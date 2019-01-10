# Bootstrapping the database

This directory is about the special code needed to do a one-time bootstrap of
the database.

If this actually becomes a thing we'll need to write a LIGO event listener
but that's actually totally unnecessary for the hack day.

## Pulling down the data

Pull down <https://www.gw-openscience.org/catalog/GWTC-1-confident/filelist/>
as `filelist.json`.

Oh wait, this is all worthless. Just download individual files from
<https://dcc.ligo.org/LIGO-P1800381/public>.

Use `ligo-skymap-contour` to convert the `skymap.fits.gz` files into GeoJSON.
Some needed packages: `lscsoft-glue`, `ligo-segments`, `reproject`, `healpy`,
`ligo-gracedb`, `lalsuite`,`'h5py`.

Finally:

```
for f in *.gz ; do
  n=$(echo $f |sed -e 's/fits.gz/c68.json/')
  ligo-skymap-contour --contour=68 $f >$n
done
```

In the JSON files, let `feature_list =
<JSON>['features'][0]['geometry']['coordinates']`. Then `feature_list` is a
list of independent localization regions. Each feature is a list of
coordinates, and each coordinate is a 2-item list of (I presume) `[RA, dec]`,
both measured in degrees.
