from typing import List, Optional


class CLI:
    EXIT_WORD = "exit"

    class NoAnswerProvidedError(Exception):
        pass

    def print(self, message: str) -> None:
        print(message)

    def prompt(self, message: str, valid_answers: Optional[List[str]] = None) -> str:
        if valid_answers is None:
            valid_answers = []

        answer = self._prompt(message)
        return self._process_answer(answer, valid_answers)

    def _process_answer(self, answer: str, valid_answers: List[str]) -> str:
        if valid_answers and answer not in valid_answers:
            new_answer = self._prompt(
                f"'{answer}' is not a valid answer."
                f" Try again or type '{self.EXIT_WORD}'."
            )
            if new_answer == self.EXIT_WORD:
                raise self.NoAnswerProvidedError
            return self._process_answer(new_answer, valid_answers)
        return answer

    def _prompt(self, message: str) -> str:
        return input(f"{message} ")

    def empty_line(self) -> None:
        self.print("")

    def prompt_with_yes_no_question(self, yes_no_question: str) -> bool:
        answer = self._prompt(yes_no_question)
        return self._process_yes_no_answer(answer)

    def _process_yes_no_answer(self, answer: str) -> bool:
        if answer.lower() in ("y", "yes"):
            return True
        if answer.lower() in ("n", "no"):
            return False
        new_answer = self._prompt(
            f"'{answer}' is not a yes-no answer. Try again or type '{self.EXIT_WORD}'."
        )
        if new_answer == self.EXIT_WORD:
            raise self.NoAnswerProvidedError
        return self._process_yes_no_answer(new_answer)
