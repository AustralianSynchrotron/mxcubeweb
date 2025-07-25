import logging

from flask import (
    Blueprint,
    jsonify,
    make_response,
    redirect,
    request,
    session,
    url_for,
)
from flask_login import current_user
from mxcubecore import HardwareRepository as HWR

from mxcubeweb.core.util import networkutils


def init_route(app, server, url_prefix):
    bp = Blueprint("login", __name__, url_prefix=url_prefix)

    @bp.route("/", methods=["POST"])
    def login():
        """
        Login into mxcube application.

        :returns: Response Object, Content-Type: application/json, an object
        containing following info:

        {'status':{ 'code': 'ok', 'msg': msg },
            'Proposal': proposal,
            'session': todays_session,
            'local_contact': local_contact,
            'person': someone,
            'laboratory': a_laboratory]}

        Status code set to:
        200: On success
        409: Error, could not log in
        """
        params = request.get_json()
        login_id = params.get("proposal", "")
        password = params.get("password", "")

        try:
            app.usermanager.login(login_id, password)
        except Exception:
            msg = "[LOGIN] User %s could not login" % login_id
            logging.getLogger("MX3.HWR").exception(msg)
            res = make_response(
                jsonify({"msg": "Authentication failed"}),
                200,
            )
        else:
            res = make_response(jsonify({"msg": ""}), 200)

        return res

    @bp.route("/sso_post_logout", methods=["GET"])
    @server.restrict
    def ssosignout():
        app.usermanager.signout()
        return redirect("/")

    @bp.route("/ssologin", methods=["GET"])
    def ssosignin():
        redirect_uri = url_for("login.auth", _external=True, _scheme="https")
        response = app.usermanager.oauth_client.keycloak.authorize_redirect(
            redirect_uri
        )
        return response

    @bp.route("/auth", methods=["GET"])
    def auth():
        try:
            app.usermanager.sso_validate()
        except Exception:
            return redirect("/login")
        else:
            return redirect("/datacollection")

    @bp.route("/signout")
    @server.restrict
    def signout():
        """
        Signout from MXCuBE Web and reset the session
        """
        app.usermanager.signout()
        return make_response(jsonify(""), 200)

    @bp.route("/login_info", methods=["GET"])
    def login_info():
        """
        Retrieve session/login info

        :returns: Response Object, Content-Type: application/json, an object
                containing:

        {'synchrotron_name': synchrotron_name,
        'beamline_name': beamline_name,
        'loginType': loginType,
        'loggedIn': True,
        'Proposal': proposal, 'session': todays_session,
        'local_contact': local_contact,
        'person': someone,
        'laboratory': a_laboratory']}}

        Status code set to:
        200: On success
        200: Error, could not log in, {"loggedIn": False}
        """
        res = app.usermanager.login_info()

        if res["loggedIn"]:
            session.permanent = True

        return jsonify(res)

    @bp.route("/send_feedback", methods=["POST"])
    @server.restrict
    def send_feedback():
        sender_data = request.get_json()
        sender_data["LOGGED_IN_USER"] = current_user.nickname
        networkutils.send_feedback(sender_data)
        return make_response("", 200)

    @bp.route("/refresh_session", methods=["GET"])
    @server.restrict
    def refresh_session():
        # Since default value of `SESSION_REFRESH_EACH_REQUEST` config setting is `True`
        # there is no need to do anything to refresh the session.
        app.usermanager.update_active_users()
        app.usermanager.handle_sso_logout()
        return make_response("", 200)

    return bp
