'''
Business constants: goals, thresholds and domain-specific rules.
Extracted from config.py so that domain/ does not depend on infrastructure/.
'''

GOALS = {
    "daily" : 7.5,
    "weekly" : 37.5,
    "monthly" : 150
}

DEPARTMENT = "7000 - INFORMATION TECHNOLOGY"

HOURS_PER_DAY_THRESHOLD = 6.75
PASSIVE_HOURS_THRESHOLD = 1.25