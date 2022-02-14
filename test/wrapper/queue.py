from flask.testing import FlaskClient
from .base import Base

QUEUE_ROUTE = "/queue"


class Queue(Base):
    """Wrapper for MXCube sample queue endpoints.

    Parameters
    ----------
    client : FlaskClient
        Flask test client used to make REST requests.
    base_url : str
        Base URL for accessing the MXCube3 Flask API.
    route : str
        Route where the enpoints can be accessed.
    """

    def __init__(self, client: FlaskClient, base_url: str, route: str = QUEUE_ROUTE) -> None:
        super().__init__(client, base_url, route)

    @property
    def group_folder(self) -> str:
        """Retrieve the current group directory.

        Returns
        -------
        str
            Current group directory.
        """
        data = self.get("/group_folder")
        return data["path"]
