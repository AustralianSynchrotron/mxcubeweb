import json
from typing import List, Union

from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from .exceptions import MXCubeAPIError


class Base:
    """Base API wrapper class, provides common methods to access the REST endpoints.

    Parameters
    ----------
    client : FlaskClient
        Flask test client used to make REST requests.
    base_url : str
        Base URL for accessing the MXCube3 Flask API.
    route : str
        Route where the enpoints can be accessed.
    """

    def __init__(self, client: FlaskClient, base_url: str, route: str) -> None:
        self._client = client
        self._base_url = base_url
        self._route = route

    def _check_response(
        self, response: TestResponse, expected_codes: List[int], is_json: bool
    ) -> None:
        """Check the REST response for signs that the
        request resulted in an error state.

        Parameters
        ----------
        response : TestResponse
            Response object returned by the REST request.
        expected_codes : List[int]
            List of expected status codes.
            If the response status is outside what is expected,
            this would indicate an error.
        is_json : bool
            True if we are expecting the reponse to return a JSON object,
            False if it's not expected.

        Raises
        ------
        MXCubeAPIError
            When the REST response indicates an error has occured.
        """
        if (
            response.status_code not in expected_codes
            or is_json
            and not response.is_json
        ):
            raise MXCubeAPIError(response.data.decode("utf-8"))

    def get(
        self,
        endpoint: str,
        headers: dict = None,
        expected_codes: List[int] = [200],  # noqa: B006
        is_json: bool = True,
    ) -> Union[dict, list, int, float, str, None]:
        """Performs a GET request to the MXCube3 REST API and validates the request
        did not result in an error state occurring.

        Parameters
        ----------
        endpoint : str
            Endpoint to target when making the GET request.
        headers : dict, optional
            Headers to pass with the GET request, by default {}.
        expected_codes : List[int], optional
            List of expected status codes.
            If the response status is outside what is expected,
            this would indicate an error, by default [200].
        is_json : bool, optional
            True if we are expecting the reponse to return a JSON object,
            False if it's not expected, by default True.

        Returns
        -------
        Union[dict, list, int, float, str, None]
            Converted JSON object if data was returned in the response.
        """
        resp = self._client.get(
            "".join([self._base_url, self._route, endpoint]), headers=headers
        )
        self._check_response(resp, expected_codes, is_json)
        return resp.json

    def post(
        self,
        endpoint: str,
        data: Union[dict, list, int, float, str],
        headers: dict = None,
        expected_codes: List[int] = [200],  # noqa: B006
        is_json: bool = False,
    ) -> Union[dict, list, int, float, str, None]:
        """Performs a POST request to the MXCube3 REST API and validates the request
        did not result in an error state occurring.

        Parameters
        ----------
        endpoint : str
            Endpoint to target when making the POST request.
        data : Union[dict, list, int, float, str]
            Data to be converted into a JSON objet and sent as part of the request.
        headers : dict, optional
            Headers to pass with the POST request, by default {}.
        expected_codes : List[int], optional
            List of expected status codes.
            If the response status is outside what is expected,
            this would indicate an error, by default [200].
        is_json : bool, optional
            True if we are expecting the reponse to return a JSON object,
            False if it's not expected, by default False.

        Returns
        -------
        Union[dict, list, int, float, str, None]
            Converted JSON object if data was returned in the response.
        """
        resp = self._client.post(
            "".join([self._base_url, self._route, endpoint]),
            data=json.dumps(data),
            headers=headers,
            content_type="application/json",
        )
        self._check_response(resp, expected_codes, is_json)
        return resp.json

    def put(
        self,
        endpoint: str,
        data: Union[dict, list, int, float, str],
        headers: dict = None,
        expected_codes: List[int] = [200],  # noqa: B006
        is_json: bool = False,
    ) -> Union[dict, list, int, float, str, None]:
        """Performs a PUT request to the MXCube3 REST API and validates the request
        did not result in an error state occurring.

        Parameters
        ----------
        endpoint : str
            Endpoint to target when making the PUT request.
        data : Union[dict, list, int, float, str]
            Data to be converted into a JSON objet and sent as part of the request.
        headers : dict, optional
            Headers to pass with the PUT request, by default {}.
        expected_codes : List[int], optional
            List of expected status codes.
            If the response status is outside what is expected,
            this would indicate an error, by default [200].
        is_json : bool, optional
            True if we are expecting the reponse to return a JSON object,
            False if it's not expected, by default False.

        Returns
        -------
        Union[dict, list, int, float, str, None]
            Converted JSON object if data was returned in the response.
        """
        resp = self._client.put(
            "".join([self._base_url, self._route, endpoint]),
            data=json.dumps(data),
            headers=headers,
            content_type="application/json",
        )
        self._check_response(resp, expected_codes, is_json)
        return resp.json
