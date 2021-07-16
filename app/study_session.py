from __future__ import annotations

from argparse import Namespace as Args
from dataclasses import dataclass

from app.cli import CLI
from app.flashcard import Collection, Database, Flashcard


@dataclass
class StudyInstance:
    flashcard: Flashcard
    cli: CLI
    record_results: bool

    def do(self) -> None:
        attempted_answer = self.cli.prompt(str(self.flashcard.question))
        if self.flashcard.answer.matches(attempted_answer):
            self._handle_success()
        else:
            self._handle_failure()

    def _handle_success(self) -> None:
        self.cli.print("Correct!")
        if self.record_results:
            self.flashcard.history.record_success()

    def _handle_failure(self) -> None:
        message = "Incorrect. Would you like to see the answer?"
        if self.record_results:
            self.flashcard.history.record_failure()
        try:
            wants_to_see_answer = self.cli.prompt_with_yes_no_question(message)
            if wants_to_see_answer:
                self.cli.print(f"The correct answer is '{self.flashcard.answer}'.")
        except CLI.NoAnswerProvidedError:
            pass


@dataclass
class StudySession:
    COMMAND = "study"

    collection: Collection
    cli: CLI
    record_results: bool

    @classmethod
    def make(
        cls, args: Args, db_filepath: str, db_schema_filepath: str, cli: CLI
    ) -> StudySession:
        db = Database.from_filepaths(db_filepath, db_schema_filepath)
        return cls(db.get_collection(args.collection), cli, not args.do_not_remember)

    def do(self) -> None:
        self.cli.print(
            f"The collection '{self.collection}' has {len(self.collection)} flashcards."
        )

        for flashcard in self.collection:
            study_instance = StudyInstance(flashcard, self.cli, self.record_results)
            study_instance.do()
            self.cli.empty_line()
