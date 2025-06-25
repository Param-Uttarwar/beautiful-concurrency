"""
Orchestrator

The Orchestrator class manages the execution of Task objects, handling their dependencies and execution order.
It supports multiple execution modes: sequential, threading, multiprocessing, and asyncio.
"""


from beautiful_concurrency.base.task import Task
import concurrent.futures
import asyncio
import functools

class Orchestrator:
    """
    The orchestrator is responsible for managing the execution of tasks.
    It can be used to run tasks in parallel or sequentially, depending on the use case.
    """

    def __init__(self):
        pass


    def run(self, tasks: list[Task], mode: str = "sequential"):
        """
        Run a list of tasks using the specified mode.
        :param tasks: List of tasks to run.
        :param mode: Execution mode: 'sequential', 'threading', 'multiprocessing', or 'asyncio'.
        """
        stages = self._build_task_graph(tasks)

        if mode == "sequential":
            self._run_sequential(stages)
        elif mode == "threading":
            self._run_with_threading(stages)
        elif mode == "multiprocessing":
            self._run_with_multiprocessing(stages)
        elif mode == "asyncio":
            asyncio.run(self._run_with_asyncio(stages))
        else:
            raise ValueError(f"Unknown execution mode: {mode}")


    def _build_task_graph(self, tasks: list[Task]) -> tuple:
        """
        Build a directed acyclic graph (DAG) of tasks based on their dependencies.
        This is an internal method that organizes tasks into a structure that can be executed.
        """
        in_degree = {task.id: len(task._parents) for task in tasks}
        task_map = {task.id: task for task in tasks}
        
        stages = []
        current_stage_tasks = [task_map[task_id] for task_id, degree in in_degree.items() if degree == 0]

        while current_stage_tasks:
            stages.append(tuple(current_stage_tasks))
            next_stage_tasks = []
            for task in current_stage_tasks:
                for child_task in task._children:
                    in_degree[child_task.id] -= 1
                    if in_degree[child_task.id] == 0:
                        next_stage_tasks.append(child_task)
            current_stage_tasks = next_stage_tasks
        
        if any(degree > 0 for degree in in_degree.values()):
            raise ValueError("Circular dependency detected in task graph.")

        return tuple(stages)


    def _run_sequential(self, stages: tuple[tuple[Task, ...], ...]):
        """
        Executes tasks sequentially, stage by stage.
        """
        for stage in stages:
            for task in stage:
                task()

    def _run_with_threading(self, stages: tuple[tuple[Task, ...], ...]):
        """
        Executes tasks using a ThreadPoolExecutor, stage by stage.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for stage in stages:
                futures = [executor.submit(task) for task in stage]
                for future in concurrent.futures.as_completed(futures):
                    future.result() # To propagate exceptions

    def _run_with_multiprocessing(self, stages: tuple[tuple[Task, ...], ...]):
        """
        Executes tasks using a ProcessPoolExecutor, stage by stage.
        """
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for stage in stages:
                futures = [executor.submit(task) for task in stage]
                for future in concurrent.futures.as_completed(futures):
                    future.result() # To propagate exceptions

    async def _run_with_asyncio(self, stages: tuple[tuple[Task, ...], ...]):
        """
        Executes tasks using asyncio, stage by stage.
        """
        for stage in stages:
            await asyncio.gather(*[self._run_async_task(task) for task in stage])

    async def _run_async_task(self, task: Task):
        """
        Wrapper to run a Task asynchronously.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, functools.partial(task.__call__))


if __name__ == "__main__":
    # Example usage
    from beautiful_concurrency.base.task import Task

    def example_task(name, duration):
        import time
        time.sleep(duration)
        return f"{name} completed"

    t1 = Task("Task 1", example_task, ("Task 1", 2), {})
    t2 = Task("Task 2", example_task, ("Task 2", 3), {})
    t3 = Task("Task 3", example_task, ("Task 3", 1), {})

    orch = Orchestrator()
    orch.run([t1, t2, t3], mode="asyncio")  # Change to "sequential", "threading", or "multiprocessing" as needed)
    print(t1.result, t2.result, t3.result)

        