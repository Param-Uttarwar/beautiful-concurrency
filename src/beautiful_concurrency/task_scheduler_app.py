import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
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

    def _long_running_task(self, task_name: str, duration: float) -> str:
        """Simulates a long-running task."""
        st.info(f"Running {task_name}...")
        time.sleep(duration)
        return f"{task_name} completed"

    def _create_default_tasks(self) -> list[Task]:
        """Creates a set of example tasks with dependencies."""
        t1 = Task("Task A", self._long_running_task, ("Task A", 2), {})
        t2 = Task("Task B", self._long_running_task, ("Task B", 3), {})
        t3 = Task("Task C", self._long_running_task, ("Task C", 1), {})
        t4 = Task("Task D", self._long_running_task, ("Task D", 4), {})

        return [t1, t2, t3, t4]

    def _build_task_graph_plotly(self, tasks: list[Task]) -> go.Figure:
        """Build a Plotly graph visualization for task dependencies."""
        G = nx.DiGraph()

        for task in tasks:
            G.add_node(task.id, name=task.name)

        for task in tasks:
            for parent in task._parents:
                G.add_edge(parent.id, task.id)

        pos = nx.spring_layout(G)

        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(G.nodes[node]['name'])

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="top center",
            marker=dict(
                showscale=False,
                color='lightblue',
                size=40,
                line_width=5))

        annotations = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            annotations.append(
                dict(
                    ax=x0, ay=y0,
                    axref='x', ayref='y',
                    x=x1, y=y1,
                    xref='x', yref='y',
                    showarrow=True,
                    #arrowhead=1,
                    arrowsize=1,
                    arrowwidth=5,
                    arrowcolor='#888'
                )
            )

        fig = go.Figure(data=[node_trace],
                     layout=go.Layout(
                        title='Task Dependency Graph',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=annotations,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        return fig

    def run(self) -> None:
        st.set_page_config(layout="wide")
        st.title("Task Orchestrator with Gantt Chart")

        # Sidebar for mode selection
        st.sidebar.header("Configuration")
        mode_options = ["sequential", "threading", "multiprocessing", "asyncio"]
        selected_mode = st.sidebar.selectbox("Select Execution Mode", mode_options)

        # Main content area
        st.header(f"Selected Mode: {selected_mode.capitalize()}")

        if not self.tasks:
            st.write("No tasks added, running with default example tasks...")
            tasks_to_run = self._create_default_tasks()
        else:
            st.write(f"Running {len(self.tasks)} custom tasks...")
            tasks_to_run = self.tasks

        if st.button("Run Tasks"):
            col1, col2 = st.columns(2)
            
            with col1:
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

        # Add horizontal line for visual separation
        st.markdown("---")
        # Removed the expander to make the graph static
        if tasks_to_run: # Check if there are tasks to run before building the graph
            if 'task_graph_figure' not in st.session_state:
                st.session_state['task_graph_figure'] = self._build_task_graph_plotly(tasks_to_run)
            st.plotly_chart(st.session_state['task_graph_figure'], use_container_width=True)
        else:
            st.info("No tasks to display in the dependency graph.")



if __name__ == '__main__':
    app = TaskSchedulerApp()
    app.run()
