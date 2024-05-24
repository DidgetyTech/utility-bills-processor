"""The CLI for this package."""
import logging
from pathlib import Path
from typing import Final, Required, Type

import click
import colorlog
from colorlog import escape_codes

from ._common.bill import Bill

_RESET_COLOR: Final[str] = escape_codes.escape_codes["reset"]


def _configure_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(asctime)s %(log_color)s[%(levelname)s] %(message)s",
            log_colors={
                "DEBUG": "light_black",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            force_color=True,
        )
    )

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


_configure_logging()


def _base_command(scope: str, bill_subtype: Type[Bill]) -> click.Command:
    @click.command(short_help=f"Process {scope} bills.")
    @click.option(
        "-c/-i",
        "--check/--ignore-checks",
        default=True,
        help="Control if extracted values are checked against each other.",
    )
    @click.option(
        "-p",
        "--password",
        prompt=True,
        prompt_required=False,
        hide_input=True,
        help="Use if the file is encrypted.",
    )
    @click.argument(
        "bill_files",
        type=click.Path(
            file_okay=True,
            readable=True,
            exists=True,
            resolve_path=True,
            path_type=Path,
        ),
        nargs=-1,
        required=True,
    )
    def command(
        bill_files: tuple[Path],
        password: str | None,
        check: bool,
    ):
        bills = []
        for bill_file in bill_files:
            try:
                bill = bill_subtype.extract_fields(bill_file, password)
                if check:
                    bill.validate()
                else:
                    click.secho("Skipping data checks", fg="yellow")
                bills.append(bill)

            except RuntimeError as error:
                message = f"Failed to process as a {scope} bill: {str(bill_file)}"
                logging.error(f"{message}{_RESET_COLOR} {str(error)}")
                raise click.ClickException(message) from error
        click.echo("-" * 80)
        print(", ".join(map(str, bills[0].to_header())))
        for bill in bills:
            print(",".join(map(str, bill.to_row())))

    return command


@click.group()
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Increase verbosity of output."
)
def cli(verbose: bool):
    """Configure global options."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


def _generate_commands():
    from .national_grid_gas import GasBill
    from .water_and_sewer import WaterBill

    cli.add_command(_base_command("gas", GasBill), "gas")
    cli.add_command(_base_command("water", WaterBill), "water")


_generate_commands()
