from enum import Enum

from StudyElements.STRUCTURALTASKASPECT import STRUCTURALTASKASPECT


class RESULTTYPE(Enum):
    VALUE = "Single value"
    LIST = "List of Items"

class Task(object):

    def __init__(self, number:int, max_total:int,
                 description:str=None, formula:str=None,
                 expected_result_cell:str=None, expected_operations:list[str]=None, expected_operands:list[str]=None,
                 result_type:RESULTTYPE=None):
        self.task_number = number
        self.task_description = description
        self.task_formula = formula
        self.task_expected_result_cell = expected_result_cell
        self.task_expected_operations = expected_operations
        self.task_expected_operands = expected_operands
        self.task_result_type = result_type
        self.structural_aspects = []
        assert max_total >= 0
        self.task_max_total = max_total



    def get_excel_line(self):
        return 2 + int(self.task_number)

    def add_structural_aspects(self, structural_aspects:list[STRUCTURALTASKASPECT]):
        self.structural_aspects = structural_aspects

    def get_operation_type(self):
        collected_information = []
        for i in self.structural_aspects:
            if i in [STRUCTURALTASKASPECT.COMP, STRUCTURALTASKASPECT.iCOMP,
                     STRUCTURALTASKASPECT.COND, STRUCTURALTASKASPECT.iCOND,
                     STRUCTURALTASKASPECT.LOOK, STRUCTURALTASKASPECT.iLOOK]:
                collected_information.append(i)
        return collected_information

    def get_operand_type(self):
        collected_information = []
        for i in self.structural_aspects:
            if i in [STRUCTURALTASKASPECT.CELL, STRUCTURALTASKASPECT.iCELL,
                     STRUCTURALTASKASPECT.RANGE, STRUCTURALTASKASPECT.iRANGE,
                     STRUCTURALTASKASPECT.LIT, STRUCTURALTASKASPECT.iLIT,
                     STRUCTURALTASKASPECT.FUNC, STRUCTURALTASKASPECT.iFUNC]:
                collected_information.append(i)
        return collected_information

    def get_result_type(self):
        collected_information = []
        for i in self.structural_aspects:
            if i in [STRUCTURALTASKASPECT.VAL, STRUCTURALTASKASPECT.iVAL,
                     STRUCTURALTASKASPECT.BATCH, STRUCTURALTASKASPECT.iBATCH,
                     STRUCTURALTASKASPECT.LIST, STRUCTURALTASKASPECT.iLIST]:
                collected_information.append(i)
        return collected_information

    def get_reference_direction(self):
        collected_information = []
        for i in self.structural_aspects:
            if i in [STRUCTURALTASKASPECT.BACK, STRUCTURALTASKASPECT.iBACK,
                     STRUCTURALTASKASPECT.FORWARD, STRUCTURALTASKASPECT.iFORWARD]:
                collected_information.append(i)
        return collected_information

    def get_reference_dispersion(self):
        collected_information = []
        for i in self.structural_aspects:
            if i in [STRUCTURALTASKASPECT.ON, STRUCTURALTASKASPECT.iON,
                     STRUCTURALTASKASPECT.OFF, STRUCTURALTASKASPECT.iOFF,
                     STRUCTURALTASKASPECT.CROSS, STRUCTURALTASKASPECT.iCROSS]:
                collected_information.append(i)
        return collected_information




