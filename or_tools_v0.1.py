import collections
from datetime import datetime

from ortools.sat.python import cp_model


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables: list[cp_model.IntVar], one_solution=False):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__one_solution = one_solution
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        # print(datetime.now().strftime("%H:%M:%S"), end=" ")
        if self.__one_solution:
            for v in self.__variables:
                print(f" {v}={self.value(v)}", end=" ")
            # sys.exit(0)
            # Throws an exception to interrupt the search.
            raise Exception("Interrupt search")

    @property
    def solution_count(self) -> int:
        return self.__solution_count


def open_file(file_name):
    with open(file_name) as f:
        lines = f.readlines()

    num_jobs = int(lines[0].split()[-1])
    global MACHINES
    MACHINES = int(lines[1].split()[-1])

    job_list = [
        [(job_task[i], job_task[i + 1]) for i in range(1, len(job_task), 2)]
        for job_task in (list(map(int, line.split())) for line in lines[5:])
    ]

    return job_list


def calculate(jobs_data, one_solution):
    """Minimal jobshop problem."""
    # print(datetime.now().strftime("%H:%M:%S"))

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)
    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Create the model.
    model = cp_model.CpModel()

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple("task_type", "start end interval")
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple(
        "assigned_task_type", "start job index duration"
    )

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine, duration = task
            suffix = f"_{job_id}_{task_id}"
            start_var = model.new_int_var(0, horizon, "start" + suffix)
            end_var = model.new_int_var(0, horizon, "end" + suffix)
            interval_var = model.new_interval_var(
                start_var, duration, end_var, "interval" + suffix
            )
            all_tasks[job_id, task_id] = task_type(
                start=start_var, end=end_var, interval=interval_var
            )
            machine_to_intervals[machine].append(interval_var)

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.add_no_overlap(machine_to_intervals[machine])

    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.add(
                all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end
            )

    # Makespan objective.
    obj_var = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(
        obj_var,
        [all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(jobs_data)],
    )
    model.minimize(obj_var)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()

    solution_printer = VarArraySolutionPrinter([obj_var], one_solution=one_solution)
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True
    # Solve.
    try:
        status = solver.solve(model, solution_printer)
    except Exception:
        return

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # print("Solution:")
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(
                        start=solver.value(all_tasks[job_id, task_id].start),
                        job=job_id,
                        index=task_id,
                        duration=task[1],
                    )
                )

        # Create per machine output lines.
        output = ""
        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()
            sol_line_tasks = "Machine " + str(machine) + ": "
            sol_line = "           "

            for assigned_task in assigned_jobs[machine]:
                name = f"job_{assigned_task.job}_task_{assigned_task.index}"
                # add spaces to output to align columns.
                sol_line_tasks += f"{name:15}"

                start = assigned_task.start
                duration = assigned_task.duration
                sol_tmp = f"[{start},{start + duration}]"
                # add spaces to output to align columns.
                sol_line += f"{sol_tmp:15}"

            sol_line += "\n"
            sol_line_tasks += "\n"
            output += sol_line_tasks
            output += sol_line

        # Finally print the solution found.
        print(f" makespan={solver.objective_value:.0f}", end=" ")
        # print(output)
    else:
        print("No solution found.")

    # Statistics.
    # print("\nStatistics")
    # print(f"  - conflicts: {solver.num_conflicts}")
    # print(f"  - branches : {solver.num_branches}")
    # print(f"  - wall time: {solver.wall_time:.2f} s")
    # print(f"{solver.wall_time:.2f}")

    return round(solver.objective_value, 2)

    """
    # Create a chart representation using different colors for each job and task
    max_time = int(solver.objective_value)
    chart = [[' '] * max_time for _ in range(len(all_machines))]

    for machine in all_machines:
        for assigned_task in assigned_jobs[machine]:
            start = assigned_task.start
            duration = assigned_task.duration
            job_id = assigned_task.job
            task_id = assigned_task.index

            # Define colors for each job (you can customize these)
            job_colors = ['\033[91m', '\033[92m', '\033[94m', '\033[93m', '\033[95m']
            color_code = job_colors[job_id % len(job_colors)]
            reset_color_code = '\033[0m'

            for i in range(start, start + duration):
                if i < max_time:
                    chart[machine][i] = color_code + chr(ord('A') + job_id * 10 + task_id) + reset_color_code

    print("\nChart Representation (with job/task color differentiation):")
    for row in chart:
        print(''.join(row))
    """


def main(jobs_data, VERBOSE=False):
    start_time = datetime.now()
    calculate(jobs_data, one_solution=True)
    finish_time = datetime.now() - start_time
    print(f"in {finish_time}")


for file_name in [
    "tests5/instance15_15.txt",
    "tests5/instance30_30.txt",
    "tests5/instance100_10.txt",
    "tests5/instance100_30.txt",
    "tests5/instance1000_100.txt",
    "tests5/instance1500_100.txt",
    "tests5/instance2000_100.txt",
    "tests5/instance2500_100.txt",
]:
    jobs_data = open_file(file_name)
    print(file_name, end=" ")
    main(jobs_data)
