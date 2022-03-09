from flask.testing import FlaskClient

from .base import Base

DIFFRACTOMETER_ROUTE = "/diffractometer"


class Diffractometer(Base):
    """Wrapper for MXCube diffractometer endpoints.

    Parameters
    ----------
    client : FlaskClient
        Flask test client used to make REST requests.
    base_url : str
        Base URL for accessing the MXCube3 Flask API.
    route : str
        Route where the enpoints can be accessed.
    """

    def __init__(
        self, client: FlaskClient, base_url: str, route: str = DIFFRACTOMETER_ROUTE
    ) -> None:
        super().__init__(client, base_url, route)

    @property
    def phase(self) -> str:
        """Retrieve the current phase in the diffractometer.

        Returns
        -------
        str
            Current phase in the diffractometer.
        """
        data = self.get("/phase")
        return data["current_phase"]

    @property
    def aperture(self) -> int:
        """Retrieve the current aperture setting for the diffractometer.

        Returns
        -------
        int
            Current aperture setting for the diffractometer.
        """
        data = self.get("/aperture")
        return data["currentAperture"]

    @property
    def md_in_plate_mode(self) -> bool:
        """Retrieve the current plate mode setting for the diffractometer.

        Returns
        -------
        bool
            Current plate mode setting for the diffractometer.
        """
        data = self.get("/platemode")
        return data["md_in_plate_mode"]
