from pathlib import Path
import openpyxl
from openpyxl import Workbook
from infrastructure.config import OUTPUT_SHEET_NAME
from domain.models import EmployeeMetric



def create_workbook():

   workbook = Workbook()

   worksheet = workbook.active

   worksheet.title = OUTPUT_SHEET_NAME
   
   return workbook, worksheet