from __future__ import annotations
import time
from ..common import Status, NOT_COMPUTED

class Task:
    """
        Represents a unit of work to be executed, encapsulating a function, its arguments,
        execution state, timing, and dependencies. Tasks can depend on the results of other tasks.
    """
    _id_counter = 0

    def __init__(self, name: str, func: callable, args, kwargs):
        """
        Initializes a Task instance.

        :param name: Unique identifier for the task.
        :param func: The function to be executed when the task is called.
        :param args: Positional arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.

        """
        self.name = name
        self.id = Task._id_counter
        Task._id_counter += 1
        self.func = func
        self.args = args  # This list can contain raw values OR other Task objects
        self.kwargs = kwargs

        self.state: Status = Status.PENDING
        self.time_started = None
        self.time_completed = None
        self._result = NOT_COMPUTED  # This is where the output will be stored
        self._parents = set()  # Tasks that this task depends on
        self._children = set() # Tasks that depend on this task
        self._set_dependencies()

    def _set_dependencies(self) -> None:
        """
        Identifies and sets explicit task dependencies from args and kwargs.
        """
        for arg in self.args:
            if isinstance(arg, Task):
                arg._children.add(self)
                self._parents.add(arg)

        for value in self.kwargs.values():
            if isinstance(value, Task):
                value._children.add(self)
                self._parents.add(value)

    def __call__(self) -> None:
        """
        Execute the task function with the provided arguments and store the result.
        Updates the task's state and timing information.
        Raises:
            Exception: Propagates any exception raised by the task function.
        """
        self.state = Status.RUNNING
        self.time_started = time.perf_counter()

        try:
            resolved_args = self._resolve_args(self.args)
            resolved_kwargs = self._resolve_kwargs(self.kwargs)
            self._result = self.func(*resolved_args, **resolved_kwargs)
            self.state = Status.COMPLETED
        except Exception as e:
            self.state = Status.FAILED
            raise e

        self.time_completed = time.perf_counter()

    @property
    def result(self):
        return self._result

    def _resolve_args(self, args):
        resolved = []
        for arg in args:
            if isinstance(arg, Task):
                resolved.append(arg.result)
            elif isinstance(arg, (list, tuple)):
                resolved.append(self._resolve_args(arg))
            elif isinstance(arg, dict):
                resolved.append(self._resolve_kwargs(arg))
            else:
                resolved.append(arg)
        return tuple(resolved) if isinstance(args, tuple) else resolved

    def _resolve_kwargs(self, kwargs):
        resolved = {}
        for key, value in kwargs.items():
            if isinstance(value, Task):
                resolved[key] = value.result
            elif isinstance(value, (list, tuple)):
                resolved[key] = self._resolve_args(value)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_kwargs(value)
            else:
                resolved[key] = value
        return resolved