from __future__ import annotations

from argparse import Namespace as Args
from dataclasses import dataclass

from app.cli import CLI
from app.flashcard import Collection, Database


@dataclass
class DeletingSession:
    COMMAND = "delete"

    collection_name: str
    cli: CLI
    db: Database

    @classmethod
    def make(
        cls, args: Args, db_filepath: str, db_schema_filepath: str, cli: CLI
    ) -> DeletingSession:
        db = Database.from_filepaths(db_filepath, db_schema_filepath)
        return cls(args.collection, cli, db)

    def do(self) -> None:
        try:
            self.db.delete_collection(self.collection_name)
            self.cli.print(f"Successfully deleted collection '{self.collection_name}'.")
        except Collection.DoesNotExist:
            self.cli.print(f"The collection '{self.collection_name}' does not exist.")
