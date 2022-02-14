import pytest
from wrapper.api_client import TEST_PASS, TEST_USER, APIClient
from wrapper.exceptions import AuthFailure


def test_login_success(client: APIClient, public_client: APIClient) -> None:
    """Test attempts to authenticate a second user session with the test user account.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    public_client : APIClient
        Unauthenticated public client session.
    """
    # Calls wrapper method, will raise an exception on auth failure.
    public_client.login(username=TEST_USER, password=TEST_PASS)


def test_login_failure(public_client: APIClient) -> None:
    """Test attempts to login to MXCube3 with a non-existent user account.

    Parameters
    ----------
    public_client : APIClient
        Authenticated client session.
    """
    # Ensure that the auth attempt fails as expected.
    with pytest.raises(AuthFailure):
        public_client.login(username="haxor", password="l33t")


def test_login_info(client: APIClient) -> None:
    """Tests the LoginInfo endpoint returns as expected.

    Parameters
    ----------
    client : APIClient
        Authenticated client session.
    """
    # Fetch login info from an authed session
    data = client.login_info()
    assert isinstance(data.get("beamline_name"), str)
    assert data.get("selectedProposal") == "idtest0"
