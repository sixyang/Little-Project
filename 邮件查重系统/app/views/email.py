from app import redis_conn
from flask import session, render_template, jsonify, request, url_for, Blueprint, flash
from app.utils.auth_func import login_required
from app.utils.helper import to_timestamp
from app.tasks import download_email, send_remail
# from app.utils.logger import lg
from os import listdir

email = Blueprint('email', __name__)


@email.route('/save_emails', methods=['GET', 'POST'])
@login_required
def save_emails():
    email = session.get('email')
    return render_template('save_emails.html', email=email)


# TODO email_password在网络上传送的安全问题
@login_required
@email.route('/email_status', methods=['POST'])
def email_status():
    email = session.get('email')
    email_password = request.form['email_password']
    #TODO 设置一下登陆密码错误的解决办法
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    report_name = request.form['report_name']
    receipt_ctx = request.form['receipt_ctx']
    send_email = request.form['send_email']

    if send_email == 'on':
        print("发送邮件！")
        redis_conn.set(email + '_password', email_password)
        redis_conn.hset(email + ':receipt', send_email, receipt_ctx)
    if all([email, email_password, start_time, end_time, report_name]):
        start_time = to_timestamp(start_time)
        end_time = to_timestamp(end_time)

        info = (email, email_password, start_time, end_time, report_name)
        task = download_email.apply_async(info, serializer='json')
        print(task, task.state)
        return jsonify({'code': 'ok'}), 200, {'Location': url_for('.save_emails_status', task_id=task.id)}
    else:
        return jsonify({'code': 'no'}), 200, None


@email.route('/save_emails_status/<task_id>')
def save_emails_status(task_id):
    task = download_email.AsyncResult(task_id)

    progress_num = session.get('email')+'download_progress'
    progress = redis_conn.get(progress_num)
    if progress:
        progress = progress.decode('utf8')
    redis_conn.delete(progress_num)
    response = {'state': task.state, 'progress': progress}
    return jsonify(response)

@email.route('/show_attachments')
@login_required
def show_attachments():
    email = session.get('email')
    save_dir = redis_conn.get('save_dir' + email)
    redis_conn.delete(save_dir)
    save_dir = save_dir.decode("utf8")
    path = save_dir.split('/')[-1]
    res = []

    task = send_remail.apply_async((email,), serializer='json') #向学生发送回执邮件

    try:
        attachments = listdir(save_dir)
        for attach in attachments:
            res.append(attach)
    except:
        pass
    return render_template('show_attachments.html', index_list=res, email=email, root=True, path=path, stask_id=task.id)
#stask_id 是为了在全站显示发送回执邮件成功。

@email.route('/back_mail/<task_id>')
@login_required
def back_mail(task_id):
    task = send_remail.AsyncResult(task_id)
    response = {'state': task.state}
    if task.state == 'SUCCESS':
        flash('回执邮件发送成功！')
    return jsonify(response)
