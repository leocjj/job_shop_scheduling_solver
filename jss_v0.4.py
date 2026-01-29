import random
from datetime import datetime


def create_jobs(jobs, machines):
    tasks = machines

    min_time = 0  # Zero means the machine won't be used
    max_time = 20
    """ jobs_data = [  # task = (machine_id, processing_time).
        [(0, 3), (1, 2), (2, 2)],  # Job0
        [(0, 2), (2, 1), (1, 4)],  # Job1
        [(1, 4), (2, 3)],  # Job2
    ]"""
    machines_ids = [i for i in range(machines)]
    jobs_data = []
    for i in range(jobs):
        row = []
        # Create a copy of machine_ids for each job
        available_machines = machines_ids.copy()
        for j in range(tasks):
            random_index = random.randint(0, len(available_machines) - 1)
            machine = available_machines.pop(random_index)
            duration = random.randint(min_time, max_time)
            row.append((machine, duration))
        jobs_data.append(row)

    return jobs_data


def open_file(file_name):
    job_list = []
    with open(file_name) as f:
        for i, line in enumerate(f):
            if i == 0:
                num_jobs = int(line.split()[-1])
            elif i == 1:
                global MACHINES
                MACHINES = int(line.split()[-1])
            elif 2 <= i <= 4:
                continue
            else:
                job_task = list(map(int, line.split()))
                job_list.append(
                    [
                        x
                        for x in zip(
                            job_task[1::2], job_task[2::2]
                        )  # machines  # processing duration
                    ]
                )
        # assert len(job_list) == num_jobs
        # Only if the number of machines is equal to the number of tasks
        # assert len(job_list[0]) == MACHINES

        return job_list


def validate_output_matrix():
    output_text_mode = string_output_matrix().replace(" ", "").replace("\n", "")
    input_text_mode = to_text(jobs_data).replace("\n", "")
    return output_text_mode == input_text_mode


def validate_output_matrix_2():
    for col in range(len(output_matrix[0])):
        seen = set()
        for row in range(len(output_matrix)):
            if output_matrix[row][col] != " ":
                if output_matrix[row][col] in seen:
                    print(
                        f"Machine {output_matrix[row][col]} is duplicated in column {col}"
                    )
                    return False
                seen.add(output_matrix[row][col])
    return True


def eliminate_zero_durations(jobs_data):
    return [
        [(machine, duration) for machine, duration in job if duration != 0]
        for job in jobs_data
    ]


def add_execution_times(jobs_data):
    jobs_with_times = []
    for job in jobs_data:
        start_time = 0
        job_with_times = []
        for machine, duration in job:
            job_with_times.append([machine, duration, start_time])
            start_time += duration
        jobs_with_times.append(job_with_times)
    return jobs_with_times


def to_text(jobs_data):
    result = []
    for job in jobs_data:
        job_list = []
        for machine, duration in job:
            job_list.extend([machine] * duration)
        result.append("".join(map(str, job_list)))
    return "\n".join(result)


def string_output_matrix():
    s = ""
    for job in output_matrix:
        s += "".join(map(str, job)) + "\n"
    return s


def convert_jobs_data_to_output_string(jobs_data):
    output = ""
    for job_id, job in enumerate(jobs_data):
        output += f"{job_id} "
        for task_id, task in enumerate(job):
            machine, duration = task
            output += f"{machine} {duration} "
        output += "\n"
    return output


def iterete_over_jobs(current_time, verbose=False):
    # Each item position represent the machine number,
    # The value is a list of jobs where the same machine number appears.
    # Example: [[], [4], [3], [2], [0, 1, 5], []] for CURRENT_TIME = 0
    # means that machine 0 has no jobs, machine 1 has job 4, machine 2 has job 3,
    # machine 3 has job 2, machine 4 has jobs 0, 1, 5, machine 5 has no jobs.
    all_jobs_per_machine = []
    for machine in range(MACHINES):
        jobs = []  # List of jobs where the same machine number appears
        for id_job, job in enumerate(data_with_times):
            if job and job[0][0] == machine and job[0][2] == current_time:
                jobs.append(id_job)
        all_jobs_per_machine.append(jobs)
    if verbose:
        print(
            f"All jobs for each machine: {all_jobs_per_machine} for time {current_time}"
        )

    # Find the duration of each job for each machine
    # [[], [4], [2], [1], [1, 1, 5], []] for time 0
    # means that machine 0 has no jobs, machine 1 has job with duration 4,
    # machine 2 has job with duration 2, machine 3 has job with duration 1,
    # machine 4 has jobs with durations 1, 1, 5, machine 5 has no jobs.
    all_durations = []
    for i, case in enumerate(all_jobs_per_machine):
        durations = []
        for j in range(JOBS):
            if j in case:
                durations.append(data_with_times[j][0][1])
        all_durations.append(durations)
    if verbose:
        print(f"All durations for machine: {all_durations} for time {current_time}")

    # Find the index of the smallest duration in each job
    min_durations_indices = []
    for machine, durations in enumerate(all_durations):
        # Check if the list do not have more than one element, this is,
        # a machine has note more than one job to do next.
        if len(durations) <= 1:
            min_durations_indices.append(None)
            continue

        min_index = durations.index(min(durations))

        # Because time zero do not have history to check.
        if current_time == 0:
            min_durations_indices.append(min_index)
            continue

        # Check if the same machine (e.g. machine 4) is still running in a job
        # for current_time, machine 3 has jobs 1, 4, 1 is shorter but job 4 is still running
        # so the min index should be 1 instead of 0
        for job in range(len(output_matrix)):
            if output_matrix[job][-1] == machine:
                if verbose:
                    print(
                        f"Machine {machine} was running in job {job}: {output_matrix[job]}"
                    )
                # Check if the job will continue running in the current_time or not
                if job in all_jobs_per_machine[machine]:
                    if verbose:
                        print(
                            f"and it will continue running in the current time {current_time}"
                        )
                    min_index = all_jobs_per_machine[machine].index(job)
                else:
                    if verbose:
                        print(
                            f"but it finished in the previous time {current_time - 1}"
                        )
                break

        min_durations_indices.append(min_index)

    if verbose:
        print(
            f"Indices of the smallest durations: {min_durations_indices} for time {current_time}"
        )

    # Move the other cases to the next time, this is,
    # leave the case with the smallest duration (or the case that is still running)
    # in the current time and move the other cases to the next time.
    # min_durations_indices[i] is the index of the case with the smallest duration
    """ data_with_times[job_index][task][(machine,duration,current_time)] """
    for machine, job_index in enumerate(min_durations_indices):
        if job_index is not None:  # and data_with_times[job_index]:
            if verbose:
                print(all_jobs_per_machine[machine])
            # dur = data_with_times[job_index][0][1]
            dur = all_durations[machine][min_durations_indices[machine]]
            for index_jobs, job_index_2 in enumerate(all_jobs_per_machine[machine]):
                if index_jobs != min_durations_indices[machine]:
                    if verbose:
                        print(
                            f"Moving all tasks in job {job_index_2}, {dur} time units"
                        )
                    for task in range(len(data_with_times[job_index_2])):
                        data_with_times[job_index_2][task][2] += dur

    # Add the jobs to the output matrix and remove them from the data_with_times
    # whent the current time is the same as the time of the job
    for row, job in enumerate(data_with_times):
        if job and job[0][2] == current_time:
            output_matrix[row].append(job[0][0])  # job[0][0] is the machine number
            if data_with_times[row][0][1] > 1:
                # If the job has more than one time unit,
                data_with_times[row][0][1] -= 1  # subtract 1 to the duration of the job
                data_with_times[row][0][2] += 1  # add 1 to the time of the job
            else:
                data_with_times[row].pop(0)
        else:
            output_matrix[row].append(" ")  # Symbol to represent idle time


MACHINES = 0  # Number of machines, enumerated from 0 to MACHINES - 1
VERBOSE = False

"""
for file_name in [
    "tests/instance100_100.txt",
    "tests/instance200_200.txt",
    "tests/instance300_300.txt",
]:
    jobs_data = open_file(file_name)
"""
# for i in range(100, 1001, 100):

JOBS = 1000
MACHINES = 100
jobs_data = create_jobs(jobs=JOBS, machines=MACHINES)
print(f"{JOBS} by {MACHINES}")

out2 = convert_jobs_data_to_output_string(jobs_data)

# with open(f"tests/instance{i}_{MACHINES}.txt", "w") as file:
#    file.write(out2)
jobs_data = open_file("tests/instance1000_100.txt")
start_time = datetime.now()

output_matrix = []
for _ in range(len(jobs_data)):  # TODO: change to list comprehension
    output_matrix.append([])

data_wo_zeros = eliminate_zero_durations(jobs_data)
data_with_times = add_execution_times(data_wo_zeros)

current_time = 0
while bool([bool(row) for row in data_with_times if row]):
    print(f"Makespan: {current_time}", end="\r")
    iterete_over_jobs(current_time, verbose=VERBOSE)
    current_time += 1

finish_time = datetime.now() - start_time
if validate_output_matrix() and validate_output_matrix_2():
    print(f"The output is correct. Makespan: {current_time} in {finish_time}")
    if VERBOSE:
        print(f"Output matrix:\n{string_output_matrix()}")
else:
    print("The output matrix is incorrect")
