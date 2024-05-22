import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.header import Header
import markdown

import my_logging as MyLog

# Activate the logger
logger = MyLog.MyLogger(name="log")


def connect_server(sender_email, smtp_password):
    # Connect to the email server
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    try:
        server.login(sender_email, smtp_password)
        logger.info("Logged in to the email server.")
        return server
    except Exception as e:
        logger.error(f"Error logging in to the email server: {str(e)}")
        return None

def prepare_email(sender_email,sender_header,receiver_email,subject,extra_html=None):
    # Create a MIMEText object to hold the email content
    message = MIMEMultipart("alternative")
    #message = MIMEText("这是一封测试邮件。", "plain", "utf-8")
    message["From"] = formataddr([sender_header, sender_email])
    message["To"] = formataddr(["Notifications", receiver_email])
    message["Subject"] = Header(subject, "utf-8")

    # draw the html content
    html = """\
    <html>
      <body>
        <p>Hello, <br>
          This is a email sent from Ubuntu of Jun Gu for notification.
        </p>
      </body>
    </html>
    """
    part2 = MIMEText(html, "html")
    part3 = MIMEText(extra_html, "html")
    message.attach(part2)
    message.attach(part3)

    return message


def send_email(server,message,sender_email,receiver_email):
    try:
        server.sendmail(sender_email, receiver_email, message.as_string())
        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")

if __name__ == '__main__':
    # Set the sender's email and password
    sender_email = "xxxxxxxxxxxxxxxxxxxxx"
    smtp_password = "xxxxxxxxxxxxxxxx"  # 授权码
    server = connect_server(sender_email, smtp_password)
    # Set the receiver's email
    receiver_email = "xxxxxxxxxxxxxx"
    extra_html = """
      <table border="5">
              <tbody><tr>
                  <th>Stage</th>
                  <th>Start Date</th>
      </tr>
      <tr><td>Manuscript under consideration</td><td>14th May 24</td></tr>
      <tr><td>Editor Assigned</td><td>14th May 24</td></tr>
      <tr><td>Manuscript submitted</td><td>9th May 24</td></tr>
      <tr><td>Submission in process</td><td>9th May 24</td></tr>
      </tbody></table>
    """
    message = prepare_email(sender_email,"Jun Gu",receiver_email,"Test email",extra_html)
    send_email(server,message,sender_email,receiver_email)
    server.quit()
