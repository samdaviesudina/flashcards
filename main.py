from argparse import ArgumentParser
from argparse import Namespace as Args

from app.cli import CLI
from app.flashcard import Collection
from app.sessions import (
    CreatingSession,
    DeletingSession,
    EditingSession,
    StudyingSession,
)

DB_FILEPATH = "db/data.db"
DB_SCHEMA_FILEPATH = "db/schema.sql"


def prepare_arg_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "command",
        type=str,
        help="The command: 'study', 'create' or 'edit'.",
    )
    parser.add_argument(
        "collection",
        type=str,
        help="The name of the collection.",
    )
    parser.add_argument(
        "--do-not-remember",
        action="store_true",
        help="Makes it a study session where your scores will not be recorded."
        " False by default.",
    )
    return parser


def main(args: Args) -> None:
    cli = CLI()
    commands = [
        StudyingSession.COMMAND,
        CreatingSession.COMMAND,
        EditingSession.COMMAND,
        DeletingSession.COMMAND,
    ]
    if args.command not in commands:
        cli.print(
            f"Unrecognised command '{args.command}'. Run flashcards --help for usage."
        )
        return

    if args.command == StudyingSession.COMMAND:
        try:
            studying_session = StudyingSession.make(
                args, DB_FILEPATH, DB_SCHEMA_FILEPATH, cli
            )
            studying_session.do()
            return
        except Collection.DoesNotExist:
            cli.print(f"Collection '{args.collection}' does not yet exist.")
            return
    if args.command == CreatingSession.COMMAND:
        creating_session = CreatingSession.make(
            args, DB_FILEPATH, DB_SCHEMA_FILEPATH, cli
        )
        creating_session.do()
        return
    if args.command == EditingSession.COMMAND:
        try:
            editing_session = EditingSession.make(
                args, DB_FILEPATH, DB_SCHEMA_FILEPATH, cli
            )
            editing_session.do()
            return
        except Collection.DoesNotExist:
            cli.print(f"Collection '{args.collection}' does not yet exist.")
            return
    if args.command == DeletingSession.COMMAND:
        deleting_session = DeletingSession.make(
            args, DB_FILEPATH, DB_SCHEMA_FILEPATH, cli
        )
        deleting_session.do()


if __name__ == "__main__":
    argument_parser = prepare_arg_parser()
    args = argument_parser.parse_args()
    main(args)
