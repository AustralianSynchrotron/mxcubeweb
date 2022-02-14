class MXCubeAPIError(Exception):
    """ MXCube API wrapper base exception. """

class AuthFailure(MXCubeAPIError):
    """Raised when there is a general authentication error
    when communicating with the MXCube API.
    """
