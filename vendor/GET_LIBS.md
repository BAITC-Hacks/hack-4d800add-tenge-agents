# Vendor these files here (no CDN at runtime)

pip download is not needed; fetch once with the venue network and commit:

    cd viewer/vendor
    curl -L -o cytoscape.min.js https://unpkg.com/cytoscape@3/dist/cytoscape.min.js
    curl -L -o layout-base.js  https://unpkg.com/layout-base@2/layout-base.js
    curl -L -o cose-base.js    https://unpkg.com/cose-base@2/cose-base.js
    curl -L -o cytoscape-fcose.js https://unpkg.com/cytoscape-fcose@2/cytoscape-fcose.js

Load order in index.html: cytoscape.min.js → layout-base.js → cose-base.js → cytoscape-fcose.js
All MIT-licensed; list in DISCLOSURE.md.
