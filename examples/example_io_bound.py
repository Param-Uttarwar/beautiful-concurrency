import time
from beautiful_concurrency.base.task import Task
from beautiful_concurrency.base.orchestrator import Orchestrator
from beautiful_concurrency.task_scheduler_app import TaskSchedulerApp

def io_task_fetch_data(name: str, duration: float) -> str:
    """Simulates fetching data from a network or disk."""
    print(f"[{name}] Fetching data... (simulated {duration}s I/O)")
    time.sleep(duration)
    return f"Data from {name} fetched"

def io_task_process_data(name: str, data: str, duration: float) -> str:
    """Simulates processing fetched data."""
    print(f"[{name}] Processing {data}... (simulated {duration}s I/O)")
    time.sleep(duration)
    return f"Processed {data}"

def io_task_write_results(name: str, *processed_data: str, duration: float) -> str:
    """Simulates writing results to a file or database."""
    print(f"[{name}] Writing {processed_data} results... (simulated {duration}s I/O)")
    time.sleep(duration)
    return f"Results for {processed_data} written"


if __name__ == "__main__":
    print("\n--- Running IO-Bound Task Example ---\n")

    # Define IO-bound tasks with dependencies
    fetch_task_a = Task("Fetch A", io_task_fetch_data, ("Service A", 2), {})
    fetch_task_b = Task("Fetch B", io_task_fetch_data, ("Service B", 1), {})

    process_task_a = Task("Process A", io_task_process_data, ("Data A", fetch_task_a, 3), {})
    process_task_b = Task("Process B", io_task_process_data, ("Data B", fetch_task_b, 2), {})

    write_task_final = Task("Write Final", io_task_write_results, ("Final Report", process_task_a, process_task_b), {'duration': 1})

    tasks = [fetch_task_a, fetch_task_b, process_task_a, process_task_b, write_task_final]

    # Use TaskSchedulerApp
    app = TaskSchedulerApp()
    for task in tasks:
        app.add_task(task)
    app.run()
