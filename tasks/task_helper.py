import os
import json

from cip_helpers.lessons_helper import get_slides_for_lesson

def load_task_file_helper(filename):
    # Get the absolute path of the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the full path to the JSON file
    file_path = os.path.join(script_dir, filename)
    
    # Open and load the JSON file
    tasks = json.load(open(file_path, 'r'))
    return tasks

# Return a list of all tasks in Code in Place 4
def get_all_tasks():
    return load_task_file_helper('all_tasks.json')

# Return all tasks that are lessons and have more than 2 slides
def get_example_lesson_tasks():
    all_tasks = get_all_tasks()
    example_lesson_tasks = []
    for task in all_tasks:
        if task['type'] != 'lesson':
            continue
        
        lesson_slides = get_slides_for_lesson(task['id'])
        if len(lesson_slides) > 2:
            example_lesson_tasks.append(task)

    return example_lesson_tasks

# Return a list of the tasks we are using to evaluate simulating completion rates
def get_completion_tasks():
    return load_task_file_helper('completion_tasks.json')

# Return a list of the tasks we are using to evaluate simulating dropout rates
def get_dropout_tasks():
    return load_task_file_helper('dropout_tasks.json')

# Return the metadata for the given task
def get_task_metadata(task_id):
    tasks = get_all_tasks()

    # Get the task metadata
    for task_data in tasks:
        if task_data['id'] == task_id:
            return task_data
    return None

# Return the index of the task in the list of tasks
def get_task_index(task, task_list):
    for i in range(len(task_list)):
        if task_list[i]['id'] == task['id']:
            return i
    return -1

# Return whether the two tasks have the same flags
def same_flags(task1, task2):
    task1_flags = task1.get('flags', [])
    task2_flags = task2.get('flags', [])

    # Check that the flags are the same length
    if len(task1_flags) != len(task2_flags):
        return False
    else:
        # Check that each flag in task1 exists in task2
        for flag in task1_flags:
            if flag not in task2_flags:
                return False
        return True
    
# Return the task that most closely precedes the given task in the list of tasks,
# based on the task's position in the list.
# If match_type is True, only return a task of the same type as the given task.
# If match_flags is True, only return a task with the same flags as the given task.
def get_baseline_task(task, all_tasks, match_type=False, match_flags=False):
    task_index = get_task_index(task, all_tasks)

    # Find the most recent task that is not the same task
    for i in range(task_index - 1, -1, -1):
        current_task = all_tasks[i]
        # Filter by type if necessary
        if not match_type or current_task['type'] == task['type']:
            # Filter by flags if necessary
            if not match_flags or same_flags(current_task, task):
                return current_task

    return None