from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        mail = (request.form.get("mail") or "").strip().lower()
        password = request.form.get("password") or ""

        if not mail or not password:
            flash("メールアドレスとパスワードを入力してください", "warning")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(mail=mail).first()
        if not user or not user.password_hash:
            flash("メールアドレスまたはパスワードが違います", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password_hash, password):
            flash("メールアドレスまたはパスワードが違います", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)

        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.index"))

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
        user = User(
            mail="dev@local",
            username="dev",
            full_name="dev",
            role="teacher",
            organization_code=None,
            moodle_user_id=None,
            password_hash=generate_password_hash("devpass123")  # 開発用
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("main.index"))


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "GET":
        return render_template("auth/signup.html")

    # フォームから取得（DBカラムに合わせる）
    full_name = (request.form.get("full_name") or "").strip()
    username = (request.form.get("username") or "").strip()
    mail = (request.form.get("mail") or "").strip().lower()
    password = request.form.get("password") or ""
    role = (request.form.get("role") or "student").strip()
    organization_code = (request.form.get("organization_code") or "").strip() or None

    # username未入力ならメールの@前を入れる（便利）
    if not username and mail:
        username = mail.split("@")[0]

    # 最低限チェック
    if not mail or not password:
        return render_template("auth/signup.html", error="メールアドレスとパスワードは必須です"), 400
    if len(password) < 4:
        return render_template("auth/signup.html", error="パスワードは4文字以上にしてください"), 400
    if User.query.filter_by(mail=mail).first():
        return render_template("auth/signup.html", error="そのメールアドレスは既に登録されています"), 400

    pw_hash = generate_password_hash(password)

    u = User(
        mail=mail,
        password_hash=pw_hash,
        role=role,
        organization_code=organization_code,
        username=username or None,
        full_name=full_name or None,
        moodle_user_id=None,
    )
    db.session.add(u)
    db.session.commit()

    login_user(u)
    return redirect(url_for("main.index"))
