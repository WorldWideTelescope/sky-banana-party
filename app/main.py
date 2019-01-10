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
        flitem = flist['data'][ident]

        peak_gps = flitem['files']['PeakAmpGPS']

        key = client.key('event', ident)
        ent = datastore.Entity(key=key)
        ent.update({
            'ident': ident,
            'geojson': text,
            'peak_gps': peak_gps,
        })
        client.put(ent)
        n += 1

    return '%d items added' % n


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
