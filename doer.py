#!/usr/bin/env python
# TODO
# 
# - Swipes integration
# - Clean up table output

from sys import argv
from docopt import docopt
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials
from termcolor import colored
from tabulate import tabulate

usage = '''

A minimalist CLI todo list using a Google Sheets backend.

Usage:
  doer.py list [--group=<group>]
  doer.py add [--color=<shade>] [--group=<group>] <name> [<description>]
  doer.py remove <task>
  doer.py count [--group=<group>]
  doer.py move <task> <target>
  doer.py edit [--color=<shade>] [--group=<group>] [--rename=<name>] [--description=<description>] <target>
'''

argx = docopt(usage)

# Access Google Sheets database for doer
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open('tasks').sheet1

# Output all current tasks and metadata
def listf(group):
    tasks_list = sheet.get_all_values()

    row = 1
    for task in tasks_list:
        task.append(row)
        row += 1

    if tasks_list[0][0] == 'No tasks found.':
        return 'No tasks found.'
    else:
        if group != None:
            tasks_list = list(filter(lambda x: x[4] == group, tasks_list))
        table = []
        for i in tasks_list:
           print(i)
           if len(i) <= 3:
               table.append(str(i[-1])  + '   ' + i[0] + '   ' + i[1] \
                   + ((' - ' + i[2]) if (i[2] != '') else '') \
                   + '   (' + str(i[4]) + ')')
           else:
               table.append(colored((str(i[-1])  + '   ' + i[0] + '   ' \
                   + i[1] + ((' - ' + i[2]) if (i[2] != '') else '')) \
                   + '   (' + str(i[4]) + ')', i[3]))
        return '\n'.join(table)

# Append new task to the database
def add(task, description, color, group):
    today = date.today().strftime('%m-%d-%Y')
    row_values = list(map(lambda y: '' if y == None else y, [today, task, description, color, group]))
    if sheet.cell(1, 1).value == 'No tasks found.':
        sheet.append_row(row_values)
        sheet.delete_row(1)
    else:
        sheet.append_row(row_values)

# Delete a task from the database by priority
def remove(task):
    if sheet.row_count == 1:
        sheet.append_row(['No tasks found.', '', '', ''])
        sheet.delete_row(1)
    else:
        sheet.delete_row(int(task))

# Display current number of tasks in the database
def count(group):
    tasks_list = sheet.get_all_values()
    if group != None:
            tasks_list = list(filter(lambda x: x[4] == group, tasks_list))
    return len(tasks_list)

def edit(target, name, description, color, group):
    updated_task = [name, description, color, group]
    column = 2
    for i in updated_task:
        if i != None:
            sheet.update_cell(target, column, i)
        column += 1

# Move a task from one priority number to another in the database
def move(task, rank):
    task, rank = int(task), int(rank)
    contents = sheet.row_values(task)
    sheet.delete_row(task)
    # Workaround for bug that prevents insert_row from working on two-row sheets
    if sheet.row_count == 2:
        sheet.append_row(contents)
    else:
        sheet.insert_row(contents, index=rank)

# Run the main body of the program
if __name__ == '__main__':
    args = argv[1:]
    command = args[0]
    if argx['list']:
        print(listf(argx['--group']))
    elif argx['add']:
        add(argx['<name>'], argx['<description>'], argx['--color'], argx['--group'])
        print(listf(None))
    elif argx['remove']:
        remove(argx['<task>'])
        print(listf(None))
    elif argx['count']:
        print(count(argx['--group']))
    elif argx['move']:
        move(argx['<task>'], argx['<target>'])
        print(listf(None))
    elif argx['edit']:
         edit(argx['<target>'], argx['--rename'], argx['--description'], argx['--color'], argx['--group'])
         print(listf(None))
    else:
        print('Command not recognized.')