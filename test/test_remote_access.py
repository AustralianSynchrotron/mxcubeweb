import random
import string

import pytest
from wrapper.api_client import TEST_PASS, TEST_USER, APIClient


def test_ra_info(client: APIClient) -> None:
    """Test required keys are returned when calling the remote access info endpoint.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    data = client.remote_access.get("/")

    expected_keys = [
        "observers",
        "sid",
        "master",
        "observerName",
        "allowRemote",
        "timeoutGivesControl",
    ]
    assert all([key in data["data"] for key in expected_keys])


def test_ra_take_control(client: APIClient, public_client: APIClient) -> None:
    """Test that we can force a session to become the master session.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    public_client : APIClient
        Unauthenticated public client session.
    """
    public_client.login(username=TEST_USER, password=TEST_PASS)

    # Verify user session is not the current master session.
    assert not public_client.remote_access.is_master

    # Take master control of the beamline.
    public_client.remote_access.post("/take_control", data={})

    # Verify user session is now the master session.
    assert public_client.remote_access.is_master


def test_ra_give_control(client: APIClient, public_client: APIClient) -> None:
    """Test that a user session can give master control to another user session.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    public_client : APIClient
        Unauthenticated public client session.
    """
    public_client.login(username=TEST_USER, password=TEST_PASS)

    # Verify user session is not the current master session.
    assert not public_client.remote_access.is_master

    # From master session give control to the new user session.
    client.remote_access.post(
        "/give_control", data={"sid": public_client.remote_access.sid}
    )

    # Verify user session is now the master session.
    assert public_client.remote_access.is_master


@pytest.mark.parametrize(
    "give_control,message",
    [
        (False, "Nope, not happening."),
        (True, "OK, you seem competent."),
    ],
)
def test_ra_request_control(
    client: APIClient,
    public_client: APIClient,
    give_control: bool,
    message: str,
) -> None:
    """Test the master control request endpoints.

    From an observer session we request control of the beamline,
    the master user session will either approve or deny the request.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    public_client : APIClient
        Unauthenticated public client session.
    give_control : bool
        True to grant control to the requesting user, False to deny.
    message : str
        Status message to pass to the endpoint.
    """
    public_client.login(username=TEST_USER, password=TEST_PASS)

    # Verify user session is not the current master session.
    assert not public_client.remote_access.is_master

    # Request that user with master session relinquish control.
    public_client.remote_access.post(
        "/request_control",
        data={
            "name": "Dr Farnsworth",
            "message": "Good news everyone!",
            "control": True,
        },
    )

    # Verify control has been requested.
    assert client.remote_access.control_requested

    # From master session grant/deny control to the new user session.
    client.remote_access.post(
        "/request_control_response",
        data={"giveControl": give_control, "message": message},
    )

    # Verify user session is in the desired state.
    assert public_client.remote_access.is_master == give_control


def test_ra_allow_remote(client: APIClient) -> None:
    """Test enabling/disabling the allow remote setting.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    # Set "allowRemote" to inverse of default value.
    initial_val = client.remote_access.allow_remote
    client.remote_access.post("/allow_remote", data={"allow": not initial_val})

    # Verify the value has actually changed.
    assert client.remote_access.allow_remote is not initial_val

    # Set value back to original value to cleanup.
    client.remote_access.post("/allow_remote", data={"allow": initial_val})
    assert client.remote_access.allow_remote is initial_val


def test_ra_timeout_gives_control(client: APIClient) -> None:
    """Test enabling/disabling the auto-approve timeout on control request setting.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    # Set "timeoutGivesControl" to inverse of default value.
    initial_val = client.remote_access.timeout_gives_control
    client.remote_access.post(
        "/timeout_gives_control", data={"timeoutGivesControl": not initial_val}
    )

    # Verify the value has actually changed.
    assert client.remote_access.timeout_gives_control is not initial_val

    # Set value back to original value to cleanup.
    client.remote_access.post(
        "/timeout_gives_control", data={"timeoutGivesControl": initial_val}
    )
    assert client.remote_access.timeout_gives_control is initial_val


def test_ra_chat(client: APIClient, public_client: APIClient) -> None:
    """Test writing to and reading back the chat log.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    public_client : APIClient
        Unauthenticated public client session.
    """
    # Check if we can write to the chat.
    message = "".join(random.choice(string.ascii_letters) for i in range(10))
    client.remote_access.post(
        "/chat", data={"message": message, "sid": client.remote_access.sid}
    )

    # From a second user session verify message was written to chat.
    public_client.login(username=TEST_USER, password=TEST_PASS)
    ra_chat = public_client.remote_access.get("/chat")
    assert isinstance(ra_chat, dict) and "messages" in ra_chat.keys()
    assert any(map(lambda item: item["message"] == message, ra_chat["messages"]))
