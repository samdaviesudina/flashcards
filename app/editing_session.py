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
                "Do you want to add a flashcard, edit an existing one,"
                " or delete an existing one?",
                ["add", "edit", "delete"],
            )
        if action == "edit":
            self._do_editing()
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
        if len(self.collection) == 0:
            self.cli.print("There are no flashcards to delete.")
            return
        self.cli.print("These are the flashcards in your collection:")
        self._display_all_flashcards_in_collection()
        while True:
            if len(self.collection) == 0:
                self.cli.print("There are no flashcards to delete.")
                break
            possible_flashcard_id = self.cli.prompt(
                "Type in the ID of the flashcard you'd like to delete:"
            )
            try:
                flashcard_id = self._validate_flashcard_id(possible_flashcard_id)
            except ValueError:
                self.cli.print(
                    f"The ID '{possible_flashcard_id}' does not match"
                    " any existing flashcards. Try again!"
                )
                continue
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

    def _do_editing(self) -> None:
        if len(self.collection) == 0:
            self.cli.print("There are no flashcards to edit.")
            return
        self.cli.print("These are the flashcards in your collection:")
        self._display_all_flashcards_in_collection()
        while True:
            possible_flashcard_id = self.cli.prompt(
                "Type in the ID of the flashcard you'd like to edit:"
            )
            try:
                flashcard_id = self._validate_flashcard_id(possible_flashcard_id)
            except ValueError:
                self.cli.print(
                    f"The ID '{possible_flashcard_id}' does not match"
                    " any existing flashcards. Try again!"
                )
                continue

            bit_to_edit = self.cli.prompt(
                "Would you like to edit the question, the answer, or both?",
                ["question", "answer", "both"],
            )

            if bit_to_edit == "question":
                new_question = self.cli.prompt("Please enter the new question:")
                self.collection.edit_flashcard(flashcard_id, new_question=new_question)
            if bit_to_edit == "answer":
                new_answer = self.cli.prompt("Please enter the new answer:")
                self.collection.edit_flashcard(flashcard_id, new_answer=new_answer)
            if bit_to_edit == "both":
                new_question = self.cli.prompt("Please enter the new question:")
                new_answer = self.cli.prompt("Please enter the new answer:")
                self.collection.edit_flashcard(
                    flashcard_id, new_question=new_question, new_answer=new_answer
                )

            try:
                wants_to_edit_another_one = self.cli.prompt_with_yes_no_question(
                    f"Flashcard with ID '{flashcard_id}' successfully edited."
                    " Want to edit another one?"
                )
                if not wants_to_edit_another_one:
                    break
            except self.cli.NoAnswerProvidedError:
                break

    def _validate_flashcard_id(self, possible_flashcard_id: str) -> int:
        flashcard_id = int(possible_flashcard_id)
        existing_flashcard_ids = [flashcard.id for flashcard in self.collection]
        if flashcard_id not in existing_flashcard_ids:
            raise ValueError
        return flashcard_id

    def _add_flashcard(self) -> None:
        question = self.cli.prompt("What's the question?")
        answer = self.cli.prompt("And what's the answer?")
        self.collection.add_flashcard(Question(question), Answer(answer))
