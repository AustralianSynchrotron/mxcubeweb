from flask.testing import FlaskClient
from .base import Base

SAMPLE_CHANGER_ROUTE = "/sample_changer"


class SampleChanger(Base):
    """Wrapper for MXCube sample changer endpoints.

    Parameters
    ----------
    client : FlaskClient
        Flask test client used to make REST requests.
    base_url : str
        Base URL for accessing the MXCube3 Flask API.
    route : str
        Route where the enpoints can be accessed.
    """

    def __init__(self, client: FlaskClient, base_url: str, route: str = SAMPLE_CHANGER_ROUTE) -> None:
        super().__init__(client, base_url, route)

    @property
    def state(self) -> str:
        """Retrieve the current state of the sample changer.

        Returns
        -------
        str
            Current state of the sample changer.
        """
        data = self.get("/state")
        return data["state"]
