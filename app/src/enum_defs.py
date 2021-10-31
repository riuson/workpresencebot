#!/usr/bin/env python

# Enums: https://antonz.ru/enum/
from enum import Enum


class RecordType(Enum):
    CameToWork = 1
    LeftWork = 2
    StayedAtHome = 3
