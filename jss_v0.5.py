import random
from datetime import datetime


def create_jobs(jobs, machines):
    min_time = 0  # Zero means the machine won't be used
    max_time = 20
    machines_ids = list(range(machines))
    jobs_data = [
        [
            (machine, random.randint(min_time, max_time))
            for machine in random.sample(machines_ids, machines)
        ]
        for _ in range(jobs)
    ]
    return jobs_data


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


def validate_output_matrix():
    output_text_mode = string_output_matrix().replace(" ", "").replace("\n", "")
    input_text_mode = to_text(jobs_data).replace("\n", "")
    return output_text_mode == input_text_mode


def validate_output_matrix_2():
    for col in range(len(output_matrix[0])):
        seen = set()
        for row in output_matrix:
            machine = row[col]
            if machine != " ":
                if machine in seen:
                    print(f"Machine {machine} is duplicated in column {col}")
                    return False
                seen.add(machine)
    return True


def eliminate_zero_durations(jobs_data):
    return [
        [(machine, duration) for machine, duration in job if duration != 0]
        for job in jobs_data
    ]


def add_execution_times(jobs_data):
    return [
        [
            [machine, duration, sum(duration for _, duration in job[:i])]
            for i, (machine, duration) in enumerate(job)
        ]
        for job in jobs_data
    ]


def to_text(jobs_data):
    return "\n".join(
        "".join(str(machine) * duration for machine, duration in job)
        for job in jobs_data
    )


def string_output_matrix():
    return "\n".join("".join(map(str, job)) for job in output_matrix)


def convert_jobs_data_to_output_string(jobs_data):
    return "\n".join(
        f"{job_id} " + " ".join(f"{machine} {duration}" for machine, duration in job)
        for job_id, job in enumerate(jobs_data)
    )


def iterete_over_jobs(current_time, verbose=False):
    # Each item position represent the machine number,
    # The value is a list of jobs where the same machine number appears.
    # Example: [[], [4], [3], [2], [0, 1, 5], []] for CURRENT_TIME = 0
    # means that machine 0 has no jobs, machine 1 has job 4, machine 2 has job 3,
    # machine 3 has job 2, machine 4 has jobs 0, 1, 5, machine 5 has no jobs.
    all_jobs_per_machine = [
        [
            id_job
            for id_job, job in enumerate(data_with_times)
            if job and job[0][0] == machine and job[0][2] == current_time
        ]
        for machine in range(MACHINES)
    ]
    if verbose:
        print(
            f"All jobs for each machine: {all_jobs_per_machine} for time {current_time}"
        )

    # Find the duration of each job for each machine
    # [[], [4], [2], [1], [1, 1, 5], []] for time 0
    # means that machine 0 has no jobs, machine 1 has job with duration 4,
    # machine 2 has job with duration 2, machine 3 has job with duration 1,
    # machine 4 has jobs with durations 1, 1, 5, machine 5 has no jobs.
    all_durations = [
        [data_with_times[j][0][1] for j in case] for case in all_jobs_per_machine
    ]
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
        for job, last_machine in enumerate(output_matrix):
            if last_machine and last_machine[-1] == machine:
                if verbose:
                    print(f"Machine {machine} was running in job {job}: {last_machine}")
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
        if job_index is not None:
            if verbose:
                print(all_jobs_per_machine[machine])
            dur = all_durations[machine][job_index]
            for index_jobs, job_index_2 in enumerate(all_jobs_per_machine[machine]):
                if index_jobs != job_index:
                    if verbose:
                        print(
                            f"Moving all tasks in job {job_index_2}, {dur} time units"
                        )
                    for task in data_with_times[job_index_2]:
                        task[2] += dur

    # Add the jobs to the output matrix and remove them from the data_with_times
    # whent the current time is the same as the time of the job
    for row, job in enumerate(data_with_times):
        if job and job[0][2] == current_time:
            output_matrix[row].append(job[0][0])  # job[0][0] is the machine number
            if job[0][1] > 1:
                job[0][1] -= 1  # subtract 1 from the duration of the job
                job[0][2] += 1  # add 1 to the time of the job
            else:
                job.pop(0)
        else:
            output_matrix[row].append(" ")  # Symbol to represent idle time


VERBOSE = False

"""
for file_name in [
    "tests/instance100_100.txt",
    "tests/instance200_200.txt",
    "tests/instance300_300.txt",
]:
    jobs_data = open_file(file_name)
"""

JOBS = 10000
MACHINES = 100

# To create random jobs
jobs_data = create_jobs(jobs=JOBS, machines=MACHINES)
print(f"{JOBS} by {MACHINES}, tasks: {JOBS * MACHINES}")
# To save the random jobs in a file
# out2 = convert_jobs_data_to_output_string(jobs_data)
# with open(f"tests/instance{JOBS}_{MACHINES}.txt", "w") as file:
#    file.write(out2)

# To open a file with jobs
# jobs_data = open_file("tests/instance1000_100.txt")

start_time = datetime.now()

output_matrix = [[] for _ in range(len(jobs_data))]
data_wo_zeros = eliminate_zero_durations(jobs_data)
data_with_times = add_execution_times(data_wo_zeros)

current_time = 0
while any(data_with_times):
    if current_time % 1000 == 0:
        print(f"Makespan: {current_time}", end=" ")
        finish_time = datetime.now() - start_time
        print(f"Time elapsed: {finish_time}")
        if current_time > 90000:
            print("Finishing")
    iterete_over_jobs(current_time, verbose=VERBOSE)
    current_time += 1

finish_time = datetime.now() - start_time

if validate_output_matrix() and validate_output_matrix_2():
    print(f"The output is correct. Makespan: {current_time} in {finish_time}")
    if VERBOSE:
        print(f"Output matrix:\n{string_output_matrix()}")
else:
    print("The output matrix is incorrect")
