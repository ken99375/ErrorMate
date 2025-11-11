from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

# ログイン画面
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # すでにログインしていたらトップへ飛ばす
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # フォームからメールアドレスとパスワードを取得
        mail = request.form.get('mail')
        password = request.form.get('password')

        # ユーザーを検索
        user = User.query.filter_by(mail=mail).first()

        # ユーザーが存在し、パスワードが合っていればログイン
        if user is not None and user.verify_password(password):
            login_user(user)
            flash('ログインしました。')
            
            # ログインが必要なページから飛ばされてきた場合は元のページへ、
            # そうでなければメニュー画面（main.index）へリダイレクト
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index')) # ← ここでメニュー画面へ飛ぶ
        else:
            flash('メールアドレスまたはパスワードが誤っています。', 'error')

    return render_template('auth/login.html')
# ログアウト機能
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。')
    return redirect(url_for('auth.login'))

# 開発用サインアップ機能（ここを追加！）
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # フォームからデータを受け取る
        user_name = request.form.get('user_name')
        mail = request.form.get('mail')
        password = request.form.get('password')
        role = request.form.get('role')

        # すでに登録済みかチェック
        if User.query.filter_by(mail=mail).first():
            flash('そのメールアドレスは既に登録されています。', 'error')
            return redirect(url_for('auth.signup'))

        # 新しいユーザーを作成して保存
        new_user = User(user_name=user_name, mail=mail, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('アカウントを作成しました。ログインしてください。')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')