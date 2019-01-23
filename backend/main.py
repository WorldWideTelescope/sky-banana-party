# Copyright 2019 Peter Williams
# Licensed under the MIT License

"""The app backend."""

from google.cloud import datastore
import json
import os

from flask import Flask, Response
app = Flask(__name__)


@app.route('/admin/destroy')
def destroy():
    """Note: the app.yaml enforces that only the app admin can invoke this
    command.

    Clear all events from the database.

    """
    try:
        # This approach seems to be the best that we can do? No isolation,
        # etc.

        client = datastore.Client()
        all_keys = set()
        n = 0

        q = client.query(kind='event')
        q.keys_only()

        for entity in q.fetch():
            all_keys.add(entity.key)
            n += 1

        client.delete_multi(all_keys)
        return '%d items deleted' % n
    except Exception as e:
        return 'ERROR: %s' % e


@app.route('/admin/bootstrap')
def bootstrap():
    """Note: the app.yaml enforces that only the app admin can invoke this command.

    Initialize the event database with historical data. You need to have
    created `bootstrap_data.json` in this directory by running
    `../bootstrap/postprocess.py`; see `../bootstrap/README.md`. When you
    deploy the site with `gcloud app deploy`, that data file will be uploaded
    to the server. This call ingests the JSON data into the Google Cloud
    Datastore system.

    """
    try:
        with open('bootstrap_data.json') as f:
            bs_data = json.load(f)

        client = datastore.Client()
        n = 0

        for ident, data in bs_data.items():
            # the region/contour data are too big to fit as "text" type, so we
            # encode as UTF-8 and specify them as `exclude_from_indexes`,
            # which causes them to be treated as a "blob" type which can be
            # much bigger.
            regionjson = json.dumps(data['regions']).encode('utf8')

            key = client.key('event', ident)
            ent = datastore.Entity(key=key, exclude_from_indexes=('regionjson',))
            ent.update({
                'ident': ident,
                'regionjson': regionjson,
                'peak_gps': data['peak_gps'],
            })
            client.put(ent)
            n += 1

        return '%d items added' % n
    except Exception as e:
        return 'ERROR: %s' % e


@app.route('/api/events/workingset')
def working_set():
    """Get a JSON blob with info about recent events that we might want to plot.

    The returned blob is a list of events sorted by occurrence time; most
    recent is last. (This ordering is chosen so that future events can be
    appended to the list, which feels like the more nature way to do things.)
    Each event is a dict of information that I don't feel like documenting
    right now.

    """
    client = datastore.Client()
    q = client.query(
        kind='event',
        projection=('ident', 'peak_gps'),
        order=('peak_gps',),
    )
    # TODO: filter by recency
    results = list(q.fetch())

    # We need to enable CORS since we're serving from appspot.com to skybanana.party.
    resp = Response(json.dumps(results))
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/events/<string:ident>/regions')
def regions(ident):
    """Get the region data for the specified event.

    The region data are returned as a JSON document whose structure is not
    documented here. See `../bootstrap/postprocess.py` for how the data are
    constructed.

    """
    client = datastore.Client()
    key = client.key('event', ident)
    ent = client.get(key)

    # We need to enable CORS since we're serving from appspot.com to skybanana.party.
    resp = Response(ent['regionjson'])
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
