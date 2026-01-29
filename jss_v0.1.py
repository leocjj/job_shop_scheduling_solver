MACHINES = 6  # Number of machines, enumerated from 0 to MACHINES - 1

jobs_data = [
    [(4, 1), (3, 6), (2, 3), (1, 6), (0, 1), (5, 2)],
    [(4, 1), (2, 0), (1, 4), (3, 4), (5, 3), (0, 0)],
    [(3, 1), (5, 5), (1, 0), (2, 0), (0, 4), (4, 1)],
    [(2, 2), (1, 6), (3, 5), (0, 1), (4, 4), (5, 3)],
    [(1, 4), (3, 6), (2, 4), (4, 5), (0, 6), (5, 1)],
    [(3, 0), (4, 5), (1, 4), (5, 4), (2, 4), (0, 4)],
]

expected_output = """
4333333222        111111  055
 4  1111     3333555                  
35555500004                   
22          11111133333  04444555
1111   333333222244444     0000005
  44444 11115555 22220000 
"""

output_matrix = []
for i in range(len(jobs_data)):
    output_matrix.append([])


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


def to_matrix(jobs_data):
    result = []
    for job in jobs_data:
        job_list = []
        for machine, duration in job:
            job_list.extend([machine] * duration)
        result.append(job_list)
    return result


def to_text(jobs_data):
    result = []
    for job in jobs_data:
        job_list = []
        for machine, duration in job:
            job_list.extend([machine] * duration)
        result.append("".join(map(str, job_list)))
    return "\n".join(result)


def print_output_matrix():
    print("Output matrix:")
    for job in output_matrix:
        print(job)


data_wo_zeros = eliminate_zero_durations(jobs_data)
data_with_times = add_execution_times(data_wo_zeros)
# output_matrix = to_matrix(data_wo_zeros)


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
            if job[0][0] == machine and job[0][2] == current_time:
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
                durations.append(data_with_times[j][current_time][1])
        all_durations.append(durations)

    print(f"All durations for machine: {all_durations} for current time {current_time}")

    # Find the index of the smallest duration in each job
    min_durations_indices = []
    for durations in all_durations:
        if len(durations) > 1:  # Check if the list has more than one element
            min_index = durations.index(min(durations))
            min_durations_indices.append(min_index)
        else:
            min_durations_indices.append(None)

    print(
        f"Indices of the smallest durations: {min_durations_indices} for current time {current_time}"
    )

    # Move the other cases to the next time, this is,
    # leave the case with the smallest duration
    # in the current time and move the other cases to the next time.
    # min_durations_indices[i] is the index of the case with the smallest duration
    """ data_with_times[job_index][task][(machine,duration,current_time)] """
    for machine, job_index in enumerate(min_durations_indices):
        if job_index is not None:
            print(all_jobs_per_machine[machine])
            dur = data_with_times[job_index][0][1]
            # TODO: use all_durations instead of data_with_times or delete all_durations code
            for index_jobs, job_index_2 in enumerate(all_jobs_per_machine[machine]):
                if index_jobs != min_durations_indices[machine]:
                    print(f"Moving all tasks in job {job_index_2}, {dur} time units")
                    for task in range(len(data_with_times[job_index_2])):
                        data_with_times[job_index_2][task][2] += dur

    # Add the jobs to the output matrix and remove them from the data_with_times
    # whent the current time is the same as the time of the job
    for row, job in enumerate(data_with_times):
        if job[0][2] == current_time:
            output_matrix[row].append(job[0])
            data_with_times[row].pop(0)
            # data_with_times[job].pop(job)
        else:
            output_matrix[row].append([])

    print_output_matrix()


current_time = 0
for i in range(6):
    iterete_over_jobs(i)
    print_output_matrix()

print()

"""
4333333222        111111  055
 4  1111     3333555                  
35555500004                   
22          11111133333  04444555
1111   333333222244444     0000005
  44444 11115555 22220000 
"""
