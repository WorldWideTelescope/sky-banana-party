(function() {
    function size_content() {
        const new_width = ($("html").width()) + "px";
        $("#wwtcanvas").css("width", new_width);
        const new_height = ($("html").height()) + "px";
        $("#wwtcanvas").css("height", new_height);
    }

    $(document).ready(size_content);
    $(window).resize(size_content);

    var wwt;

    function initialize() {
        wwt = wwtlib.WWTControl.initControlParam("wwtcanvas", true); // "true" => WebGL enabled
        wwt.add_ready(wwt_ready);
    }

    $(document).ready(initialize);

    function wwt_ready() {
        wwt.loadImageCollection('https://WorldWideTelescope.github.io/pywwt/surveys.xml')
        wwt.setForegroundImageByName('Digitized Sky Survey (Color)')
        wwt.setBackgroundImageByName('Hydrogen Alpha Full Sky Map')
        wwt.setForegroundOpacity(80.0)
        wwt.settings.set_actualPlanetScale(false)
        wwt.settings.set_showConstellationBoundries(false)
        wwt.settings.set_showConstellationFigures(false)
        wwt.settings.set_showConstellationSelection(false)
        wwt.settings.set_constellationBoundryColor('#0000ff')
        wwt.settings.set_constellationFigureColor('#ff0000')
        wwt.settings.set_constellationSelectionColor('#ffff00')
        wwt.settings.set_showCrosshairs(false)
        wwt.settings.set_crosshairsColor('#ffffff')
        wwt.settings.set_showEcliptic(false)
        wwt.settings.set_showGrid(false)
        wwt.settings.set_galacticMode(false)
        wwt.settings.set_showGalacticGrid(false)
        wwt.settings.set_showEclipticGrid(false)
        wwt.settings.set_showAltAzGrid(false)
        wwt.settings.set_localHorizonMode(false)
        wwt.settings.set_locationAltitude(0.0)
        wwt.settings.set_locationLat(47.633)
        wwt.settings.set_locationLng(122.133333)
        wwt.settings.set_solarSystemLighting(true)
        wwt.settings.set_solarSystemMilkyWay(true)
        wwt.settings.set_solarSystemOrbits(true)
        wwt.settings.set_solarSystemScale('1')
        wwt.settings.set_solarSystemStars(true)
        wwt.settings.set_solarSystemMinorOrbits(false)
        wwt.settings.set_solarSystemPlanets(true)

        //const wsurl = new URL("api/workingset", window.location.href).href;
        //$.getJSON(wsurl, function(data) {
        //    for (const [key, value] of Object.entries(data)) {
        //        const peak_gps = value.peak_gps;
        //
        //        const gjurl = new URL("api/" + key + "/contourdata", window.location.href).href;
        //        $.getJSON(gjurl, function(geojson) {
        //            for (const feature of geojson.features[0].geometry.coordinates) {
        //                console.log(feature);
        //            }
        //        });
        //    }
        //});

        // TODO: this code is from pywwt and was designed for use in Jupyter;
        // we might be able to do something simpler here.

        var canvas = document.body.getElementsByTagName("canvas")[0];

        function new_event(action, attributes, deprecated) {
            if (!deprecated) {
                var event = new CustomEvent(action);
            } else {
                var event = document.createEvent("CustomEvent");
                event.initEvent(action, false, false);
            }

            if (attributes) {
                for (var attr in attributes)
                    event[attr] = attributes[attr];
            }

            return event;
        }

        const wheel_up = new_event("wwt-zoom", {deltaY: 53, delta: 53}, true);
        const wheel_down = new_event("wwt-zoom", {deltaY: -53, delta: -53}, true);
        const mouse_left = new_event("wwt-move", {movementX: 53, movementY: 0}, true);
        const mouse_up = new_event("wwt-move", {movementX: 0, movementY: 53}, true);
        const mouse_right = new_event("wwt-move", {movementX: -53, movementY: 0}, true);
        const mouse_down = new_event("wwt-move", {movementX: 0, movementY: -53}, true);

        const zoomCodes = {
            "KeyZ": wheel_up,
            "KeyX": wheel_down,
            90: wheel_up,
            88: wheel_down
        };

        const moveCodes = {
            "KeyJ": mouse_left,
            "KeyI": mouse_up,
            "KeyL": mouse_right,
            "KeyK": mouse_down,
            74: mouse_left,
            73: mouse_up,
            76: mouse_right,
            75: mouse_down
        };

        window.addEventListener("keydown", function(event) {
            // "must check the deprecated keyCode property for Qt"
            if (zoomCodes.hasOwnProperty(event.code) || zoomCodes.hasOwnProperty(event.keyCode)) {
                var action = zoomCodes.hasOwnProperty(event.code) ? zoomCodes[event.code] : zoomCodes[event.keyCode];

                if (event.shiftKey)
                    action.shiftKey = 1;
                else
                    action.shiftKey = 0;

                canvas.dispatchEvent(action);
            }

            if (moveCodes.hasOwnProperty(event.code) || moveCodes.hasOwnProperty(event.keyCode)) {
                var action = moveCodes.hasOwnProperty(event.code) ? moveCodes[event.code] : moveCodes[event.keyCode];

                if (event.shiftKey)
                    action.shiftKey = 1
                else
                    action.shiftKey = 0;

                if (event.altKey)
                    action.altKey = 1;
                else
                    action.altKey = 0;

                canvas.dispatchEvent(action);
            }
        });

        canvas.addEventListener("wwt-move", (function(proceed) {
            return function(event) {
                if (!proceed)
                    return false;

                if (event.shiftKey)
                    delay = 500; // milliseconds
                else
                    delay = 100;

                setTimeout(function() { proceed = true }, delay);

                if (event.altKey)
                    wwtlib.WWTControl.singleton._tilt(event.movementX, event.movementY);
                else
                    wwtlib.WWTControl.singleton.move(event.movementX, event.movementY);
            }
        })(true));

        canvas.addEventListener("wwt-zoom", (function(proceed) {
            return function(event) {
                if (!proceed)
                    return false;

                if (event.shiftKey)
                    delay = 500; // milliseconds
                else
                    delay = 100;

                setTimeout(function() { proceed = true }, delay);

                if (event.deltaY < 0)
                    wwtlib.WWTControl.singleton.zoom(1.43);
                else
                    wwtlib.WWTControl.singleton.zoom(0.7);
            }
        })(true));
    }
})();
