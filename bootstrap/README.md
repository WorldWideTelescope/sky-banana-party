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
