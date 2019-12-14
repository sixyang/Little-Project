from app.models import User, db
from flask import request, session, redirect, render_template, url_for, Blueprint
from app.utils.auth_func import valid_login, valid_regist, verfication
from app.utils.send_code import send_email
from app.utils.helper import create_dir
from time import time
from random import randint
from app.utils.forms import NameForm
from app import attachment_dir

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    forms = NameForm()
    pic_name = str(time()) + '.png'
    pic_url = 'static/pictures/' + pic_name

    if request.method == "GET":
        verfy_code = verfication(pic_name=pic_name)
        session['verfy_code'] = verfy_code
        print(verfy_code)

    if request.method == 'POST':
        verfy_code = session.get('verfy_code')
        email = request.form['email']
        password = request.form['password']

        if valid_login(email, password):
            if request.form['verfy'] == verfy_code:
                session['email'] = request.form.get('email')
                return 'ok'
            else:
                return 'verfy'
        else:
            return 'wrong'

    return render_template('login.html', pic=pic_url, form=forms)


@auth.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('base.home'))


@auth.route('/regist', methods=['GET', 'POST'])
def regist():
    pic_name = str(time()) + '.png'
    pic_url = 'static/pictures/' + pic_name

    if request.method == "GET":
        verfy_code = verfication(pic_name=pic_name)
        session['verfy_code'] = verfy_code
        print(verfy_code)

    if request.method == 'POST':
        verfy_code = session.get('verfy_code')
        email = request.form['email']
        password1 = request.form['password1']

        if request.form['password1'] != request.form['password2']:
            return 'dump'
        elif valid_regist(request.form['email']):
            if request.form['verfy'] == verfy_code:
                user = User(email=email)
                user.password(password1)
                db.session.add(user)
                db.session.commit()

                session['email'] = email
                send_email(email, '您已注册邮件查重网站', '注册')

                user_dir = '{0}/{1}'.format(attachment_dir, email)
                create_dir(user_dir)
                return 'ok'
            else:
                return 'verfy'

    return render_template('regist.html', pic=pic_url)

@auth.route('/verfy')
def verfy():
    pic_name = str(time()) + '.png'
    pic_url = 'static/pictures/' + pic_name
    verfy_code = verfication(pic_name=pic_name)
    session['verfy_code'] = verfy_code
    return pic_url

@auth.route('/forget', methods=['GET', 'POST'])
def forget():
    '''忘记密码'''
    fill = None
    if request.method == 'POST':
        get_verfy_code = request.form.get('code')


        if get_verfy_code:
            # 说明这里只是来请求验证码的。
            email_exists = True
            email = request.form.get('email')
            #TODO 查询数据库，看有没有这个邮箱！
            content_num = randint(1000, 9999)
            session['content_num'] = content_num

            print(content_num)
            content = '''
                <p>您的验证码为 <h3>{}</h3> </p>
            '''.format(str(content_num))
            ret = send_email(email, content, '更改密码的验证码')
            if email_exists and not ret:
                session['m_email'] = email
                return 'yes'
            else:
                return 'no'
        else:
            #说明这里是来请求修改密码的。
            content_num = session.get('content_num')
            verfy_code = request.form.get('verfy_code')
            print(verfy_code, content_num)
            if verfy_code:
                if int(verfy_code) == content_num:
                    return 'ok'
                else:
                    return 'no'
            else:
                return 'none'

    return render_template('forget.html', fill=fill)

@auth.route('/modify', methods=['GET', 'POST'])
def modify():
    m_email = session.get('m_email')
    if session.get('m_email'):
        if request.method == 'POST':
            email = request.form.get('email')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            if email == m_email:
                if password1 == password2:
                    user = User.query.filter(User.email == email).first()
                    if user:
                        user.password(password1)
                        db.session.add(user)
                        db.session.commit()
                        return 'ok'
                    else:
                        return 'no'
                else:
                    return 'incorrect'
            else:
                return 'invalid'

        return render_template('modify.html', m_email=m_email)
    else:
        return redirect('/home')