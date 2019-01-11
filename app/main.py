# Copyright 2019 Peter Williams
# Licensed under the MIT License
#
# The app backend.

from google.cloud import datastore
import json
import os

from flask import Flask
app = Flask(__name__)



@app.route('/bootstrap')
def bootstrap():
    """Note: the app.yaml enforces that only the app admin can invoke this command.

    You need to copy th bootstrap JSON files into the directory containing
    this file in order for them to land on the servers.

    """
    try:
        client = datastore.Client()
        n = 0

        with open('filelist.json') as f:
            fldata = json.load(f)

        for filename in os.listdir():
            if not filename.endswith('.json') or not filename.startswith('GW'):
                continue

            with open(filename) as f:
                text = f.read()

            ident = filename.split('_')[0]
            flitem = fldata['data'][ident]

            peak_gps = flitem['files']['PeakAmpGPS']

            key = client.key('event', ident)
            ent = datastore.Entity(key=key, exclude_from_indexes=('geojson',))
            ent.update({
                'ident': ident,
                'geojson': text.encode('utf8'), # these are too big to fit as "text" type
                'peak_gps': peak_gps,
            })
            client.put(ent)
            n += 1

        return '%d items added' % n
    except Exception as e:
        return 'ERROR: %s' % e


@app.route('/api/workingset')
def working_set():
    """Get a JSON blob with info about recent events that we might want to plot.

    """
    client = datastore.Client()
    q = client.query(kind='event', projection=('ident', 'peak_gps'))
    # TODO: filter by recency!
    results = dict((r['ident'], r) for r in q.fetch())
    return json.dumps(results)


@app.route('/api/<string:ident>/contourdata')
def contour_data(ident):
    """Get a GeoJSON blob with the contour data for the event.

    """
    client = datastore.Client()
    key = client.key('event', ident)
    ent = client.get(key)
    return ent['geojson']


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
