from datetime import datetime, time, timedelta

from StudyElements.Task import Task


class ParticipantTask(Task):

    def __init__(self, p_id:str, task:Task):
        super().__init__(number=task.task_number, max_total=task.task_max_total, description=task.task_description,
                         expected_operands=task.task_expected_operands, expected_result_cell=task.task_expected_result_cell,
                         expected_operations=task.task_expected_operations, result_type=task.task_result_type,
                         formula=task.task_formula
                         )
        self.structural_aspects = task.structural_aspects
        self.p_id = p_id

        self.id = f"{self.p_id}-{self.task_number}"

        self.raw_data = {}
        self.secondCoder_raw_data = {}


    def parse_time_data(self, value:str):
        if " "in value:
            value = value.split(" ")[-1]

        if value is None or value == "None":
            return
        minutes, seconds, milliseconds = value.split(":")
        if milliseconds != "00":
           raise Exception("milliseconds or whatever")
        try:
            value = time(
                hour=0,
                minute=int(minutes),
                second=int(seconds)
            )
        except Exception as e:
            print(value, flush=True)
            print(e)
        return value



    def set_raw_data(self, raw_data:dict):
        if len(self.raw_data) > 0:
            return
        self.raw_data = raw_data

        #TODO separat abspeichern:
        self.start = self.parse_time_data(self.raw_data["start (of new slide)"])
        self.understanding = self.parse_time_data(value=self.raw_data["timestamp where participant realizes"])

        start_dt = datetime.combine(datetime.today(), self.start)
        understanding_dt = datetime.combine(datetime.today(), self.understanding)
        if understanding_dt < start_dt:# ggf. Datumswechsel berücksichtigen
            understanding_dt += timedelta(hours=1)
        time_diff = understanding_dt - start_dt
        self.time_to_understand = time_diff.total_seconds()

        self.understood_result_cell = raw_data["Result Cell understood (1 / 0)"]
        self.understood_result_type = raw_data["Result Type understood (1.0/0.5/0)"]
        self.understood_operation = raw_data["each operation understood (1 point for each)"]
        self.understood_operand = raw_data["each expected operand understood (1 point for each)"]

        self.total = [
            value if value != "x" and value is not None else 0
            for value in (
                *self.understood_operand.values(),
                *self.understood_operation.values(),
                *self.understood_result_type.values(),
                *self.understood_result_cell.values()
            )
        ]
        self.total = sum(self.total)
        self.degree_of_understanding = self.total / self.task_max_total

        self.notes = self.raw_data["notes"]
        self.skipped = False

        if not self.time_to_understand >= 0:
            self.skipped = True
            print("VERY STRANGE BEHAVIOR", self.p_id, self.task_id, "negative time")
            print("TTU:", self.time_to_understand, "=", self.understanding, "-", self.start)
            self.time_to_understand = None
        if len(self.notes) > 0 and self.notes != "None":
            if "skipped" in self.notes.lower():
                print(self.notes, "skipped")
                self.skipped = True
            # if self.notes in [
            #                  'Participant was not getting it so I told him that where the green box is, the formula/answer goes',
            #                  'Did not understand through, thought is was apart of the excel formula',
            #                  'Buggy question. Question misunderstood, said you find the unit price and show it if you have more than five in stock',
            #                  'Participant did not understand', 'Participant did not understand. Before question 15 was fixed.',
            #                  'Gave him a hint for the if statement, if -> then -> else, still did not fully get it. Ended up explaining it.',
            # ]:
            #     self.skipped = True

        return


    def set_raw_data_secondCoder(self, secondCoder_raw_data:dict):
        if len(self.secondCoder_raw_data) > 0:
            return
        self.secondCoder_raw_data = secondCoder_raw_data

        #TODO separat abspeichern:
        self.secondCoder_start = self.parse_time_data(self.secondCoder_raw_data["start (of new slide)"])
        if self.secondCoder_start is None:
            return
        self.secondCoder_understanding = self.parse_time_data(value=self.secondCoder_raw_data["timestamp where participant realizes"])
        if self.secondCoder_understanding is None:
            return

        secondCoder_start_dt = datetime.combine(datetime.today(), self.secondCoder_start)
        secondCoder_understanding_dt = datetime.combine(datetime.today(), self.secondCoder_understanding)
        if secondCoder_understanding_dt < secondCoder_start_dt:# ggf. Datumswechsel berücksichtigen
            secondCoder_understanding_dt += timedelta(hours=1)
        secondCoder_time_diff = secondCoder_understanding_dt - secondCoder_start_dt
        self.secondCoder_time_to_understand = secondCoder_time_diff.total_seconds()

        self.secondCoder_understood_result_cell = secondCoder_raw_data["Result Cell understood (1 / 0)"]
        self.secondCoder_understood_result_type = secondCoder_raw_data["Result Type understood (1.0/0.5/0)"]
        self.secondCoder_understood_operation = secondCoder_raw_data["each operation understood (1 point for each)"]
        self.secondCoder_understood_operand = secondCoder_raw_data["each expected operand understood (1 point for each)"]

        self.secondCoder_total = [
            value if value != "x" and value is not None else 0
            for value in (
                *self.secondCoder_understood_operand.values(),
                *self.secondCoder_understood_operation.values(),
                *self.secondCoder_understood_result_type.values(),
                *self.secondCoder_understood_result_cell.values()
            )
        ]
        self.secondCoder_total = sum(self.secondCoder_total)
        self.secondCoder_degree_of_understanding = self.secondCoder_total / self.task_max_total

        self.secondCoder_notes = self.secondCoder_raw_data["notes"]
        self.secondCoder_skipped = False

        if not self.secondCoder_time_to_understand >= 0:
            self.secondCoder_skipped = True
            print("VERY STRANGE BEHAVIOR", self.p_id, self.task_id, "negative time")
            print("TTU:", self.secondCoder_time_to_understand, "=", self.secondCoder_understanding, "-", self.start)
            self.secondCoder_time_to_understand = None
        if len(self.secondCoder_notes) > 0 and self.secondCoder_notes != "None":
            if "skipped" in self.secondCoder_notes.lower():
                print(self.notes, "skipped")
                self.secondCoder_skipped = True
            # if self.notes in [
            #                  'Participant was not getting it so I told him that where the green box is, the formula/answer goes',
            #                  'Did not understand through, thought is was apart of the excel formula',
            #                  'Buggy question. Question misunderstood, said you find the unit price and show it if you have more than five in stock',
            #                  'Participant did not understand', 'Participant did not understand. Before question 15 was fixed.',
            #                  'Gave him a hint for the if statement, if -> then -> else, still did not fully get it. Ended up explaining it.',
            # ]:
            #     self.skipped = True

        return

