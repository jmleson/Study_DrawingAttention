

import SETTINGS as settings


import json
import os
from openpyxl import load_workbook

from StudyElements.Participanttask import ParticipantTask
from StudyElements.STUDYGROUP import STUDYGROUP
from StudyElements.Task import Task


class Participant(object):

    def __init__(self, id:str, studygroup: STUDYGROUP):
        self.id = id
        self.studygroup = studygroup
        self.tasks = []


    def get_data_directory(self):
        return f"DATA/participant_{self.id}/"

    def get_demographics_filename(self):
        return self.get_data_directory() + f"demographics_{self.id}.json"

    def create_task_files(self, task:Task):

        filename = f"task_{self.id}_{task.task_number}.json"
        ########### USE JSON
        if settings.DATA_INPUT == "JSON":
            with open(self.get_data_directory()+filename, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                p_task = ParticipantTask(p_id=self.id, task=task)
                p_task.set_raw_data(raw_data)#, info=f"{self.id}_{task.task_number}")
                self.add_participant_task(p_task=p_task)
            # print(f"✓ Loaded from JSON: {filename}")
            return

        ########### READ FROM EXCEL FILE #########
        if settings.DATA_INPUT == "EXCEL":
            output_dir = self.get_data_directory()
            wb = load_workbook("DATA/Data_Study_KEO_Analyzing_Complete.xlsx", data_only=True)
            ws = wb[f"{self.id}({self.studygroup.name})"]

            task_line = task.get_excel_line()
            template = {
                    "Task ID": ws[f"A{task_line}"].value,# just to be sure
                    "Result Cell understood (1 / 0)": {
                        "explicitly mentioned": ws[f"I{task_line}"].value,
                        "implied understand": ws[f"J{task_line}"].value
                    },
                    "each operation understood (1 point for each)": {
                        "explicitly mentioned": ws[f"K{task_line}"].value,
                        "implied understanding": ws[f"L{task_line}"].value
                    },
                    "each expected operand understood (1 point for each)": {
                        "explicitly mentioned": ws[f"M{task_line}"].value,
                        "implied understanding": ws[f"N{task_line}"].value
                    },
                    "Result Type understood (1.0/0.5/0)": {
                        "explicitly mentioned": ws[f"O{task_line}"].value,
                        "implied understanding": ws[f"P{task_line}"].value
                    },
                    "start (of new slide)": str(ws[f"S{task_line}"].value),
            }
            if self.studygroup == STUDYGROUP.V:
                template["End of video"] = str(ws[f"T{task_line}"].value),
                template["timestamp where participant realizes"] = str(ws[f"U{task_line}"].value)
                template["end of this slide"] = str(ws[f"V{task_line}"].value)
                template["notes"] = str(ws[f"W{task_line}"].value)
            else:
                template["timestamp where participant realizes"] = str(ws[f"T{task_line}"].value)
                template["end of this slide"] = str(ws[f"U{task_line}"].value)
                template["notes"] = str(ws[f"V{task_line}"].value)

            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            print(f"! Updated Data from Excel for: {filepath}")
            p_task = ParticipantTask(p_id=self.id, task=task)
            p_task.set_raw_data(template)# info=f"{self.id}_{task.task_number}")
            self.add_participant_task(p_task=p_task)
        return


    def create_task_files_2nd_coding(self, task:Task):

        p_task = None
        for referenced_task in self.tasks:
            if referenced_task.task_number == task.task_number:
                p_task = referenced_task
        if p_task is None:
            raise Exception("Task not found")
            return

        filename = f"2nd_task_{self.id}_{task.task_number}.json"
        try_again = False
        ########### USE JSON
        if settings.DATA_INPUT == "JSON":
            try:
                with open(self.get_data_directory()+filename, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    p_task.set_raw_data_secondCoder(raw_data)#, info=f"{self.id}_{task.task_number}")

                    p_task.secondCoder_time_to_understand # INFO: testing whether it was added
            except Exception as e:
                try_again = True
                # self.add_participant_task(p_task=p_task)
            # print(f"✓ Loaded from JSON: {filename}")
            if not try_again:
                return

        ########### READ FROM EXCEL FILE #########
        if try_again or settings.DATA_INPUT == "EXCEL":
            output_dir = self.get_data_directory()
            wb = load_workbook("DATA/Data_Study_VJV_Analyzing_Complete.xlsx", data_only=True)
            ws = wb[f"{self.id}({self.studygroup.name})"]

            task_line = task.get_excel_line()
            template = {
                    "Task ID": ws[f"A{task_line}"].value,# just to be sure
                    "Result Cell understood (1 / 0)": {
                        "explicitly mentioned": ws[f"I{task_line}"].value,
                        "implied understand": ws[f"J{task_line}"].value
                    },
                    "each operation understood (1 point for each)": {
                        "explicitly mentioned": ws[f"K{task_line}"].value,
                        "implied understanding": ws[f"L{task_line}"].value
                    },
                    "each expected operand understood (1 point for each)": {
                        "explicitly mentioned": ws[f"M{task_line}"].value,
                        "implied understanding": ws[f"N{task_line}"].value
                    },
                    "Result Type understood (1.0/0.5/0)": {
                        "explicitly mentioned": ws[f"O{task_line}"].value,
                        "implied understanding": ws[f"P{task_line}"].value
                    },
                    "start (of new slide)": str(ws[f"S{task_line}"].value),
            }
            if self.studygroup == STUDYGROUP.V:
                template["End of video"] = str(ws[f"T{task_line}"].value),
                template["timestamp where participant realizes"] = str(ws[f"U{task_line}"].value)
                template["end of this slide"] = str(ws[f"V{task_line}"].value)
                template["notes"] = str(ws[f"W{task_line}"].value)
            else:
                template["timestamp where participant realizes"] = str(ws[f"T{task_line}"].value)
                template["end of this slide"] = str(ws[f"U{task_line}"].value)
                template["notes"] = str(ws[f"V{task_line}"].value)

            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            print(f"! Updated Data from Excel for: {filepath}")
            p_task.set_raw_data_secondCoder(template)# info=f"{self.id}_{task.task_number}")
            # self.add_participant_task(p_task=p_task)
        return

    def add_participant_task(self, p_task:ParticipantTask):
        task_ids = []
        for t in self.tasks:
            task_ids.append(t.id)
        if p_task.id not in task_ids:
            self.tasks.append(p_task)

    def get_participant_task(self, task_id:int):
        for i in self.tasks:
            if i.task_number == task_id:
                return i
        print(f"task not found {task_id} in", [i.task_number for i in self.tasks])
        return None

