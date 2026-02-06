import os
from flask import Blueprint, request, redirect, url_for, jsonify, session
from pylti1p3.contrib.flask import (
    FlaskOIDCLogin,
    FlaskMessageLaunch,
    FlaskCookieService,
    FlaskRequest
)
from pylti1p3.tool_config import ToolConfDict
from flask_login import login_user
from models import db, User

lti_bp = Blueprint("lti", __name__, url_prefix="/lti")

# ---------------------------------------------------
# HTTP環境用 Cookie Service
# ---------------------------------------------------
class HttpCookieService(FlaskCookieService):
    def __init__(self, flask_request: FlaskRequest):
        super().__init__(flask_request)
        self._cookie_secure = False
        self._cookie_samesite = "None"



# ---------------------------------------------------
# LTI設定
# ---------------------------------------------------
def get_lti_config():
    settings = {
        "client_id": "SVoztigx4Gmmv78",
        "auth_login_url": "http://54.208.71.44/mod/lti/auth.php",
        "auth_token_url": "http://54.208.71.44/mod/lti/token.php",
        "key_set_url": "http://54.208.71.44/mod/lti/certs.php",
        "private_key_file": "/home/ec2-user/environment/ErrorMate/keys/private.key",
        "public_key_file": "/home/ec2-user/environment/ErrorMate/keys/public.key",
        "deployment_ids": ["1"],
        "launch_url": "http://54.208.71.44/errormate/lti/launch",
    }

    return ToolConfDict({
        "http://54.208.71.44": settings,
        "http://54.208.71.44/": settings,
    })


# ---------------------------------------------------
# LTI Login
# ---------------------------------------------------
@lti_bp.route("/login", methods=["GET", "POST"])
def lti_login():
    print("--- OIDC LOGIN START ---")
    try:
        tool_config = get_lti_config()

        flask_request = FlaskRequest()

        oidc_login = FlaskOIDCLogin(
            flask_request,
            tool_config,
            cookie_service=HttpCookieService(flask_request),
        )
        
        print("LOGIN SESSION:", dict(session))

        return oidc_login.enable_check_cookies().redirect(
            request.values.get("target_link_uri")
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500




# ---------------------------------------------------
# LTI Launch
# ---------------------------------------------------
@lti_bp.route("/launch", methods=["POST"])
def lti_launch():
    print("--- LTI LAUNCH RECEIVED ---")
    try:
        tool_config = get_lti_config()

        flask_request = FlaskRequest()

        message_launch = FlaskMessageLaunch(
            flask_request,
            tool_config,
            cookie_service=HttpCookieService(flask_request),
        )

        launch_data = message_launch.get_launch_data()
        print("LAUNCH SESSION:", dict(session))

        return "OK"

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Launch failed", "details": str(e)}), 500


 