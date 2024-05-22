import time

import my_logging as MyLog
import remind_wechat as wechat
import remind_mail as mail
import tracking_manuscript as tm

#first, activate the logger
journal = "**" #self defined
login_url = "https://mts-ncomms.nature.com/cgi-bin/main.plex" # taks NC as an example

#user information
username = "xxxxxxxx"
password = "xxxxxxxxxxxx"

#wechat
openId = "0000000000000000000000000000"
#mail
sender_email = "xxxxxxxxxxxxxxxxxxxxxx"
smtp_password = "xxxxxxxxxxxxxxxx"  # Authorization code
receiver_email = "xxxxxxxxxxxxxx"

logger = MyLog.MyLogger(name="log")
tm_nc = tm.TrackingManuscript(username,password,logger)

"""
Main code
"""
#activate the browser
driver = tm_nc.activate_browser()

# navigate to the website
driver = tm_nc.login_and_navigate(driver,login_url)

previous_stage_info = "None"
method = "email" # or wechat
while True:
    try:
        status_message, status_table = tm_nc.check_status(driver,"email")
        if method == "wechat":  
            wechat.sendMsg(openId,status_message)
        elif method == "email":
            mail_server = mail.connect_server(sender_email, smtp_password)
            mail_message = mail.prepare_email(sender_email, journal + " Manuscript Notifications",receiver_email,status_message,status_table)
            mail.send_email(mail_server,mail_message,sender_email,receiver_email)
        logger.info("Waiting for 30 minutes")
        time.sleep(1800)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.info("Waiting for 5 minutes before retrying")
        time.sleep(300)
