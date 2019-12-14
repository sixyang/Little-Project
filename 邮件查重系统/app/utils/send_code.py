from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

def send_email(receiver, mail_content, mail_title):
    '''
    reciver：接收者邮箱
    mail_content：邮件正文，并且可以使用html格式
    mail_title：邮件标题
    '''
    #qq邮箱smtp服务器    此处应该修改！
    host_server = 'smtp.qq.com'
    #sender_qq为发件人的qq号码
    sender_qq = '1827382607'
    #pwd为qq邮箱的授权码
    pwd = 'ciwglzmqwcuucgad'
    #发件人的邮箱

    sender_qq_mail = '1827382607@qq.com'

    #ssl登录
    smtp = SMTP_SSL(host_server)
    # smtp.set_debuglevel(True)

    smtp.ehlo(host_server)
    smtp.login(sender_qq, pwd)

    msg = MIMEText(mail_content, "html", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq_mail
    msg["To"] = receiver
    try:
        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
    except Exception as e:
        #log记录一下！
        return 'no'
    finally:
        smtp.quit()

