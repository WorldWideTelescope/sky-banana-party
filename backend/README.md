# The Google App Engine backend

This is the backend Python app that has the server-side smarts. It is served
at <http://sky-banana-party.appspot.com/>. The user-facing frontend,
<http://skybanana.party/>, makes various API calls to this backend from
JavaScript.

Update the deployed app with `gcloud app deploy`. Update datastore indexes
with `gcloud datastore indexes create index.yaml`.
