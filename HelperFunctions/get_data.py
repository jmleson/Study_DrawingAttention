import pandas as pd

from HelperFunctions.time_to_seconds import time_to_seconds
from StudyElements.Participant import Participant



def get_data(task_ids: list[int], participants: list[Participant]):
    data = []
    for task_id in task_ids:
        for p in participants:
            task = p.get_participant_task(task_id=task_id)
            if task is not None:
                assert task.video_length_in_s is not None
                info = {
                    "participant": p.id,
                    "task_id": f"{task.task_number}",
                    "group": p.studygroup.value,
                    "TTU": task.time_to_understand,
                    "DOU": task.degree_of_understanding,
                    #
                    "structural_aspects": task.structural_aspects,
                    "video_length_in_s": task.video_length_in_s,
                    "timestamp_where_participant_realizes": time_to_seconds(task.understanding)
                    # "operation_type": task.get_operation_type(),
                    # "operand_type": task.get_operand_type(),
                    # "result_type": task.get_result_type(),
                    # "Ref_direction": task.get_reference_direction(),
                    # "Ref_dispersion": task.get_reference_dispersion(),
                }
                try:
                    info["TTU_second_coder"] = task.secondCoder_time_to_understand
                    info["DOU_second_coder"] = task.secondCoder_degree_of_understanding
                    info["timestamp_where_participant_realizes_second_coder"] = time_to_seconds(task.secondCoder_understanding)
                except Exception as e:
                    print(e)
                    info["TTU_second_coder"] = None
                    info["DOU_second_coder"] = None
                    info["timestamp_where_participant_realizes_second_coder"] = None

                data.append(info)
            else:
                raise Exception(f"missing task {p.id}_{task_id}")
    df = pd.DataFrame(data)
    return df


