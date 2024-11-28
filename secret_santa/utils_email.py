import logging
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64


class ChristmasMessageTemplate:
    def __init__(self, santa_mail) -> None:
        self.santa_mail = santa_mail

    def _craft_message_html_part(self, sender_name, target_name):
        if self.mail_template:
            return self.template.render(
                sender_name=sender_name, target_name=target_name
            )
        else:
            return self._basic_message_html_part(sender_name, target_name)

    def _basic_message_html_part(self, sender_name, target_name):
        return f"""<html>
        <head>
            <h1>Ho ho ho!</h1>
            <style>
                h1 {{
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div><strong>{sender_name}, cette année tu offres un cadeau à {target_name} ! \U0001F381 </strong></div>
            <br>
            <footer>~ Le Père Noël \U0001F385 </footer>

            <style>
                footer {{
                    text-align: right;
                }}
            </style>
        </body>
        </html>"""

    def get_email(self, sender_name, sender_mail, target_name):
        # Create multipart MIME email
        email_message = MIMEMultipart()
        email_message.add_header("To", sender_mail)
        email_message.add_header("From", f"Papa Noel <{self.santa_mail}>")
        email_message.add_header("Subject", "Une petite mission pour ce Noël ...")
        email_message.add_header("X-Priority", "1")  # Urgent/High priority

        # Create text and HTML bodies for email
        # text_part = MIMEText('Hello world plain text!', 'plain')
        html_part = MIMEText(
            self._craft_message_html_part(sender_name, target_name), "html"
        )

        # Create file attachment
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(b"\xDE\xAD\xBE\xEF")  # Raw attachment data
        attachment.add_header("Content-Disposition", "attachment; filename=myfile.dat")

        # Attach all the parts to the Multipart MIME email
        # email_message.attach(text_part)
        email_message.attach(html_part)
        email_message.attach(attachment)
        return email_message


class EMail:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.server = self.get_server(host, port)
        self.email = f"Papa Noel <{user}>"

    def get_server(self, host, port):
        smtp_server = SMTP(host=host, port=port)
        smtp_server.starttls()
        return smtp_server

    def send(self, sender_email, message: MIMEMultipart):
        self.server.sendmail(self.email, sender_email, message.as_bytes())

    def login(self):
        self.server.login(self.user, self.password)

    def logout(self):
        self.server.quit()

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, *arg, **kwargs):
        self.logout()
