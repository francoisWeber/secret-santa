import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tqdm import tqdm

def get_mail_config():
    with open('./mail_config.json') as f:
        return json.load(f)


def get_connection(host, port, santas_address, santas_password):
    server = smtplib.SMTP(host, port)
    server.starttls()
    server.login(santas_address, santas_password)
    return server


def fire_emails(server, mails_and_messages):
    for mail_message in tqdm.tqdm(mails_and_messages):
        msg = MIMEMultipart()
        msg['From'] = server.user
        msg['To'] = mail_message['mail']
        msg['Subject'] = "Secret Santa <3"
        msg.attach(MIMEText(mail_message['message'], 'plain'))
        server.send_message(msg)
        time.sleep(1)