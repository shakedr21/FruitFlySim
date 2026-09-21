class Timer:
    TURNS_PER_SECOND = 60

    def __init__(self, frequency_in_turns, start_ready=False):
        self._frequency_in_turns = frequency_in_turns
        self._turns_remaining = 0 if start_ready else frequency_in_turns

    def reset(self):
        self._turns_remaining = self._frequency_in_turns

    def progress(self):
        if self._turns_remaining <= 0:
            raise Exception("Timer was expired!")

        self._turns_remaining = self._turns_remaining - 1

    def status(self):
        return self._turns_remaining <= 0
