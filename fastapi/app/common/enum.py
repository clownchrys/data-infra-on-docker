from enum import Enum


class ApiEnvEnum(str, Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    STG = "STG"
    PRD = "PRD"
