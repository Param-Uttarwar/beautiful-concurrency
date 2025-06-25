import enum


NOT_COMPUTED = object()

class Status(enum.Enum):
    """
    Enum representing the status of a task.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    def __str__(self):
        return self.value