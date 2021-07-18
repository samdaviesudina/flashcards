from __future__ import annotations

from dataclasses import dataclass
from sqlite3 import connect, Connection, Row
from typing import Generator, List


@dataclass
class Question:
    question: str

    def __repr__(self) -> str:
        return self.question


@dataclass
class Answer:
    answer: str

    def __repr__(self) -> str:
        return self.answer

    def matches(self, attempted_answer: str) -> bool:
        return attempted_answer == self.answer


@dataclass
class Database:
    filepath: str
    schema_filepath: str
    connection: Connection

    @classmethod
    def from_filepaths(cls, filepath: str, schema_filepath: str) -> Database:
        connection = connect(filepath)
        connection.row_factory = Row
        return cls(filepath, schema_filepath, connection)

    def __post_init__(self) -> None:
        with open(self.schema_filepath) as f:
            sql = f.read()
        with self.connection:
            self.connection.executescript(sql)

    def record_success(self, flashcard_id: int) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE Flashcard"
                " SET SuccessfulAttempts = SuccessfulAttempts + 1"
                " WHERE Id = :id",
                {"id": flashcard_id},
            )

    def record_failure(self, flashcard_id: int) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE Flashcard"
                " SET FailedAttempts = FailedAttempts + 1"
                " WHERE Id = :id",
                {"id": flashcard_id},
            )

    def get_collection(self, collection_name: str) -> Collection:
        collection_id = self._get_collection_id(collection_name)
        with self.connection:
            rows = self.connection.execute(
                "SELECT * FROM Flashcard" " WHERE CollectionId = :collection_id",
                {"collection_id": collection_id},
            )

            return Collection(
                CollectionData(
                    collection_id,
                    collection_name,
                ),
                [
                    Flashcard(
                        row["Id"],
                        CollectionData(collection_id, collection_name),
                        Question(row["Question"]),
                        Answer(row["Answer"]),
                        FlashcardHistory(
                            row["Id"],
                            row["SuccessfulAttempts"],
                            row["FailedAttempts"],
                            self,
                        ),
                    )
                    for row in rows
                ],
                self,
            )

    def _get_collection_id(self, collection_name: str) -> int:
        with self.connection:
            collection_rows = list(
                self.connection.execute(
                    "SELECT Id FROM Collection WHERE Name = :name",
                    {"name": collection_name},
                )
            )
        assert len(collection_rows) == 1
        return collection_rows[0]["Id"]

    def does_collection_exist(self, collection_name: str) -> bool:
        with self.connection:
            collection_rows = list(
                self.connection.execute("SELECT Name FROM Collection")
            )
        collection_names = [row["Name"] for row in collection_rows]
        return collection_name in collection_names

    def create_collection(self, collection_name: str) -> Collection:
        if self.does_collection_exist(collection_name):
            raise Collection.AlreadyExists

        with self.connection:
            self.connection.execute(
                "INSERT INTO Collection (Name) VALUES (:name)",
                {"name": collection_name},
            )

        collection_id = self._get_collection_id(collection_name)
        return Collection(CollectionData(collection_id, collection_name), [], self)

    def add_flashcard(
        self, collection_id: int, question: Question, answer: Answer
    ) -> Flashcard:
        # TODO: We might want to check that the question is unique.
        question_string = question.question
        with self.connection:
            self.connection.execute(
                "INSERT INTO Flashcard (CollectionId, Question, Answer)"
                " VALUES (:collection_id, :question, :answer)",
                {
                    "collection_id": collection_id,
                    "question": question_string,
                    "answer": answer.answer,
                },
            )

        with self.connection:
            flashcard_rows = list(
                self.connection.execute(
                    "SELECT Flashcard.Id, Collection.Name FROM Flashcard"
                    " INNER JOIN Collection ON Flashcard.CollectionId = Collection.Id"
                    " WHERE Question = :question",
                    {"question": question_string},
                )
            )
            assert len(flashcard_rows) == 1
            flashcard_id = flashcard_rows[0]["Id"]
            collection_name = flashcard_rows[0]["Name"]

        return Flashcard(
            flashcard_id,
            CollectionData(collection_id, collection_name),
            question,
            answer,
            FlashcardHistory(flashcard_id, 0, 0, self),
        )

    def delete_flashcard(self, flashcard_id: int) -> None:
        with self.connection:
            self.connection.execute(
                "DELETE FROM Flashcard WHERE Id = :flashcard_id",
                {"flashcard_id": flashcard_id},
            )


@dataclass
class FlashcardHistory:
    flashcard_id: int
    successful_attempts: int
    failed_attempts: int
    database: Database

    def record_success(self) -> None:
        self.successful_attempts += 1
        self.database.record_success(self.flashcard_id)

    def record_failure(self) -> None:
        self.failed_attempts += 1
        self.database.record_failure(self.flashcard_id)

    @property
    def total_attempts(self) -> int:
        return self.successful_attempts + self.failed_attempts


@dataclass
class CollectionData:
    id: int
    name: str


@dataclass
class Collection:
    class DoesNotExist(Exception):
        pass

    class AlreadyExists(Exception):
        pass

    collection_data: CollectionData
    flashcards: List[Flashcard]
    db: Database

    def __str__(self) -> str:
        return self.collection_data.name

    def __iter__(self) -> Generator[Flashcard, None, None]:
        yield from self.flashcards

    def __len__(self) -> int:
        return len(list(self.flashcards))

    def add_flashcard(self, question: Question, answer: Answer) -> None:
        flashcard = self.db.add_flashcard(self.collection_data.id, question, answer)
        self.flashcards.append(flashcard)

    def delete_flashcard(self, flashcard_id: int) -> None:
        self.db.delete_flashcard(flashcard_id)


@dataclass
class Flashcard:
    id: int
    collection_data: CollectionData
    question: Question
    answer: Answer
    history: FlashcardHistory

    def __repr__(self) -> str:
        return f"{self.id} | {self.question}"
