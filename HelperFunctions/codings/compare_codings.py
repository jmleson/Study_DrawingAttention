from HelperFunctions.time_to_seconds import time_to_seconds
from Study import participants, tasks


def get_both_codings():
    ttu = []
    dou = []
    ttu_secondCoder = []
    dou_secondCoder = []
    realization = []
    realization_secondCoder = []

    id = []

    for p in participants:
        for task in tasks:
            p.create_task_files(task=task)
            try:
                p.create_task_files_2nd_coding(task=task)
            except:
                pass

    for p in participants:
        for task in p.tasks:
            try:
                # print(task.raw_data_secondCoder)
                print(task.task_number, task.degree_of_understanding, task.time_to_understand,
                      task.secondCoder_time_to_understand, task.degree_of_understanding)
                id.append(f"{p.id}_{task.task_number}")
                ttu.append(
                    task.time_to_understand
                )
                dou.append(task.degree_of_understanding)
                realization.append(time_to_seconds(task.understanding))

                ttu_secondCoder.append( task.secondCoder_time_to_understand)
                dou_secondCoder.append( task.secondCoder_degree_of_understanding)
                realization_secondCoder.append( time_to_seconds(task.understanding))

            except Exception as e:
                pass

    return id, ttu, dou, ttu_secondCoder, dou_secondCoder, realization, realization_secondCoder


