from wrapper.api_client import APIClient

# Python 2 and 3 compatibility
if sys.version_info[0] >= 3:
    unicode = str


def test_beamline_get_all_attribute(client):
    """
    Checks that the data returned has the right structure and if "all"
    beamline attributes are at least present
    """
    resp = client.get("/mxcube/api/v0.1/beamline/")
    data = json.loads(resp.data)

    actual = list(data.get("hardwareObjects").keys())

    expected = [
        "beam",
        "cryo",
        "data_publisher",
        "detector",
        "detector.detector_distance",
        "diffractometer",
        "diffractometer.backlight",
        "diffractometer.backlightswitch",
        "diffractometer.beamstop",
        "diffractometer.beamstop_distance",
        "diffractometer.capillary",
        "diffractometer.frontlight",
        "diffractometer.frontlightswitch",
        "diffractometer.kappa",
        "diffractometer.kappa_phi",
        "diffractometer.phi",
        "diffractometer.phix",
        "diffractometer.phiy",
        "diffractometer.phiz",
        "diffractometer.sampx",
        "diffractometer.sampy",
        "diffractometer.zoom",
        "energy",
        "energy.wavelength",
        "fast_shutter",
        "flux",
        "transmission",
    ],
    "machineinfo": [
        "machine_info",
        "resolution",
        "safety_shutter",
        "transmission",
    ]

    assert isinstance(data["hardwareObjects"], dict)
    assert isinstance(data["actionsList"], list)
    assert isinstance(data["path"], str)
    assert len(data["energyScanElements"]) == 31
    assert isinstance(data["availableMethods"], dict)
    expected = sum([val for key, val in BEAMLINE_ATTRS.items()], [])
    assert all(attr in actual for attr in expected)
    assert len(actual) == len(expected)


def test_beamline_get_attribute(client: APIClient):
    """Tests retrieval of all the beamline attributes (one by one), checks that
    the data returned at-least contain a minimal set of keys that make up a
    'beamline attribute'.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    bl_attrs = [
        ("safety_shutter", "nstate"),
        ("diffractometer.capillary", "nstate"),
        ("diffractometer.beamstop", "nstate"),
        ("fast_shutter", "nstate"),
        ("resolution", "motor"),
        ("energy", "motor"),
        ("flux", "actuator"),
        ("transmission", "motor"),
        ("detector.detector_distance", "motor"),
    ]

    for name, adapter_type in bl_attrs:
        resp = client.get(f"/mxcube/api/v0.1/beamline/{adapter_type}/{name}")
        data = json.loads(resp.data)

                assert data["available"] is True


def test_beamline_set_attribute(client: APIClient):
    """Tests set on the writable attributes

    Basically only tests that the set command executes without unexpected
    errors. Reads the attributes current value and sets it to the same, so
    that the test can be safely executed on a beamline.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    bl_attrs = [
        ("resolution", "motor"),
        ("energy", "motor"),
        ("transmission", "motor"),
        ("safety_shutter", "nstate"),
        ("diffractometer.beamstop", "nstate"),
        ("fast_shutter", "nstate"),
        ("detector.detector_distance", "motor"),
    ]

    for name, adapter_type in bl_attrs:
        resp = client.get(f"/mxcube/api/v0.1/beamline/{adapter_type}/{name}")
        data = json.loads(resp.data)

                new_value = data.get("value")

        resp = client.put(
            f"/mxcube/api/v0.1/beamline/{adapter_type}/value",
            data=json.dumps({"name": name, "value": new_value}),
            content_type="application/json",
        )

        resp = client.get(f"/mxcube/api/v0.1/beamline/{adapter_type}/{name}")
        data = json.loads(resp.data)


def test_available_methods(client: APIClient):
    """Test expected beamline methods are defined and in expected state.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.beamline.get("/")
    expected_vals = [
        ("characterisation", True),
        ("datacollection", True),
        ("energy_scan", True),
        ("helical", True),
        ("mesh_scan", False),
        ("xrf_scan", True),
    ]
    for key, expected_val in expected_vals:
        assert data["availableMethods"][key] == expected_val


def test_get_beam_info(client: APIClient):
    """Tests retrieval of information regarding the beam, and that the data is
    returned in the expected format.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    resp = client.get("/mxcube/api/v0.1/beamline/beam/info")
    data = json.loads(resp.data)

    assert isinstance(data["currentAperture"], int)
    assert len(data["apertureList"]) >= 0
    assert isinstance(data["position"][0], int)
    assert isinstance(data["position"][1], int)
    assert isinstance(data["size_x"], float)
    assert isinstance(data["size_y"], float)


def test_get_data_path(client: APIClient):
    """Retrieve data path, this is specific for each beamline.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    path = client.beamline.datapath
    assert isinstance(path, str)
    assert len(path) > 0
