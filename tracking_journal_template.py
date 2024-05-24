import time

import my_logging as MyLog
import remind_wechat as wechat
import remind_mail as mail
import tracking_manuscript as tm

#first, activate the logger
journal = "**" #self defined
login_url = "https://mts-ncomms.nature.com/cgi-bin/main.plex" # taks NC as an example

#some debug
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
tm_my = tm.TrackingManuscript(username,password,logger,"plex") or "scholarOn"

method = "email" # or wechat

"""
Main code
"""
#activate the browser
driver = tm_my.activate_browser(headless=True)
# navigate to the website
driver = tm_my.login_and_navigate(driver,login_url)

previous_stage_info = "None"
while True:
    try:
        status_message, status_table, previous_stage_info = tm_my.monitor_status_changes(driver,"email",previous_stage_info)
        if method == "wechat":  
            wechat.sendMsg(openId,status_message)
        elif method == "email":
            mail_server = mail.connect_server(sender_email, smtp_password)
            mail_message = mail.prepare_email(sender_email, journal + " Manuscript Notifications",receiver_email,status_message,status_table)
            mail.send_email(mail_server,mail_message,sender_email,receiver_email)
        logger.info("Waiting for 30 minutes")
        time.sleep(1800)
    except Exception as e:
        logger.critical(f"An error occurred: {str(e)}")
        wechat.sendMsg(openId,"An error occurred, please check the log")
        logger.info("retrying")
        driver = tm_my.login_and_navigate(driver,login_url)
    except ValueError("unknown site type"):
        logger.critical("unknown site type")
        break

driver.quit()

