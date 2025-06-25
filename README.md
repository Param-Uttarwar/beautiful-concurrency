# beautiful-concurrency

A Streamlit-based UI to visualize and execute concurrent tasks in Python using different execution models (sequential, threading, multiprocessing, asyncio). This project helps in understanding how various concurrency paradigms affect task execution and overall performance, especially when tasks have dependencies.

## Features

- **Task Orchestration**: Define tasks with inter-dependencies.
- **Multiple Execution Modes**: Run tasks in sequential, threading, multiprocessing, or asyncio modes.
- **Interactive UI**: Visualize task execution flow with a Gantt chart.
- **Dependency Graph**: See a clear visualization of task dependencies.

## Installation

To get started with `beautiful-concurrency`, you can install it directly from PyPI (once published) or set it up for local development.

### From PyPI (Recommended)

```bash
pip install beautiful-concurrency
```

### For Local Development

If you want to contribute or modify the source code, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Param-Uttarwar/beautiful-concurrency.git
    cd beautiful-concurrency
    ```
2.  **Install in editable mode**: This will install the project and its dependencies, allowing you to make changes to the source code without re-installing.
    ```bash
    pip install -e .
    ```


## Usage

The core of `beautiful-concurrency` is the `TaskSchedulerApp`, which allows you to define and run tasks using different concurrency modes.


## Demo Examples

The `examples/` directory contains pre-defined examples demonstrating how to use the `Task` and `Orchestrator` classes for different types of workloads.

You can create your own tasks and run them using the `TaskSchedulerApp` as follows:


### 1. Compute-Intensive Tasks

This example showcases tasks that primarily consume CPU resources, such as finding prime factors and calculating Fibonacci numbers.

To run this example:

```bash
streamlit run examples/example_compute_intensive.py
```

### 2. I/O-Bound Tasks

This example demonstrates tasks that spend most of their time waiting for I/O operations (e.g., network requests, disk reads/writes).

To run this example:

```bash
streamlit run examples/example_io_bound.py
```
### 3. Custom Example
```python
# Custom Example for Custom Tasks
from beautiful_concurrency.base.task import Task
from beautiful_concurrency.task_scheduler_app import TaskSchedulerApp

def foo(param1: str) -> str:
    print(f"Doing work with {param1}...")
    # Simulate work
    return f"Result {param1}"

def bar(param1: str, param2: str) -> str: 
    print(f"Doing work with {param1} and {param2}...")
    # Simulate work
    return f"Result {param1} {param2}"

# Create Task instances
task_foo = Task("Task foo", foo, ("value_a"), {})
task_bar = Task("Task bar", bar, ("value_b", task_1), {}) # it automatically takes result of foo as input

# Initialize TaskSchedulerApp
app = TaskSchedulerApp()

# Add tasks to the app
app.add_task(task_1)
app.add_task(task_2)

# Run the app
app.run()
```