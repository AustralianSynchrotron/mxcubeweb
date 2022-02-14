from flask.testing import FlaskClient
from .base import Base

RA_ROUTE = "/ra"


class RemoteAccess(Base):
    """Wrapper for MXCube remote access endpoints.

    Parameters
    ----------
    client : FlaskClient
        Flask test client used to make REST requests.
    base_url : str
        Base URL for accessing the MXCube3 Flask API.
    route : str
        Route where the enpoints can be accessed.
    """

    def __init__(self, client: FlaskClient, base_url: str, route: str = RA_ROUTE) -> None:
        super().__init__(client, base_url, route)

    @property
    def is_master(self) -> bool:
        """Check if the client holds the current master session.

        Returns
        -------
        bool
            True if the session is the master session.
        """
        data = self.get("/")
        return data["data"]["master"]

    @property
    def control_requested(self) -> bool:
        """Check if a user is requesting control of the beamline.

        Returns
        -------
        bool
            True if there is at least one user requesting control.
        """
        data = self.get("/")
        return any(
            map(
                lambda observer: observer.get("requestsControl", False),
                data["data"]["observers"]
            )
        )

    @property
    def sid(self) -> str:
        """Session identifier for the current user session.

        This session identifier is generated automatically by Flask
        and can be used to differentiate between users who may be
        connected to the beamline using a shared login.

        Returns
        -------
        str
            Client's session identifier (SID)
        """
        data = self.get("/")
        return data["data"]["sid"]

    @property
    def allow_remote(self) -> bool:
        """Check if users are allowed to connect from an external network.

        Returns
        -------
        bool
            True if enabled, otherwise False.
        """
        data = self.get("/")
        return data["data"]["allowRemote"]

    @property
    def timeout_gives_control(self) -> bool:
        """Check if requests for control will auto-approve after a set timeout,
        if there is no response from the user with the master session.

        Returns
        -------
        bool
            True if enabled, otherwise False.
        """
        data = self.get("/")
        return data["data"]["timeoutGivesControl"]
