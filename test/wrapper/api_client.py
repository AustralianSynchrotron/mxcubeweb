from flask.testing import FlaskClient
from .base import Base
from .exceptions import AuthFailure
from .ra import RemoteAccess
from .diffractometer import Diffractometer
from .beamline import Beamline
from .sample_changer import SampleChanger
from .queue import Queue

TEST_USER = "idtest0"
TEST_PASS = "password"
TEST_BASE_URL = "/mxcube/api/v0.1"


class APIClient(Base):
    """ Simple wrapper to call MXCube Flask API endpoints programmatically. """

    def __init__(self, client: FlaskClient, base_url: str = TEST_BASE_URL) -> None:
        """
        Parameters
        ----------
        client : FlaskClient
            Flask test client to be used when making calls to the API endpoints.
        base_url : str, optional
            Base URL for all REST endpoints, by default TEST_BASE_URL.
        """
        self._client = client
        self._base_url = base_url
        super().__init__(self._client, self._base_url, "")

    @property
    def remote_access(self) -> RemoteAccess:
        """Provides access to the wrapper for the remote access endpoints.

        Returns
        -------
        RemoteAccess
            Wrapper for the remote access endpoints.
        """
        return RemoteAccess(self._client, self._base_url)

    @property
    def diffractometer(self) -> Diffractometer:
        """Provides access to the wrapper for the diffractometer endpoints.

        Returns
        -------
        Diffractometer
            Wrapper for the remote access endpoints.
        """
        return Diffractometer(self._client, self._base_url)

    @property
    def beamline(self) -> Beamline:
        """Provides access to the wrapper for the beamline endpoints.

        Returns
        -------
        Beamline
            Wrapper for the remote access endpoints.
        """
        return Beamline(self._client, self._base_url)

    @property
    def sample_changer(self) -> SampleChanger:
        """Provides access to the wrapper for the sample changer endpoints.

        Returns
        -------
        SampleChanger
            Wrapper for the remote access endpoints.
        """
        return SampleChanger(self._client, self._base_url)

    @property
    def queue(self) -> Queue:
        """Provides access to the wrapper for the sample queue endpoints.

        Returns
        -------
        Queue
            Wrapper for the remote access endpoints.
        """
        return Queue(self._client, self._base_url)

    def login(self, username: str, password: str) -> None:
        """Authenticate session with the MXCube3 REST API.

        Note:
            The mocked ISPyB connection does not seem to care what password is
            passed in the request. Any password provided will result in a successful
            login.

        Parameters
        ----------
        username : str
            User username.
        password : str
            User password.
        """
        data = self.post("/login/", {"proposal": username, "password": password}, expected_codes=[200, 302], is_json=False)
        if data.get("code") != "ok":
            raise AuthFailure("Failed to authenticate with the MXCube API!")

    def login_info(self) -> dict:
        """Calls the login info endpoint.

        Returns
        -------
        dict
            Contains details about connected users and the running experiment.
        """
        return self.get("/login/login_info")

    def signout(self) -> None:
        """Calls the signout endpoint to log out of the user session.
        """
        self.get("/login/signout", headers={"Connection": "close"}, is_json=False)
