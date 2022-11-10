import logging
import click
from secret_santa.people import Group
from secret_santa.chain_saver import ChainSaver
from secret_santa.utils import check_and_extract_email_stuff
import random
import os

logging.basicConfig(level=logging.DEBUG)


@click.command()
@click.option(
    "--people-file",
    "-i",
    default="/Users/f.weber/Code/secret-santa/lesGens.txt",
    help="File to the people",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "--peoples-email-config-path",
    "--peoples-email",
    "-m",
    default=None,
    help="File to an people > email JSON",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "--mail-server-config-path",
    "--mail-config",
    "-c",
    default=None,
    help="JSON of email config",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "--output-dir",
    "-o",
    default=".",
    help="output file",
    type=click.Path(exists=False, dir_okay=True),
)
@click.option(
    "--mail-template",
    "-t",
    default=None,
    help="Jinja mail template",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
@click.option(
    "--secret",
    "-s",
    default=False,
    help="If set, then no trace about the people's chain is left !",
    is_flag=True,
)
@click.option(
    "--debug",
    default=False,
    is_flag=True,
)
def run(
    people_file,
    peoples_email_config_path,
    mail_server_config_path,
    output_dir,
    mail_template,
    secret,
    debug,
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    # load group info
    logging.info("Getting people data")
    group = Group.load(people_file)

    # find a valid chain
    logging.info("Crafting a valid people chain")
    people_chain = None
    while not group.is_chain_valid(people_chain):
        people_chain = group.people.copy()
        random.shuffle(people_chain)

    # save chain
    if not secret:
        logging.info("Now savig the people chain")
        if output_dir == ".":
            output_dir = os.path.join(os.path.abspath(output_dir), group.name())
        logging.info(f"Saving dir is: {output_dir}")
        ChainSaver.into_simple_listfile(people_chain, output_dir)
        ChainSaver.into_several_files(people_chain, output_dir)
    if peoples_email_config_path and mail_server_config_path:
        logging.info("Secret run : no trace will be left !")
        ChainSaver.into_emails(
            **check_and_extract_email_stuff(
                people_chain,
                peoples_email_config_path,
                mail_server_config_path,
                mail_template,
            )
        )
    elif (
        peoples_email_config_path
        and mail_server_config_path is None
        or peoples_email_config_path is None
        and mail_server_config_path
    ):
        print("peoples_email and mail_config must both be non-None")

    print("Ho ho hooo !")


if __name__ == "__main__":
    run()
