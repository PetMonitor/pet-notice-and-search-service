from enum import Enum

class PostState(Enum):
    LOST = "LOST"
    FOUND = "FOUND"

    def __str__(self):
        return str(self.value)