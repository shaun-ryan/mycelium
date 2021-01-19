from enum import Enum

class DependencyOperator(Enum):
    AND = 1
    OR = 2

class DependencyCondition(Enum):
    SUCCESS = 1
    FAILURE = 2
    COMPLETION = 3