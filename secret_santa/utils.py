import hashlib
import vobject
import json
import logging
import os


def sha256(*args):
    sha1_creator = hashlib.sha256()
    for item in args:
        sha1_creator.update(str(item).encode())
    return sha1_creator.digest().hex()


def load_vcards(path):
    with open(path) as f:
        card_lines = f.readlines()
    vcards = []
    for line in card_lines:
        if line.startswith("BEGIN:VCARD"):
            one_vcard = line
        elif line.startswith("END:VCARD"):
            one_vcard += line
            vcards.append(vobject.readOne(one_vcard))
        else:
            one_vcard += line
    return vcards


def check_and_extract_email_stuff(
    people_chain, peoples_email, mail_config, mail_template
):
    with open(peoples_email) as f:
        _peoples_email = json.load(f)
        _peoples_email = {
            name.capitalize(): mail for name, mail in _peoples_email.items()
        }
    with open(mail_config) as f:
        _mail_config = json.load(f)
    if "password" not in _mail_config:
        logging.warning("password not in JSON, trying to get it from environment")
        password = os.environ.get("SANTA_PASSWORD")
        if password:
            _mail_config["password"] = password
            print(password)
            logging.info("Retrieved password from env")
        else:
            raise AttributeError("No password to connect to Santa's mail :(")
    logging.debug("Checking everyone has an email")
    mail_update = {
        people: input(f"Provide an email for {people} :)")
        for people in people_chain
        if people not in _peoples_email
    }
    if len(mail_update) > 0:
        _peoples_email.update(mail_update)
        with open(peoples_email, "w") as f:
            json.dump(_peoples_email, f, indent=2)
    return {
        "people_chain": people_chain,
        "people_emails": _peoples_email,
        "email_config": _mail_config,
        "mail_template": mail_template,
    }
