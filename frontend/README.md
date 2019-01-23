# The app frontend

This is the frontend of the app, served as static files off of <http://skybanana.party>.

## Local testing

The recommendend means for local testing is to use Node.js:

```
npx httpserver 8080
```

This server is a bit more sophisticated about MIME types and whatnot than some
other one-liners.

Note that the app hardcodes a reference to the backend URL on
<http://sky-banana-party.appspot.com/>, so it's not super convenient to test
integrated changes to both the frontend and backend.

## Deployment

Run `./publish.sh`, which uses the `gsutil` command-line tool.

