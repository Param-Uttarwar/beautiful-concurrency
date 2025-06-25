import time
import math
from beautiful_concurrency.base.task import Task
from beautiful_concurrency.base.orchestrator import Orchestrator
from beautiful_concurrency.task_scheduler_app import TaskSchedulerApp

def compute_prime_factors(name: str, number: int) -> int:
    """Simulates a compute-intensive task: finding prime factors."""
    print(f"[{name}] Finding prime factors for {number}...")
    factors = []
    d = 2
    temp = number
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            temp //= d
        else:
            d += 1
    if temp > 1:
        factors.append(temp)
    time.sleep(0.1) # Simulate some minimal work if computation is too fast
    return len(factors)  # Return the count of prime factors as a result

def compute_fibonacci(name: str, n: int) -> int:
    """Simulates a compute-intensive task: calculating Fibonacci number."""
    print(f"[{name}] Calculating Fibonacci({n})...")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    time.sleep(0.1) # Simulate some minimal work if computation is too fast
    return a

def compute_complex_calculation(name: str, val1: int, val2: int) -> float:
    """Simulates a complex calculation that depends on other results."""
    print(f"[{name}] Performing complex calculation with {val1} and {val2}...")
    result = (val1 * 0.5) + val2 / 2
    time.sleep(0.2) # Simulate some minimal work
    return result


if __name__ == "__main__":
    print("\n--- Running Compute-Intensive Task Example ---\n")

    # Define compute-intensive tasks with dependencies
    prime_task_1 = Task("Prime Factors 1", compute_prime_factors, ("Num 1", 1234567), {})
    fib_task_1 = Task("Fibonacci 1", compute_fibonacci, ("N1", 30), {})

    prime_task_2 = Task("Prime Factors 2", compute_prime_factors, ("Num 2", 7654321), {})
    fib_task_2 = Task("Fibonacci 2", compute_fibonacci, ("N2", 35), {})

    complex_task_a = Task("Complex Calc A", compute_complex_calculation, ("Calc A", prime_task_1, fib_task_1), {})
    complex_task_b = Task("Complex Calc B", compute_complex_calculation, ("Calc B", prime_task_2, fib_task_2), {})


    tasks = [
        prime_task_1, fib_task_1,
        prime_task_2, fib_task_2,
        complex_task_a, complex_task_b,
    ]

    # Use TaskSchedulerApp
    app = TaskSchedulerApp()
    for task in tasks:
        app.add_task(task)
    app.run()