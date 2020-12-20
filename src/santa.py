import click
from santa import humans
from santa import secret


@click.command(name="Secret santa", no_args_is_help=True)
@click.option(
    "-i",
    "--people-path",
    required=True,
    type=click.Path(exists=True, resolve_path=True, dir_okay=False),
    help="Path to your people's list with couples",
)
@click.option(
    "--with-mail",
    is_flag=True,
    default=False,
    help="Wether you want to send emails or not",
)
@click.option(
    "--vcard-path",
    default=None,
    required=False,
    type=click.Path(exists=True, resolve_path=True, dir_okay=False),
    help="If you have a VCARD file to ease email sending, provide it here",
)
@click.option(
    "--with-stdout",
    is_flag=True,
    default=False,
    help="Wether you want to display results in terminal",
)
@click.option(
    "--no-dump",
    is_flag=True,
    default=False,
    help="Wether you want to dump results inside files",
)
@click.option("--debug", is_flag=True, default=False, help="debug mode")
def run(people_path, with_stdout, with_mail, vcard_path, no_dump, debug):
    people, couple = humans.load_people(people_path)
    vcards = None if vcard_path is None else humans.load_vcards(vcard_path)
    gift_matrix = secret.santa_roll_dices(people, couple)
    senders = humans.SendersList(people, gift_matrix, vcards)
    if with_stdout:
        senders.stdout()
    if with_mail:
        senders.fire_email()
    if not no_dump:
        senders.dump()


if __name__ == "__main__":
    run()