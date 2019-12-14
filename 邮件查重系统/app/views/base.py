from app.utils.auth_func import login_required
from flask import session, render_template, Blueprint,request
from app.models import User

base = Blueprint('base', __name__)


@base.route('/')
@base.route('/home')
def home():
    return render_template('home.html', email=session.get('email'))


@base.route('/panel')
@login_required
def panel():
    email = session.get('email')
    user = User.query.filter(User.email == email).first()
    return render_template('panel.html', user=user, email=email)


@base.route('/help')
def help():
    email = session.get('email')
    return render_template('help.html', email=email)

# 反馈示例
@base.route('/feedback', methods=['GET', 'POST'])
def feedback():
    message = None
    email = session.get('email')
    if request.method == 'POST':
        contact = request.form['contact_way']
        fb = request.form['feedback']
        if contact and fb != '':
            message = '发送成功!'
    return render_template('feedback.html', message=message, email=email)



