import streamlit as st
import pandas as pd
import plotly.express as px
import time
from beautiful_concurrency.base.task import Task
from beautiful_concurrency.base.orchestrator import Orchestrator


class TaskSchedulerApp:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.tasks = []

    def add_task(self, task: Task):
        """Adds a task to the scheduler."""
        self.tasks.append(task)

    def _long_running_task(self, task_name, duration):
        """Simulates a long-running task."""
        st.info(f"Running {task_name}...")
        time.sleep(duration)
        return f"{task_name} completed"

    def _create_default_tasks(self):
        """Creates a set of example tasks with dependencies."""
        t1 = Task("Task A", self._long_running_task, ("Task A", 2), {})
        t2 = Task("Task B", self._long_running_task, ("Task B", 3), {})
        t3 = Task("Task C", self._long_running_task, ("Task C", 1), {})
        t4 = Task("Task D", self._long_running_task, ("Task D", 4), {})

        return [t1, t2, t3, t4]

    def run(self):
        st.set_page_config(layout="wide")
        st.title("Task Orchestrator with Gantt Chart")

        # Sidebar for mode selection
        st.sidebar.header("Configuration")
        mode_options = ["sequential", "threading", "multiprocessing", "asyncio"]
        selected_mode = st.sidebar.selectbox("Select Execution Mode", mode_options)

        # Main content area
        st.header(f"Selected Mode: {selected_mode.capitalize()}")

        if st.button("Run Tasks"):
            col1, col2 = st.columns(2)
            
            with col1:
                if not self.tasks:
                    st.write("No tasks added, running with default example tasks...")
                    tasks_to_run = self._create_default_tasks()
                else:
                    st.write(f"Running {len(self.tasks)} custom tasks...")
                    tasks_to_run = self.tasks
                
                start_app_time = time.perf_counter()
                try:
                    self.orchestrator.run(tasks_to_run, mode=selected_mode)
                    end_app_time = time.perf_counter()
                    st.success(f"All tasks completed in {end_app_time - start_app_time:.2f} seconds!")

                except Exception as e:
                    st.error(f"An error occurred during task execution: {e}")

            with col2:
                # Prepare data for Gantt chart
                gantt_data = []
                first_start_time = min(task.time_started for task in tasks_to_run if task.time_started is not None)
                for task in tasks_to_run:
                    if task.time_started is not None and task.time_completed is not None:
                        gantt_data.append(dict(
                            Task=task.name,
                            Start=task.time_started - first_start_time,
                            Finish=task.time_completed - first_start_time,
                            State=task.state.name  # Using the name of the Status enum
                        ))

                if gantt_data:
                    df = pd.DataFrame(gantt_data)

                    # Convert relative times to actual timestamps for Plotly if needed
                    # For Gantt chart, relative times from a common start point are fine
                    df['Start'] = pd.to_datetime(df['Start'], unit='s')
                    df['Finish'] = pd.to_datetime(df['Finish'], unit='s')

                    # Calculate duration for color scaling
                    df['Duration'] = df['Finish'] - df['Start']
                    df['DurationSeconds'] = df['Duration'].dt.total_seconds().round(2)

                    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="State",
                                      color_discrete_map={'COMPLETED': 'green', 'FAILED': 'red', 'RUNNING': 'blue', 'PENDING': 'gray'},
                                      title="Task Execution Gantt Chart",
                                      hover_name="Task",
                                      text="DurationSeconds")  # Show duration as text on bars

                    fig.update_xaxes(title="Time (HH:MM:SS:LLL)",tickformat="%H:%M:%S:%L") # Add x-axis label
                    fig.update_yaxes(autorange="reversed")  # tasks at the top are the ones that started earlier
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.warning("No task data available to generate Gantt chart. Ensure tasks ran successfully.")


        # st.write("### How to Use:")
        # st.write("1. Select an execution mode from the sidebar.")
        # st.write("2. Click the 'Run Tasks' button.")
        # st.write("3. Observe the task execution and the generated Gantt chart.")


if __name__ == '__main__':
    app = TaskSchedulerApp()
    # You can add custom tasks here before running the app
    # Example:
    # def my_custom_func(x, y):
    #     return x + y
    # app.add_task(Task("Custom Task 1", my_custom_func, (10, 20), {}))
    app.run()
