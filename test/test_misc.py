from wrapper.api_client import APIClient

from mxcube3.version import __version__ as version


def test_version() -> None:
    assert isinstance(version, float)


def test_uiproperties(client: APIClient) -> None:
    """Test if we can fetch the UI properties.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.get("/uiproperties")

    # Check expected view properties are present and components
    # have at least the minimal attributes required.
    required_views = ["beamline_setup", "sample_view"]
    required_attrs = ["attribute", "label", "object_type", "value_type"]
    for view in required_views:
        assert view in data
        for attribute in required_attrs:
            for component in data[view]["components"]:
                assert attribute in component


def test_log(client: APIClient) -> None:
    """Test if we can fetch the log.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.get("/log/")

    required_attrs = ["logger", "message", "severity", "timestamp"]
    for item in data:
        for attribute in required_attrs:
            assert attribute in item


def test_detector(client: APIClient) -> None:
    """Test if we can fetch the detector info.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.get("/detector/")

    required_attrs = ["fileSuffix"]
    for attr in required_attrs:
        assert attr in data
