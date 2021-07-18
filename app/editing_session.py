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
        if self.just_created:
            action = "add"
            self.cli.print("Now let's add some flashcards!")
        else:
            action = self.cli.prompt(
                "What do you want to do: add a flashcard, edit an existing one"
                " or delete a flashcard?",
                ["add", "edit", "delete"],
            )
        if action == "edit":
            raise NotImplementedError
        if action == "add":
            self._do_adding()
        if action == "delete":
            self._do_deleting()

    def _display_all_flashcards_in_collection(self) -> None:
        for flashcard in self.collection:
            self.cli.print(f"  {flashcard}")

    def _do_adding(self) -> None:
        while True:
            self._add_flashcard()
            try:
                wants_to_add_another_one = self.cli.prompt_with_yes_no_question(
                    "Added a new flashcard. Want to add another one?"
                )
                if not wants_to_add_another_one:
                    break
            except self.cli.NoAnswerProvidedError:
                break

    def _do_deleting(self) -> None:
        self.cli.print("These are the flashcards in your collection:")
        self._display_all_flashcards_in_collection()
        while True:
            flashcard_id = int(
                self.cli.prompt("Type in the ID of the flashcard you'd like to delete:")
            )
            if flashcard_id not in [flashcard.id for flashcard in self.collection]:
                self.cli.print(
                    f"The ID '{flashcard_id}' does not match any existing flashcards."
                )
            self.collection.delete_flashcard(flashcard_id)
            try:
                wants_to_delete_another_one = self.cli.prompt_with_yes_no_question(
                    f"Flashcard with ID '{flashcard_id}' successfully deleted."
                    " Want to delete another one?"
                )
                if not wants_to_delete_another_one:
                    break
            except self.cli.NoAnswerProvidedError:
                break

    def _add_flashcard(self) -> None:
        question = self.cli.prompt("What's the question?")
        answer = self.cli.prompt("And what's the answer?")
        self.collection.add_flashcard(Question(question), Answer(answer))
