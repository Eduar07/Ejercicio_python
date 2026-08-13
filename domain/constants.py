'''
Constantes de negocio: metas, umbrales y reglas propias del dominio.
Extraídas de config.py para que domain/ no dependa de infrastructure/.
'''

GOALS = {
    "daily" : 7.5,
    "weekly" : 37.5,
    "monthly" : 150
}

DEPARTMENT = "7000 - INFORMATION TECHNOLOGY"

HOURS_PER_DAY_THRESHOLD = 6.75
PASSIVE_HOURS_THRESHOLD = 1.25