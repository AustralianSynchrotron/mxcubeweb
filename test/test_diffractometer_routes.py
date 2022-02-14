import pytest
from wrapper.api_client import APIClient


def test_get_phase_list(client: APIClient) -> None:
    """Checks retrieval of phase list and if the returned data is list.
    Does not test if the actual phases in the list are correct.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.diffractometer.get("/phaselist")
    assert isinstance(data["current_phase"], list)


def test_get_phase(client: APIClient) -> None:
    """Checks if current phase is one of the phases in the phase list.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.diffractometer.get("/phaselist")
    assert client.diffractometer.phase in data["current_phase"]


@pytest.mark.parametrize(
    "new_phase",
    [
        "Transfer",
        "Centring",
        "DataCollection",
        "BeamLocation",
    ],
)
def test_set_phase(client: APIClient, new_phase: str) -> None:
    """Sets phase to a phase P (any phase in the phase list), checks if the
    actual phase after set_phase is P.

    Moves the phase back to the original phase OP, and verifies that the
    current phase after the move is OP.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    new_phase : str
        Phase to put the diffractometer into.
    """
    # Get current phase.
    original_phase = client.diffractometer.phase

    # Change phase to new phase.
    client.diffractometer.put("/phase", data={"phase": new_phase})

    # Verify the phase was changed successfully.
    assert client.diffractometer.phase == new_phase

    # Revert phase back to its original value.
    client.diffractometer.put("/phase", data={"phase": original_phase})


    # Move phase back to its original value
    resp = client.put(
        "/mxcube/api/v0.1/diffractometer/phase",
        data=json.dumps({"phase": original_phase}),
        content_type="application/json",
    )

    assert new_phase == actual_phase


def test_get_aperture(client):
    """
    Checks if the data returned have is on the expected format
    """
    resp = client.get("/mxcube/api/v0.1/diffractometer/aperture")
    data = json.loads(resp.data)

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.diffractometer.get("/aperture")
    assert isinstance(data["currentAperture"], int)
    assert isinstance(data["apertureList"], list)


@pytest.mark.parametrize(
    "new_aperture,should_change",
    [(10, True), (12, False), ("20", False), (50, True), ("abcd", False)],
)
def test_set_aperture(
    client: APIClient,
    new_aperture: int,
    should_change: bool,
) -> None:
    """Sets the aperture to an aperture AP belonging to the list of valid
    apertures and verifies that the aperture actually changed to AP.

    Moves the aperture back to its original value and verifies that the
    original value also is the current.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    new_aperture : int
        New aperture value.
    should_change : bool
        True if the change should succeed, False if it should fail.
    """
    original_aperture = client.diffractometer.aperture

    # Attempt to set the aperture.
    client.diffractometer.put("/aperture", data={"diameter": new_aperture})
    assert (client.diffractometer.aperture == new_aperture) == should_change

    # Set aperture back to original value.
    client.diffractometer.put("/aperture", data={"diameter": original_aperture})
    assert client.diffractometer.aperture == original_aperture


def test_get_md_plate_mode(client: APIClient) -> None:
    """Simply checks if the route runs and does not throw any exceptions.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    assert isinstance(client.diffractometer.md_in_plate_mode, bool)


def test_get_diffractometer_info(client: APIClient) -> None:
    """Simply checks if the route runs and does not throws any exceptions.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    expected_keys = ["currentPhase", "phaseList", "useSC"]
    data = client.diffractometer.get("/info")
    assert all([key in data for key in expected_keys])
