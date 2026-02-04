from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        # ログインしていない場合
        if 'user_id' not in session:
            flash('ログインが必要です', 'error')

            # 元いたページを記憶（ログイン後に戻すため）
            return redirect(
                url_for('auth.login', next=request.path)
            )

        return view_func(*args, **kwargs)

    return wrapped_view
