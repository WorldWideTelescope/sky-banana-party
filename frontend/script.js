(function() {
    const backend_base = "http://sky-banana-party.appspot.com/api/";

    function size_content() {
        const new_width = ($("html").width()) + "px";
        $("#wwtcanvas").css("width", new_width);
        const new_height = ($("html").height()) + "px";
        $("#wwtcanvas").css("height", new_height);
    }

    $(document).ready(size_content);
    $(window).resize(size_content);

    function initialize() {
        // This function call is
        // wwt-web-client/HTML5SDK/wwtlib/WWTControl.cs:WWTControl::InitControlParam.
        // It creates a singleton WWTControl object, accessible here as
        // `wwtlib.WWTControl.singleton`, and returns a singleton
        // ScriptInterface object, also accessible as
        // `wwtlib.WWTControl.scriptInterface`.
        var wwt_si = wwtlib.WWTControl.initControlParam("wwtcanvas", true); // "true" => WebGL enabled
        wwt_si.add_ready(wwt_ready);

        apply_config();
    }

    $(document).ready(initialize);

    function wwt_ready() {
        var wwt_ctl = wwtlib.WWTControl.singleton;
        var wwt_si = wwtlib.WWTControl.scriptInterface;

        wwt_si.loadImageCollection('https://WorldWideTelescope.github.io/pywwt/surveys.xml');
        wwt_si.setBackgroundImageByName('USNOB');
        wwt_si.settings.set_showConstellationBoundries(false);
        wwt_si.settings.set_showConstellationFigures(false);
        wwt_si.settings.set_showConstellationSelection(false);
        wwt_si.settings.set_showGrid(true);

        setup_bananas(wwt_ctl, wwt_si);
        setup_controls(wwt_ctl, wwt_si);
    }

    //wwt.settings.set_actualPlanetScale(false);
    //wwt.settings.set_showConstellationBoundries(false);
    //wwt.settings.set_showConstellationFigures(false);
    //wwt.settings.set_showConstellationSelection(false);
    //wwt.settings.set_constellationBoundryColor('#0000ff');
    //wwt.settings.set_constellationFigureColor('#ff0000');
    //wwt.settings.set_constellationSelectionColor('#ffff00');
    //wwt.settings.set_showCrosshairs(false);
    //wwt.settings.set_crosshairsColor('#ffffff');
    //wwt.settings.set_showEcliptic(false);
    //wwt.settings.set_galacticMode(false);
    //wwt.settings.set_showGalacticGrid(false);
    //wwt.settings.set_showEclipticGrid(false);
    //wwt.settings.set_showAltAzGrid(false);
    //wwt.settings.set_localHorizonMode(false);
    //wwt.settings.set_locationAltitude(0.0);
    //wwt.settings.set_locationLat(47.633);
    //wwt.settings.set_locationLng(122.133333);
    //wwt.settings.set_solarSystemLighting(true);
    //wwt.settings.set_solarSystemMilkyWay(true);
    //wwt.settings.set_solarSystemOrbits(true);
    //wwt.settings.set_solarSystemScale('1');
    //wwt.settings.set_solarSystemStars(true);
    //wwt.settings.set_solarSystemMinorOrbits(false);
    //wwt.settings.set_solarSystemPlanets(true);

    function setup_bananas(wwt_ctl, wwt_si) {
        const wsurl = backend_base + "events/workingset";

        $.getJSON(wsurl, function(data) {
            var index = 0;

            for (const event_info of data) {
                const key = event_info.ident;
                const regurl = backend_base + "events/" + key + "/regions";
                event_info.index = index;
                $.getJSON(regurl, function(regions) { setup_one_event(wwt_ctl, wwt_si, event_info, regions) });
                index++;
            }
        });
    }

    // from https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
    const palette = [
        [230, 25, 75],
        [60, 180, 75],
        [255, 225, 25],
        [0, 130, 200],
        [245, 130, 48],
        [145, 30, 180],
        [70, 240, 240],
        [240, 50, 230],
        [210, 245, 60],
        [250, 190, 190],
        [0, 128, 128],
        [230, 190, 255],
        [170, 110, 40],
        [255, 250, 200],
        [128, 0, 0],
        [170, 255, 195],
        [128, 128, 0],
        [255, 215, 180]
    ];

    function setup_one_event(wwt_ctl, wwt_si, event_info, regions) {
        const peak_gps = event_info.peak_gps;
        var region_index = 0;

        for (const region of regions) {
            const id = event_info.ident + "_" + region_index;
            region_index++;

            const contour = region["contours"]["68"];
            const c = palette[event_info.index % palette.length];

            var poly = wwt_si.createPolygon(true); // fill=true
            poly.set_id(id);
            poly._fillColor$1 = wwtlib.Color.fromArgb(80, c[0], c[1], c[2]); // XXX API only does FromWindowsColorNamed
            poly._lineColor$1 = wwtlib.Color.fromArgb(0, 0, 0, 0);
            poly.set_lineWidth(0);

            for (const [x, y] of contour) {
                poly.addPoint(x, y); // addPoint() takes decimal degrees for both
            }

            wwt_si.addAnnotation(poly);
        }
    }

    function apply_config() {
        // Note: at the moment, this is called before the WWT control is
        // necessarily set up; would be straightforward to restructure if we
        // end up needing access to it.

        $.getJSON("config.json").done(function(data) {
            var ligo_status_html;
            var seconds_until_start;

            if (data.ligo_mode == "off") {
                seconds_until_start = 0.001 * (data.ligo_turn_on_unix_ms - Date.now());

                if (seconds_until_start < 1) {
                    // The JSON must be stale ...
                    data.ligo_mode = "on";
                    // ... handle this more
                }
            }

            if (data.ligo_mode == "off") {
                ligo_status_html = "<a href=\"https://www.ligo.caltech.edu/\">LIGO</a> is currently <b>off</b>" +
                    " — " + data.ligo_turn_on_html_frag + " will begin in " + wait_time_to_text(seconds_until_start) +
                    "<br>Events from earlier observing runs are shown.";
            } else {
                ligo_status_html = "<a href=\"https://www.ligo.caltech.edu/\">LIGO</a>’s status is <b>unknown</b>";
            }

            $("#ligostatus").html(ligo_status_html);
        });
    }

    function setup_controls(wwt_ctl, wwt_si) {
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
                    wwt_ctl._tilt(event.movementX, event.movementY);
                else
                    wwt_ctl.move(event.movementX, event.movementY);
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
                    wwt_ctl.zoom(1.43);
                else
                    wwt_ctl.zoom(0.7);
            }
        })(true));
    }

    function wait_time_to_text(seconds) {
        if (seconds > 5184000) { // 86400 * 30 * 2
            const months = seconds / 2592000;
            return months.toFixed(0) + " months";
        } else if (seconds > 259200) { // 86400 * 3
            const days = seconds / 86400;
            return days.toFixed(0) + " days";
        } else if (seconds > 7200) { // 2 hours
            const hours = seconds / 3600;
            return "about " + hours.toFixed(0) + " hours";
        } else {
            // With timezones, etc., I don't think we'll get more precise than this.
            return "just a few hours!";
        }
    }
})();
