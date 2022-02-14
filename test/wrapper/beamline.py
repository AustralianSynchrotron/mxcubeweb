from flask.testing import FlaskClient
from .base import Base

BEAMLINE_ROUTE = "/beamline"


class Beamline(Base):
    """Wrapper for MXCube beamline endpoints.

    Parameters
    ----------
    client : FlaskClient
        Flask test client used to make REST requests.
    base_url : str
        Base URL for accessing the MXCube3 Flask API.
    route : str
        Route where the enpoints can be accessed.
    """

    def __init__(self, client: FlaskClient, base_url: str, route: str = BEAMLINE_ROUTE) -> None:
        """[summary]

        Parameters
        ----------
        client : FlaskClient
            [description]
        base_url : str
            [description]
        route : str, optional
            [description], by default BEAMLINE_ROUTE
        """
        super().__init__(client, base_url, route)

    @property
    def datapath(self) -> str:
        """Retrieve the current data directory.

        Returns
        -------
        str
            Current data directory.
        """
        data = self.get("/datapath")
        return data["path"]
