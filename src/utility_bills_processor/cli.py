"""The CLI for this package."""

import logging
from pathlib import Path
from typing import Final, Type

import click
import colorlog
from colorlog import escape_codes

from . import __version__
from ._common.bill import Bill

_RESET_COLOR: Final[str] = escape_codes.escape_codes["reset"]


def _configure_logging(level: int = logging.INFO) -> None:
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


def _base_command(scope: str, bill_subtype: Type[Bill]) -> click.Command:
    """A factory function for defining bill processing commands.

    This function ensures consistent parameters and behavior of those parameters.

    Args:
        scope: the text name of the bill, e.g. gas
        bill_subtype: the concrete class that represents the bill, e.g. GasBill

    Returns:
        a function decorated by `@click.command` that will be invoked based on CLI parameters
    """

    @click.command(short_help=f"Process {scope} bills.")
    @click.option(
        "-c/-i",
        "--check/--ignore-checks",
        default=True,
        help="Control if extracted values per bill are checked against each other.",
    )
    @click.option(
        "-p",
        "--password",
        prompt=True,
        prompt_required=False,
        hide_input=True,
        help="Use if the file(s) are encrypted.",
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
    ) -> None:
        """Extract data from BILL_FILES.

        A BILL_FILE must be PDF and may be encrypted. Use --password to decrypt.
        """
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
        bills.sort(key=lambda b: b.date)
        click.echo("-" * 80)
        print(", ".join(map(str, bills[0].to_header())))
        for bill in bills:
            print(",".join(map(str, bill.to_row())))

    return command


CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Increase verbosity of output."
)
def process_utility_bill(verbose: bool) -> None:
    """A script to process home utility bills into a CSV format."""
    # This function configures global options and settings.
    _configure_logging(level=logging.DEBUG if verbose else logging.INFO)


def _generate_commands() -> None:
    # Defer importing bill classes as long as possible.
    from .national_grid_gas import GasBill
    from .water_and_sewer import WaterBill

    process_utility_bill.add_command(_base_command("gas", GasBill), "gas")
    process_utility_bill.add_command(_base_command("water", WaterBill), "water")


_generate_commands()
