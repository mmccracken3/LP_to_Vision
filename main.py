'''
2025-02-12 .01
'''

import sys
import csv
import tkinter as tk
from tkinter import filedialog
import re
from datetime import datetime
import os


PHASE_TASK_REGEX = re.compile(r'^(\S+)\s-\s(\S+)\s-\s(\S+)')
PROJECT_BG_NUMBER_REGEX = re.compile(r'(\d\S+)\.(\S+)')
PROJECT_NUMBER_REGEX = re.compile(r'(\d\S+)')
MISC_BG_REGEX = re.compile(r'Miscellaneous.+>.+(\.\S+)')
EMPLOYEE_NAME_REGEX = re.compile(r'(\S+$)')
SPECIAL_PROJ_REGEX = re.compile(r'(General Business - Non-Billable Tasks > )([^>]+)(\s>.+)?')

SPECIAL_PROJECT_NUMS_PROJECTS = {'OVH - Overhead': {'Project Number': 'OVH',
                                                    'Phase': '15',
                                                    'Task': 'GB'},
                                 'BDV - Business Development': {'Project Number': 'BDV',
                                                                'Phase': '04',
                                                                'Task': 'BD'}
                                 }

SPECIAL_PROJECT_NUMS_TASKS = {
    'HOL - Holiday': 'HOL',
    'PERS - Personal': 'PERS',
    'PD - Professional Development': {'Project Number': 'PD',
                                      'Phase': '04',
                                      'Task': 'MTG'},
    'VAC - Vacation': 'VAC',
    'BRV - Bereavement': 'BEREAVEMENT',
    'SICK - Sick Leave': 'SICK',
    'OFC - Office Closed': 'OFFICE CLOSED'
}

SPECIAL_BG_LIST = {'109': ('09', 'E'),
                   '103': ('01', 'E'),
                   '106': ('01', 'E'),
                   '107': ('01', 'WA'),
                   '108': ('01', 'E')
                   }

PHASE_TASK_CONVERSION = {('00', 'BD'): ('04', 'BD'),
                         ('00', 'PP'): ('04', 'COR'),
                         ('01', 'FA'): ('04', 'COR'),
                         ('01', 'RPT'): ('01', 'E'),
                         ('02', 'AEM'): ('04', 'E'),
                         ('02', 'EPD'): ('04', 'EPD'),
                         ('02', 'OA'): ('04', 'OA'),
                         ('02', 'PMT'): ('04', 'EPD'),
                         ('02', 'PR'): ('04', 'PR'),
                         ('04', 'CD'): ('04', 'CD'),
                         ('04', 'COR'): ('04', 'COR'),
                         ('04', 'DE'): ('04', 'DE'),
                         ('04', 'M'): ('04', 'M'),
                         ('04', 'PS'): ('04', 'PS'),
                         ('04', 'SP'): ('04', 'SP'),
                         ('04', 'SV'): ('04', 'SV'),
                         ('04', 'TT'): ('04', 'TT'),
                         ('04', 'SUR'): ('04', 'LS'),
                         ('06', 'BID'): ('06', 'BO'),
                         ('07', 'CA'): ('07', 'PE'),
                         ('07', 'SD'): ('07', 'SD'),
                         ('08', 'IA'): ('08', 'IA'),
                         ('08', 'I'): ('08', 'I'),
                         ('08', 'ITT'): ('08', 'TT'),
                         ('15', 'OVH'): ('04', 'COR')
                         }

EMPLOYEE_NUMBER = {'ASHWORTH': 'ASHWORTH',
                   'CRABTREE': 'CRABTREE',
                   'HOLLIE': 'HOLLIE',
                   'JOHNSTON': 'JOHNSTON',
                   'KOTRONIS': 'KOTRONIS',
                   'LEONARD': 'LEONARD',
                   'MCCRACKEN': 'MCCRACKEN',
                   'MCCUNE': 'MCCUNE',
                   'ROGERS': 'ROGERS',
                   'GREEN': 'GREEN',
                   'LANGSTON': 'LANGSTON',
                   'MCCLELLAN': 'MCCLELLAN',
                   'OUZTS': 'OUZTS',
                   'SELF': 'SELF',
                   'TYRE': 'TYRE',
                   'VIGNERI': 'VIGNERI',
                   'RIVERS': 'RIVERS',
                   'KOVALCHIK': 'KOVALCHIK',
                   'ALICIA': 'ADDENBROOK',
                   'KATEMCGOWAN': 'MCGOWAN',
                   'AMANDACASE': 'CASE',
                   'JILLFRITZ': 'FRITZ J',
                   'ALLAWSON': 'LAWSON A',
                   'ROBERTMOODY': 'MOODY R',
                   'DENNISMARTIN': 'MARTIN D',
                   'ELLESAJORDAN': 'JORDAN',
                   'JACOBCAYLOR': 'CAYLOR',
                   'KATHLEENJONES': 'JONES K',
                   'STEPHANIEJONES': 'JONES S',
                   'JANLOVE': 'LOVE',
                   'CINDYMAYSON': 'MAYSON',
                   'BILLMILLER': 'MILLER',
                   'TUCKERPRESSLEY': 'PRESSLEY',
                   'RYANFIERRO': 'FIERRO',
                   'BRANDONSMITH': 'SMITH B',
                   'SEABORNSTREET': 'STREET',
                   'KATHYROSS': 'ROSS',
                   'WILLIAMSPRINGER': 'SPRINGER',
                   'LAURENLEWALLEN': 'LEWALLEN',
                   'WESFRITZ': 'FRITZ',
                   'MATTHENDERSON': 'HENDERSONM',
                   'KENADAMS': 'ADAMS K',
                   'DANIELHOFMEIER': 'HOFMEIER',
                   'SARAHGREER': 'GREER',
                   'ALLISONWRIGHT': 'WRIGHT',
                   'HEATHLEE': 'LEE',
                   'JEFFKELLEY': 'KELLEY',
                   'GILBERTELLIS': 'ELLIS G'
                   }


class VisionRow:
    def __init__(self, employee_name, project_number, phase, task, date, hours, comment):
        self.employee_name = employee_name
        self.project_number = project_number
        self.phase = phase
        self.task = task
        self.date = date
        self.hours = hours
        self.comment = comment


def select_file():
    root = tk.Tk()
    root.withdraw()

    filename = filedialog.askopenfilename()

    return filename


def phase_task_parse(activity):
    phase_task_match = PHASE_TASK_REGEX.search(activity)
    phase = phase_task_match.group(1)
    task = phase_task_match.group(2)
    if (phase, task) in PHASE_TASK_CONVERSION:
        phase, task = PHASE_TASK_CONVERSION[(phase, task)]
    return phase, task

def read_file_contents(filename):
    info = []
    with open(filename) as file:
        reader = csv.DictReader(file)
        for row in reader:

            # If time is less than 0.25, then skip
            if float(row['hours']) < 0.25:
                continue

            # Name
            name_match = EMPLOYEE_NAME_REGEX.search(row['full_name'])
            try:
                name = EMPLOYEE_NUMBER[name_match.group(1).upper()]

            except KeyError:
                print(f'ERROR: Name not recognized: {name_match.group(1)}')
                input('Press Enter to exit...')
                sys.exit()


            # Project Number

            # Check if the project number is a special case
            project_number_match = None
            billing_group_match = None

            # Special Case - Project
            special_project_match = SPECIAL_PROJ_REGEX.search(row['folder'])
            if special_project_match is not None:
                special_project_match = special_project_match.group(2)
                if special_project_match in SPECIAL_PROJECT_NUMS_PROJECTS:
                    project_number = SPECIAL_PROJECT_NUMS_PROJECTS[special_project_match]['Project Number']
                    phase = SPECIAL_PROJECT_NUMS_PROJECTS[special_project_match]['Phase']
                    task = SPECIAL_PROJECT_NUMS_PROJECTS[special_project_match]['Task']


            # Special Case - Task

            elif row['task'] in SPECIAL_PROJECT_NUMS_TASKS:
                if isinstance(SPECIAL_PROJECT_NUMS_TASKS[row['task']], dict):
                    project_number = SPECIAL_PROJECT_NUMS_TASKS[row['task']]['Project Number']
                    phase = SPECIAL_PROJECT_NUMS_TASKS[row['task']]['Phase']
                    task = SPECIAL_PROJECT_NUMS_TASKS[row['task']]['Task']
                else:
                    project_number = SPECIAL_PROJECT_NUMS_TASKS[row['task']]
                    phase = ''
                    task = ''
            elif '- inspection' == row['task'][-12:].lower():
                project_number_match = PROJECT_NUMBER_REGEX.search(row['task'])
                project_number = project_number_match.group(1)
                phase, task = phase_task_parse(row['activity'])
            else:
                project_number_match = PROJECT_BG_NUMBER_REGEX.search(row['project'])
                # Check if miscellaneous in the title and look for billing group
                if 'miscellaneous' in row['project'].lower():
                    billing_group_match = MISC_BG_REGEX.search(row['folder'])
                    if billing_group_match is None:
                        project_number = row['project']
                    else:
                        project_number_match = PROJECT_NUMBER_REGEX.search(row['project'])
                        project_number = f'{project_number_match.group(1)}{billing_group_match.group(1)}'
                # No project number can be found
                elif project_number_match is None:
                    project_number = row['project']
                # Project number found
                else:
                    project_number = f'{project_number_match.group(1)}.{project_number_match.group(2)}'

                # Phase and Task
                phase, task = phase_task_parse(row['activity'])

            # Comment
            if row['timesheet_entry_note'] == '':
                comment = row['task']
            else:
                comment = f'{row['task']} - {row['timesheet_entry_note']}'

            # If .003 BG then FA stays FA
            project_number_match = PROJECT_BG_NUMBER_REGEX.search(project_number)
            if project_number_match is not None and project_number_match.group(2) == '003' and \
                    PHASE_TASK_REGEX.search(row['activity']).group(2) == 'FA':
                task = 'FA'
            elif project_number_match is not None and project_number_match.group(2) in SPECIAL_BG_LIST:
               phase, task = SPECIAL_BG_LIST[project_number_match.group(2)]

            # Date


            info.append(VisionRow(
                name,
                project_number,
                phase,
                task,
                row['ï»¿date'].replace('-', '/'),
                row['hours'],
                comment
                ))

    return info


def create_file(data: list):
    dt = datetime.now()

    program_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(program_dir,
                               f'LP to Vision {dt.year}-{dt.month}-{dt.day} {dt.hour}_{dt.minute}_{dt.second}.csv')
    with open(output_path, 'w', newline='') as output:
        writer = csv.DictWriter(output, ['name',
                                         'project_number',
                                         'phase',
                                         'task',
                                         'date',
                                         'hours',
                                         'comment'
                                         ])
        for row in data:
            writer.writerow({'name': row.employee_name,
                             'project_number': row.project_number,
                             'phase': row.phase,
                             'task': row.task,
                             'date': row.date,
                             'hours': row.hours,
                             'comment': row.comment})


def main():
    filename = select_file()
    csv_data = read_file_contents(filename)
    create_file(csv_data)


if __name__ == '__main__':
    main()

