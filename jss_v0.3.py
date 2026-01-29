MACHINES = 30  # Number of machines, enumerated from 0 to MACHINES - 1

jobs_data = [
    [(4, 1), (3, 6), (2, 3), (1, 6), (0, 1), (5, 2)],
    [(4, 1), (2, 0), (1, 4), (3, 4), (5, 3), (0, 0)],
    [(3, 1), (5, 5), (1, 0), (2, 0), (0, 4), (4, 1)],
    [(2, 2), (1, 6), (3, 5), (0, 1), (4, 4), (5, 3)],
    [(1, 4), (3, 6), (2, 4), (4, 5), (0, 6), (5, 1)],
    [(3, 0), (4, 5), (1, 4), (5, 4), (2, 4), (0, 4)],
]

file_name = "tests/instance30_30.txt"


def open_file(file_name):
    job_list = []
    with open(file_name) as f:
        for i, line in enumerate(f):
            if i == 0:
                num_jobs = int(line.split()[-1])
            elif i == 1:
                num_machines = int(line.split()[-1])
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
        assert len(job_list) == num_jobs
        assert len(job_list[0]) == num_machines

        return job_list

    # prompt: convert list_data table to a list of rows where each row has tuples of two elements

    list_data = [list(map(int, row.split())) for row in raw_data.splitlines()]

    # Create a list of rows where each row has tuples of two elements
    new_list_data = []
    for row in list_data:
        new_row = []
        for i in range(0, len(row), 2):
            if i + 1 < len(row):
                new_row.append((row[i], row[i + 1]))
        new_list_data.append(new_row)


jobs_data = open_file(file_name)

output_matrix = []
for _ in range(len(jobs_data)):
    output_matrix.append([])


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


"""
def to_matrix(jobs_data):
    result = []
    for job in jobs_data:
        job_list = []
        for machine, duration in job:
            job_list.extend([machine] * duration)
        result.append(job_list)
    return result
"""


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


data_wo_zeros = eliminate_zero_durations(jobs_data)
data_with_times = add_execution_times(data_wo_zeros)


def iterete_over_jobs(current_time):
    # Each item position represent the machine number,
    # The value is a list of jobs where the same machine number appears.
    # Example: [[], [4], [3], [2], [0, 1, 5], []] for time 0
    # means that machine 0 has no jobs, machine 1 has job 4, machine 2 has job 3,
    # machine 3 has job 2, machine 4 has jobs 0, 1, 5, machine 5 has no jobs.
    all_jobs_per_machine = []
    for machine in range(MACHINES):
        jobs = []  # List of jobs where the same machine number appears
        for id_job, job in enumerate(data_with_times):
            if job and job[0][0] == machine and job[0][2] == current_time:
                jobs.append(id_job)
        all_jobs_per_machine.append(jobs)
    print(f"All jobs for each machine: {all_jobs_per_machine} for time {current_time}")

    # Find the duration of each job for each machine
    # [[], [4], [2], [1], [1, 1, 5], []] for time 0
    # means that machine 0 has no jobs, machine 1 has job with duration 4,
    # machine 2 has job with duration 2, machine 3 has job with duration 1,
    # machine 4 has jobs with durations 1, 1, 5, machine 5 has no jobs.
    all_durations = []
    for i, case in enumerate(all_jobs_per_machine):
        durations = []
        for j in range(MACHINES):
            if j in case:
                durations.append(data_with_times[j][0][1])
        all_durations.append(durations)
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
                print(
                    f"Machine {machine} was running in job {job}: {output_matrix[job]}"
                )
                # Check if the job will continue running in the current_time or not
                if job in all_jobs_per_machine[machine]:
                    print(
                        f"and it will continue running in the current time {current_time}"
                    )
                    min_index = all_jobs_per_machine[machine].index(job)
                else:
                    print(f"but it finished in the previous time {current_time - 1}")
                break

        min_durations_indices.append(min_index)

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
            print(all_jobs_per_machine[machine])
            # dur = data_with_times[job_index][0][1]
            dur = all_durations[machine][min_durations_indices[machine]]
            for index_jobs, job_index_2 in enumerate(all_jobs_per_machine[machine]):
                if index_jobs != min_durations_indices[machine]:
                    print(f"Moving all tasks in job {job_index_2}, {dur} time units")
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


# current_time = 0
for current_time in range(1000):
    iterete_over_jobs(current_time)
    if not bool([bool(row) for row in data_with_times if row]):
        break


if validate_output_matrix() and validate_output_matrix_2():
    print("\nThe output matrix is correct")
    print(f"Makespan: {current_time}")
    # print(f"Output matrix:\n{string_output_matrix()}")
else:
    print("The output matrix is incorrect")

print()
