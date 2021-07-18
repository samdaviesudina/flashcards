from __future__ import annotations

from argparse import Namespace as Args
from dataclasses import dataclass

from app.cli import CLI
from app.flashcard import Answer, Collection, Database, Question


@dataclass
class EditingSession:
    COMMAND = "edit"

    collection: Collection
    cli: CLI
    just_created: bool = False

    @classmethod
    def make(
        cls, args: Args, db_filepath: str, db_schema_filepath: str, cli: CLI
    ) -> EditingSession:
        db = Database.from_filepaths(db_filepath, db_schema_filepath)
        return cls(db.get_collection(args.collection), cli)

    def do(self) -> None:
        action = self.cli.prompt(
            "What do you want to do, add a flashcard or edit an existing one?",
            ["add", "edit"],
        )
        if action == "edit":
            raise NotImplementedError
        if action == "add":
            while True:
                self.add_flashcard()
                wants_to_add_another_one = self.cli.prompt_with_yes_no_question(
                    "Added a new flashcard. Want to add another one?"
                )
                if not wants_to_add_another_one:
                    break

    def add_flashcard(self) -> None:
        question = self.cli.prompt("What's the question?")
        answer = self.cli.prompt("And what's the answer?")
        self.collection.add_flashcard(Question(question), Answer(answer))
