from flask import Blueprint
from backend.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth_bp", __name__)
controller = AuthController()


# =======================
# AUTH
# =======================
auth_bp.route("/login", methods=["POST"])(controller.login)


# =======================
# PROFILE
# =======================
auth_bp.route("/profile/<username>", methods=["GET"])(controller.get_profile)
auth_bp.route("/upload_foto/<username>", methods=["POST"])(controller.upload_foto)
auth_bp.route("/uploads/<filename>", methods=["GET"])(controller.get_foto)
auth_bp.route("/delete_foto/<username>", methods=["DELETE"])(controller.delete_foto)


# =======================
# ACCOUNT
# =======================
auth_bp.route("/update_account", methods=["PUT"])(controller.update_account)
auth_bp.route("/account/<username>", methods=["GET"])(controller.get_account)