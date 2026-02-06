from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        mail = (request.form.get("mail") or "").strip().lower()
        if not mail:
            flash("メールを入力してください", "warning")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(mail=mail).first()
        if not user:
            username = mail.split("@")[0] if "@" in mail else mail
            user = User(mail=mail, username=username, role=None, moodle_user_id=None)
            db.session.add(user)
            db.session.commit()

        login_user(user)

        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.index"))

    # ★ templates/auth/login.html を参照
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth_bp.route("/dev-login")
def dev_login():
    if not current_app.config.get("ENABLE_DEV_LOGIN", False):
        return ("Not Found", 404)

    user = User.query.order_by(User.user_id.asc()).first()
    if not user:
        user = User(mail="dev@local", username="dev", role=None, moodle_user_id=None)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("main.index"))

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")

    username = (request.form.get("username") or "").strip()
    mail = (request.form.get("mail") or "").strip().lower()
    password = request.form.get("password") or ""
    role = (request.form.get("role") or "student").strip()

    # 最低限チェック
    if not mail or not password:
        return render_template("auth/signup.html", error="メールアドレスとパスワードは必須です"), 400

    # 既に同じメールがいるなら弾く（推奨）
    if User.query.filter_by(mail=mail).first():
        return render_template("auth/signup.html", error="そのメールアドレスは既に登録されています"), 400

    u = User(username=username, mail=mail, role=role)
    u.set_password(password)  # 卒制用の簡易版（平文保存）
    db.session.add(u)
    db.session.commit()

    login_user(u)
    return redirect(url_for("main.index"))  # ←あなたのトップに合わせて