import pandas as pd

from StudyElements.Participant import Participant


def get_data(task_ids: list[int], participants: list[Participant]):
    data = []
    for task_id in task_ids:
        for p in participants:
            task = p.get_participant_task(task_id=task_id)
            if task is not None:
                data.append({
                    "participant": p.id,
                    "id": f"task_{task.task_number}",
                    "group": p.studygroup.value,
                    "TTU": task.time_to_understand,
                    "DOU": task.degree_of_understanding,
                    #
                    "structural_aspects": task.structural_aspects,
                    "operation type": task.get_operation_type(),
                    "operand type": task.get_operand_type(),
                    "result type": task.get_result_type(),
                    "Ref. direction": task.get_reference_direction(),
                    "Ref. dispersion": task.get_reference_dispersion(),
                })
            else:
                raise Exception(f"missing task {p.id}_{task_id}")
    df = pd.DataFrame(data)
    return df


