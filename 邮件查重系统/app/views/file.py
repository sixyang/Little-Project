import os, zipfile
from redis import Redis
from flask import (request, session, jsonify, send_from_directory, url_for, render_template, Blueprint, send_file)
from app.tasks import jaccard, generate_report
from app.utils.helper import create_dir, docx2pdf, delete_file, unzip
from app.utils.pagination import Pagination
from app.utils.auth_func import login_required
from app import attachment_dir, temp_dir, redis_conn
from shutil import rmtree
from pyecharts import options
from pyecharts.charts import Bar
from xlrd import open_workbook

file = Blueprint('file', __name__)


@login_required
@file.route('/upload_file', methods=['GET'])
def upload_file():
    return render_template('upload_file.html')


@login_required
@file.route('/file/file', methods=['POST'])
def upload_part():  # 接收前端上传的一个分片
    task = request.form.get('task_id')  # 获取文件的唯一标识符
    chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
    filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

    upload_file = request.files['file']
    path = '{0}/{1}'.format(temp_dir, filename)
    upload_file.save(path)  # 保存分片到本地
    return render_template('upload_file.html')


@login_required
@file.route('/file/merge', methods=['GET'])
def upload_success():  # 按序读出分片内容，并写入新文件
    email = session.get('email')
    target_filename = request.args.get('filename')  # 获取上传文件的文件名
    task = request.args.get('task_id')  # 获取文件的唯一标识符
    chunk = 0  # 分片序号

    dirpath = '{0}/{1}'.format(attachment_dir, email)
    if target_filename.endswith('.zip'):
        dirname = '{0}/{1}'.format(dirpath, 'Zips')
        create_dir(dirname)

        final_path = '{0}/{1}'.format(dirname, target_filename)
        with open(final_path, 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = '{0}/{1}{2}'.format(temp_dir, task, chunk)
                    with open(filename, 'rb') as source_file:
                        target_file.write(source_file.read())  # 读取分片内容写入新文件
                except Exception:
                    break
                chunk += 1
                os.remove(filename)  # 删除该分片，节约空间
        savedir = '{0}/{1}'.format(dirpath, target_filename.rsplit('.zip')[0])
        create_dir(savedir)
        unzip(final_path, savedir)

    return render_template('upload_file.html', email=email)


@file.route('/show_upload_attachments', methods=['GET', 'POST'])
@login_required
def show_upload_attachments():
    # 这个函数只展示文件夹
    email = session.get('email')

    path = '{0}/{1}'.format(attachment_dir, email)
    files = os.listdir(path)  # 获取文件目录
    if request.method == "POST":
        dirname = request.form.get('search')
        tmp_dirs = []
        for i in files:
            if i.startswith(dirname) or dirname in i:
                tmp_dirs.append(i)
        files = tmp_dirs

    html = ''
    if len(files) > 1:
        files, html = get_pagination(files)
    return render_template('show_attachments.html', index_list=files, html=html, email=email,
                           root=True, path=None)


def get_files(dirname):
    email = session.get('email')
    upload_dir = '{0}/{1}/{2}'.format(attachment_dir, email, dirname)
    return os.listdir(upload_dir), email


def get_pagination(files):
    # 返回分页，需要获得文件列表，然后进行对其进行分页
    pager = Pagination(request.args.get("page", 1), len(files), request.path, request.args, per_page_count=10)
    index_list = files[pager.start: pager.end]
    html = pager.page_html()
    return index_list, html


@login_required
@file.route('/file/show/<filename>', methods=['GET', 'POST'])
def file_download(filename):
    # 这个函数只展示文件
    files, email = get_files(filename)
    display = 'yes'
    html = ''

    if request.method == 'GET':
        files, html = get_pagination(files)
        if filename.startswith('Zips') or filename.startswith('Xlsx'):
            display = ''
    else:
        tmp_files = []
        target_file = request.form.get('search')
        for i in files:
            if i.startswith(target_file) or target_file in i:
                tmp_files.append(i)
        files = tmp_files
    return render_template('show_attachments.html', index_list=files, html=html, email=email,
                           root=False, path=filename, display=display)


@login_required
@file.route('/file/download_f/<filename>')
def file_download_f(filename):
    filename = filename.replace('~', '/')
    email = session.get('email')
    file_url = '{0}/{1}'.format(attachment_dir, email)
    return send_from_directory(file_url, filename)


@login_required
@file.route('/file/download_a/<dirname>')
def file_download_a(dirname):
    files, email = get_files(dirname)
    zip_path = '{0}/{1}/'.format(attachment_dir, email)
    zip_dir = create_dir(zip_path + 'Zips')
    dir = zip_path + dirname

    zipf = zipfile.ZipFile(zip_dir + '/' + dirname + '.zip', 'w', zipfile.ZIP_DEFLATED)
    pre_len = len(os.path.dirname(dir))
    for parent, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
            zipf.write(pathfile, arcname)
    zipf.close()
    print(dir + '.zip')
    return send_from_directory(zip_path + 'Zips', dirname + '.zip')


@login_required
@file.route('/file/delete', methods=["POST"])
def file_delete():
    email = session.get('email')
    name = request.form.get('file')
    print(name)
    dirpath = name.split('/')[-1].replace('~', '/')
    path = '{0}/{1}/{2}'.format(attachment_dir, email, dirpath)

    try:
        delete_file(path)
    except:
        rmtree(path)
        return 'dir'
    else:
        return 'file'


@login_required
@file.route('/duplicate', methods=['GET', 'POST'])
def duplicate():
    email = session.get('email')
    if request.method == 'POST':
        target_dir = request.form.get('dir')
        redis_conn.set(email + 'xls_path', target_dir)
        if target_dir:
            file_dir = '{0}/{1}/{2}'.format(attachment_dir, email, target_dir)

            xlsx_path = '{0}/{1}/{2}'.format(attachment_dir, email, 'Xlsxs')
            redis_conn.delete(target_dir)
            target_xlsx = '{0}/{1}{2}'.format(xlsx_path, target_dir, '.xlsx')
            print('target_xlsx', target_xlsx)

            if os.path.exists(target_xlsx):
                result = []
                data = open_workbook(filename=target_xlsx)
                table = data.sheets()[0]
                row_nums = table.nrows
                for i in range(row_nums):
                    if i != 0:
                        result.append(table.row_values(i))
                return jsonify({'state': "SUCCESS", 'result': result}), 202, {}

            task = jaccard.apply_async((file_dir, email), serializer='json')
            return jsonify({'state': "no"}), 202, {'Location': url_for('.duplicate_result', task_id=task.id)}
        else:
            return 'no'
    else:
        path = '{0}/{1}'.format(attachment_dir, email)
        files = os.listdir(path)
        index_list, html = get_pagination(files)
        return render_template('duplicate.html', email=email, attachments=files, index_list=index_list, html=html)


@login_required
@file.route('/duplicate_result/<task_id>')
def duplicate_result(task_id):
    result = []
    email = session.get('email')
    task = jaccard.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        conn = Redis(host='127.0.0.1', port=6379, db=1)
        name = email + ':duplicate_result'
        res = conn.hgetall(name)

        for k, v in res.items():
            new_k = k.decode('utf-8')
            new_v = v.decode('utf-8')
            splited_v = new_v.rsplit(',', 1)
            splited_v.insert(0, new_k)
            result.append(splited_v)
            result.sort(key=lambda x: x[2], reverse=True)

        generate_report.apply_async((email,), serializer='json')  # 这里直接在查重完成后就生成报表
        redis_conn.delete(email + 'dump')
        redis_conn.delete(email + 'xls_path')

    progress = redis_conn.get(email + 'dump')
    response = {'state': task.state, 'result': result}
    if progress:
        progress = progress.decode('utf8')
        response['progress'] = progress
    return jsonify(response)


@login_required
@file.route('/file/download_x/<filename>')
def download_x(filename):
    email = session.get('email')
    save_path = attachment_dir + '/' + email + '/Xlsxs/'
    print(save_path)
    return send_from_directory(save_path, filename + '.xlsx')


@login_required
@file.route('/file/draw/<filename>')
def draw(filename):
    email = session.get('email')
    xlsxpath = '{0}/{1}/{2}/{3}.xlsx'.format(attachment_dir, email, 'Xlsxs', filename)
    data = open_workbook(xlsxpath)
    table = data.sheets()[0]
    target_file = table.col_values(0)[1:]
    print(target_file)
    dup_files = table.col_values(1)[1:]
    rate = table.col_values(2)[1:]

    c = (
        Bar()
            .add_xaxis(target_file)
            .add_xaxis(dup_files)
            .add_yaxis("相似率", rate)
            .set_global_opts(title_opts=options.TitleOpts(title="邮件查重结果", subtitle='请勿刷新页面，否则结果将丢失'))
    )
    return c.dump_options_with_quotes()


@login_required
@file.route('/file/draw_new')
def new_draw():
    return render_template('duplicate_pic.html')


@login_required
@file.route('/file/read_online/<filename>')
def read_online(filename=None):
    email = session.get('email')
    if not filename.endswith('.docx'):
        path = '{0}/{1}/{2}'.format(attachment_dir, email, filename)
        files = os.listdir(path)  # 获取文件目录

        return render_template('read_online.html', attachments=files, email=email, root=True, path=filename)
    else:

        name = filename.split('-')
        dirpath = '{0}/{1}'.format(attachment_dir, email)
        filepath = '{0}/{1}/{2}'.format(dirpath, name[-2], name[-1])

        output = (dirpath + '/Webpages/' + name[-1]).replace('.docx', '.html')
        if not os.path.exists(output):
            docx2pdf(filepath, dirpath, output)
        return send_file(output)
