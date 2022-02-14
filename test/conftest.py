# -*- coding: utf-8 -*-
""" Helper functions for pytest """
from gevent import monkey
from wrapper.api_client import TEST_PASS, TEST_USER, APIClient

monkey.patch_all(thread=False)

import os  # noqa: E402
import sys  # noqa: E402

import pytest  # noqa: E402

MXCUBE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../mxcube3/")
)

MXCUBE_CONF = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "./HardwareObjectsMockup.xml/mxcube-server-config.yml",
    )
)

sys.path.append(MXCUBE_ROOT)
sys.path.append("./")

from mxcube3 import Server, mxcube, parse_args, server  # noqa: E402
from mxcube3.config import Config  # noqa: E402


class TestConfig(Config):
    def __init__(self, fpath=None):
        super().__init__(fpath=fpath)
        self.flask.TESTING = True


@pytest.fixture(autouse=True, scope="session")
def flask_server():
    """
    Fixture loads the MXCube3 server and Flask routes.
    """
    cmdline_options = parse_args()[0]
    cfg = TestConfig(fpath=MXCUBE_CONF)
    server.init(None, cfg, None)
    mxcube.init(
        server,
        cmdline_options.hwr_directory,
        cmdline_options.allow_remote,
        cmdline_options.ra_timeout,
        cmdline_options.video_device,
        cmdline_options.log_file,
        cfg,
    )
    server.register_routes(mxcube)
    yield server


@pytest.fixture
def public_client(flask_server: Server):
    """
    Fixture yields a public client session.
    """
    api_client = APIClient(client=flask_server.flask.test_client())
    yield api_client


@pytest.fixture
def client(flask_server: Server) -> APIClient:
    """
    Fixture yields an authenticated client session.
    """
    api_client = APIClient(client=flask_server.flask.test_client())
    api_client.login(username=TEST_USER, password=TEST_PASS)

    # The MXCube3 API restricts certain API endpoints to a single user session.
    # This is known as the master session and will by default be the first authed
    # session to connect to the server, with all subsequent conections considered
    # observers with limited permissions to view the current experiment.

    # For test repeatability we will insure this client instance is the master session.
    api_client.remote_access.post("/take_control", data={})
    yield api_client
    api_client.signout()
