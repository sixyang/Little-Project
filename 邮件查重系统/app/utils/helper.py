from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from app import redis_conn
import poplib
import os
import email
import yagmail
from datetime import datetime, timedelta
import time
from pydocx import PyDocX
import zipfile
from pathlib import Path
# from app.utils.logger import lg

# 可执行文件拓展名
LEGAL_EXTENSION = ['docx']
# LEGAL_EXTENSION = ['docx', 'doc', 'txt']


def to_timestamp(date_time):
    """将形如2019-4-18日这种格式转换为时间戳（10位）"""
    time_array = time.strptime(date_time, "%Y-%m-%d")
    timestamp = time.mktime(time_array)
    return timestamp


def allowed_file(filename):
    """检查文件名是否合法"""
    return '.' in filename and filename.split('.')[-1] in LEGAL_EXTENSION


def get_smtp_host(email):
    """获取邮箱对应的服务商的SMTP服务器地址"""
    maps = {
        'qq.com': 'smtp.qq.com',
        'gmail.com': 'smtp.gmail.com',
        '126.com': 'smtp.126.com',
        '163.com': 'smtp.163.com',
        'sohu.com': 'smtp.sohu.com',
        'sina.com': 'smtp.sina.com',
        '139.com': 'smtp.139.com',
        'foxmail.com': 'smtp.foxmail.com'
    }
    tail = email.split('@')[1]
    return maps[tail] if tail in maps else None


def get_pop3_host(email):
    """获取邮箱对应的服务商的 POP3 服务器地址"""
    maps = {
        'qq.com': 'pop.qq.com',
        'gmail.com': 'pop.gmail.com',
        '126.com': 'pop.126.com',
        '163.com': 'pop.163.com',
        'sohu.com': 'pop3.sohu.com',
        'sina.com': 'pop3.sina.com',
        '139.com': 'pop.139.com',
        'foxmail.com': 'pop.foxmail.com'
    }
    tail = email.split('@')[1]
    return maps[tail] if tail in maps else None


def get_now_time():
    """获取当前时间并转换成2018_7_5_12_14这种格式"""
    return time.strftime('%Y_%m_%d_%H_%M', time.localtime(time.time()))


def create_dir(abs_path):
    """创建附件文件夹"""
    if not os.path.exists(abs_path):
        os.makedirs(abs_path)
    return abs_path


def delete_file(abs_path):
    """删除文件"""
    os.remove(abs_path)


def split_file_name(filenames):
    """
    分割附件名，提取出学号/姓名/作业名
    :param filenames: 附件名列表
    :return: （学号,姓名,作业名,）元组
    """
    filename_info = []
    for name in filenames:
        filename_info.append(name.split('-'))
    return filename_info


def get_file_name_list(sender_info):
    """
    从senfer_info中提取出所有附件名并保存为一个集合
    :param sender_info: 发件人列表
    :return: （学号,姓名,作业名,）元组
    """
    name_list = []
    for sender in sender_info:
        name_list.extend(sender.attachments)
    return split_file_name(name_list)


class Saver(object):
    """用户账户信息/下载偏好"""

    def __init__(self, account, password,
                 start=None, end=None, report_name=None):
        self.account = account  # 账号
        self.password = password  # 密码/授权码
        self.start_date = start  # 接受报告开始时间
        self.end_date = end  # 接收报告终止时间
        self.report_name = report_name  # 报告名称


class Sender:
    """发信人对象"""

    def __init__(self):
        self.nickname = None  # 昵称
        self.address = None  # 邮箱
        self.timestamp = None  # 时间戳
        self.attachments = None  # 附件名称列表
        self.report_name = None #报告名


# TODO(bearcarl@qq.com) 未考虑附件重名的情况
class EmailSpider:

    save_path = 'Attachments'

    def __init__(self, saver):
        self.saver = saver
        self.attachments = []  # 附件集合
        self.emails = []       # 发件学生邮箱集合
        self.email_attach = {} # 邮件和附件的对应字典
        self.server = poplib.POP3_SSL(get_pop3_host(self.saver.account))
        self.now = get_now_time()

    def _connect(self):
        try:
            self.server.user(self.saver.account)  # 身份信息
            self.server.pass_(self.saver.password)
        except Exception as e:
            # lg.warning('\t' + repr(e))
            print('connect error: ', e.args)

    def _disconnect(self):
        try:
            self.server.quit()
        except Exception as e:
            # lg.warning('\t' + repr(e))
            print('disconnect error: ', e.args)

    def _get_email_num(self):
        """获得邮件数量"""
        num, size = self.server.stat()
        return num

    @staticmethod
    def _decode_str(s):
        """转换编码"""
        try:
            value, charset = decode_header(s)[0]
            if charset:
                value = value.decode(charset)
            return value
        except Exception as e:
            # lg.warning('\t' + repr(e))
            print('decode string error:', e.args)

    def _get_time_stamp(self, index):
        """获取邮件的UNIX时间戳
        :param index: 邮件在邮件列表中的编号
        """
        print('邮件编号：{}'.format(index))
        messages = self.server.retr(index)[1]
        mail = email.message_from_bytes('\n'.encode('utf-8').join(messages))
        date = email.header.decode_header(mail.get('Date'))[0][0]  # 获取邮件发送时间
        print('时间：{}'.format(date))
        try:
            beijing_time = datetime.strptime(date[5:31].rstrip(), '%d %b %Y %H:%M:%S %z')
            localtime = beijing_time + timedelta(hours=+8)
            localtimestamp = localtime.timestamp()
        except:
            beijing_time = datetime.strptime(date[5:31], '%d %b %Y %H:%M:%S %z')
            localtimestamp = beijing_time.timestamp()
        return localtimestamp

    @classmethod
    def _get_from(cls, msg):
        """获取发送人昵称/邮箱
        :param msg: Message对象
        :return: (昵称,邮箱)
        """
        value = msg.get('From', '')
        if value:
            name, addr = parseaddr(value)
            name = cls._decode_str(name)
            from_info = (name, addr)
            return from_info

    @classmethod
    def _get_subject(cls, msg):
        subject = cls._decode_str(msg.get("Subject"))
        return subject

    def _parse_email(self, index):
        """根据邮件在邮件列表中的编号，解析邮件
        :param index: 邮件在邮件列表中的编号
        :return: None
        """
        time_stamp = self._get_time_stamp(index)
        tmp_sender = Sender()
        tmp_sender.timestamp = time_stamp

        byte_lines = self.server.retr(index)[1]
        msg_content = ''
        try:
            #如果邮件内容包含图片和非法字符，直接跳过，不解析
            for x in byte_lines:  # 转码
                msg_content += (x.decode() + '\n')

            # 把邮件内容解析成Message对象
            msg = Parser().parsestr(msg_content)
            # 获取发信人昵称/邮箱/主题名并保存
            sender_info = self._get_from(msg)
            subject = self._get_subject(msg)

            tmp_sender.nickname = sender_info[0]
            tmp_sender.address = sender_info[1]
            tmp_sender.subject = subject

            if tmp_sender.subject.startswith(self.saver.report_name):
                attachments = self._download_attachment(msg, tmp_sender.address)
                tmp_sender.attachments = attachments
                self.email_attach[tmp_sender.address] = attachments  # 将邮箱和attachments关联
                self.attachments.extend(attachments)
        except:
            pass


    def find_emails(self):
        """二分法查找时间间隔内的邮件
        开始时的左右边界分别是邮件列表中的第一封邮件和最后一封邮件
        :return: None
        """
        # todo QQ 邮箱对于时间过久的邮件好像不会出现在邮件列表中，做个提示
        email_count = self._get_email_num()
        left = 1
        right = email_count

        target = self._traveler(left, right)
        redis_conn.set(self.saver.account+'download_progress', '{:.2%}'.format(0.1))

        l = target
        r = target

        while self._get_time_stamp(l) > self.saver.start_date:
            print('起始时间' , self.saver.start_date)
            print("当前文件时间" , self._get_time_stamp(l))
            self._parse_email(l)
            if l > 1:l -= 1
            else:break
        redis_conn.set(self.saver.account + 'download_progress', '{:.2%}'.format(0.6))

        while self._get_time_stamp(r) < self.saver.end_date:
            print('结束时间' , self.saver.end_date)
            print("结束时间" , self._get_time_stamp(r))
            self._parse_email(r)
            if r < email_count:r += 1
            else:break
        redis_conn.set(self.saver.account + 'download_progress', '{:.2%}'.format(1.0))

    def _traveler(self, left, right):
        """从left向右遍历， 直到right
        :param left: 遍历范围内最左侧（时间最早）的邮件编号
        :param right: 遍历范围内最右侧（时间最晚）的邮件编号
        :return: None
        """
        mid_date = (self.saver.start_date + self.saver.end_date) // 2

        mid = 0
        while left < right:
            lts = self._get_time_stamp(left)
            rts = self._get_time_stamp(right)
            mid = (left + right) // 2
            mid_ts = (lts + rts) // 2
            if mid_ts >= mid_date:
                right = mid - 1
            elif mid_ts < mid_date:
                left = mid + 1
        return mid


    def _download(self, part, filename):
        data = part.get_payload(decode=True)
        save_dir = '{0}/{1}/{2}'.format(self.save_path, self.saver.account, self.saver.report_name)
        save_path = '{0}/{1}/{2}/{3}'.format(self.save_path, self.saver.account, self.saver.report_name, filename)
        create_dir(save_dir)
        with open(save_path, 'wb') as f:
            f.write(data)

    def _download_attachment(self, message, email):
        attachments = []
        for part in message.walk():
            filename = part.get_filename()
            if filename:
                filename = self._decode_str(filename)
                if allowed_file(filename):  # 检查文件名是否符合规则
                    print("现在进入下载！")
                    self._download(part=part, filename=filename)
                    attachments.append(filename)
                    self.emails.append(email)
        return attachments

    def run(self):
        """主控方法，控制服务器的连接/断开/邮件遍历等
        :return: 发送人邮件列表/附件名列表
        """
        self._connect()
        self.find_emails()
        self._disconnect()
        print('self.attach', self.attachments)
        save_dir = '{0}/{1}/{2}'.format(self.save_path, self.saver.account, self.saver.report_name)
        return self.attachments, self.emails, save_dir


class EmailSender(object):
    def __init__(self):
        self.server = None

    def conn_server(self, account, password, host):
        # try:
        self.server = yagmail.SMTP(user=account,
                                       password=password,
                                       host=host,
                                       smtp_ssl=True)
        return True
        # except Exception as e:
        #     return False

    def send_email(self, receiver_list, subject, contents):
        if len(receiver_list) <= 0:
            print('few shoot')
        # try:
        self.server.send(to=receiver_list,
                             subject=subject,
                             contents=contents)
        # except Exception:
        #     print('发送失败')

def docx2pdf(filepath, dirpath, filename):
    #结果是html，xswl
    # wdFormatPDF = 17
    in_file = filepath
    out_path = dirpath + '/Webpages'
    create_dir(out_path)
    html = PyDocX.to_html(in_file)
    f = open(filename, 'w', encoding="utf-8")
    f.write(html)
    f.close()

def unzip(filepath, targetdir):
    """unzip zip file"""
    zip_file = zipfile.ZipFile(filepath)
    for names in zip_file.namelist():       #如果解压错误，并且加上过滤
        if names.endswith('.docx'):
            zip_file.extract(names, targetdir)
    zip_file.close()
    print(targetdir)
    decode_filename(targetdir)

def decode_filename(parse_dir):
    for temp_name in os.listdir(parse_dir):
        try:
            new_name = temp_name.encode('cp437')
            new_name = new_name.decode("gbk")
            os.rename('{0}/{1}'.format(parse_dir, temp_name), '{0}/{1}'.format(parse_dir, new_name))
        except:
            pass
