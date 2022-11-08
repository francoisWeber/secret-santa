from os import path as osp
from secret_santa.utils_email import ChristmasMessageTemplate, ChristmassMessage, EMail
from time import sleep
from tqdm import tqdm
from time import sleep
import logging
import random
import smtplib
import os


def get_notice(sender, receiver):
    return f"{sender}, tu offres ton cadeau à {receiver} :)\n\n Ho ho hooo!"


class ChainSaver:
    @staticmethod
    def into_simple_listfile(people_chain: list, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        output_path = osp.join(output_dir, "santa.txt")
        logging.info(f"Saving chain as one single flatfile: {output_path}")
        with open(output_path, "w") as f:
            f.writelines([p + "\n" for p in people_chain])

    @staticmethod
    def into_several_files(people_chain: list, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Saving chain as multiple one-person files: {output_dir}")
        n_people = len(people_chain)
        for i in range(n_people):
            sender = people_chain[i]
            receiver = people_chain[(i + 1) % n_people]
            msg = get_notice(sender, receiver)
            with open(osp.join(output_dir, f"{sender}.txt"), "w") as f:
                f.write(msg)

    @staticmethod
    def into_emails(
        people_chain: list, people_emails: dict, email_config: dict, mail_template=None
    ):
        logging.info("Sending emails to everyone")
        n_people = len(people_chain)
        problem = 0
        logging.debug("Checking everyone has an email address")
        for people in people_chain:
            if people not in people_emails:
                print(f"No email for {people} !")
                problem += 1
        assert problem == 0, "Problèmes d'email"
        logging.info("Connecting to santa's email ...")
        with EMail(**email_config) as server:
            logging.info("Connected !")
            logging.info("Sending mails ...")
            template = ChristmasMessageTemplate(email_config["user"], mail_template)
            n_mail_sent = 0
            for i in tqdm(range(n_people)):
                sender = people_chain[i]
                sender_email = people_emails[sender]
                receiver = people_chain[(i + 1) % n_people]
                message = template.get_email(sender, sender_email, receiver)
                try:
                    server.send(sender_email, message)
                    n_mail_sent += 1
                except smtplib.SMTPRecipientsRefused:
                    break
        logging.info(f"{n_mail_sent} mails sent")
