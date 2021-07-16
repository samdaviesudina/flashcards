from __future__ import annotations

from argparse import Namespace as Args
from dataclasses import dataclass

from app.cli import CLI
from app.edit_session import EditSession
from app.flashcard import Collection, Database


@dataclass
class CreateSession:
    COMMAND = "create"

    collection_name: str
    cli: CLI
    db: Database

    @classmethod
    def make(
        cls, args: Args, db_filepath: str, db_schema_filepath: str, cli: CLI
    ) -> CreateSession:
        db = Database.from_filepaths(db_filepath, db_schema_filepath)
        return cls(args.collection, cli, db)

    def do(self) -> None:
        try:
            collection = self.db.create_collection(self.collection_name)
        except Collection.AlreadyExists:
            self.cli.print(f"The collection '{self.collection_name}' already exists.")
            return
        self.cli.print(f"New collection '{self.collection_name}' successfully created.")
        edit_session = EditSession(collection, self.cli, just_created=True)
        edit_session.do()
