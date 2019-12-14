from functools import wraps
from flask import session, redirect, url_for, request
from app.utils.verification import generate_verify_image


def valid_login(email, password):
    '''判断是否为正确的用户'''
    from app.models import User

    email_ = User.query.filter(User.email == email).first()
    if email_:
        password_ = email_.check_password_hash(password=password)
    else:
        password_ = None

    return True if password_ else False


def valid_regist(email):
    '''判断用户是否重复注册'''
    from app.models import User
    user = User.query.filter(User.email == email).first()
    return False if user else True


def verfication(pic_name=None):
    strs = generate_verify_image(image_name=pic_name, save_img=True)
    return strs


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('email'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('auth.login', next=request.url))

    return wrapper
