# Sky Banana Party

**See the app at <http://skybanana.party/>!** (Note: it will not work over
  HTTPS — only plain HTTP for now ☹)

A website that shows recent [LIGO](https://www.ligo.org/) events on the sky.
It's got a silly name, but the hope is that it will show how to create a
simple web app that uses
[WorldWide Telescope](http://www.worldwidetelescope.org/) technology to power
a nice, interactive all-sky visualization of astronomical data.

This project was started during the [AAS233](https://aas.org/meetings/aas233)
Hack Together Day, but only the barest progress was made that day. Getting
nice localization sky maps out of LIGO data turned out to be harder than
anticipated!

## Technical Overview

The app runs in [Google App Engine](https://cloud.google.com/appengine/),
simply because it’s a system with which the author was familiar. The live app
backend, implemented in `app/main.py`, is actually relatively simple, and just
provides a small API for retrieving data about LIGO events and their
localizations.

The website as seen by users is mostly simple static content, stored in
`app/static/`. It’s very quick to create a WWT control, and then there’s some
custom JavaScript to download the LIGO event data and render them in the WWT
framework.

The idea is that when LIGO is running, the app will show events as they occur.
But in the meantime, we have to show something. The directory `bootstrap/` has
code to bootstrap the event database with data from the LIGO
[O1/O2 Catalog](https://www.ligo.org/detections/O1O2catalog.php).

## Legalities

Copyright 2019 Peter K. G. Williams. Licensed under the MIT license.
