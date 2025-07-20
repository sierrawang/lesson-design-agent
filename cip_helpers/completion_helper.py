import os
import pandas as pd

# Return the true completion dataframe for all tasks
def load_true_completion_df():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    true_completion_filename = os.path.join(current_dir, '../cip_data/true_completion.csv')
    true_completion_df = pd.read_csv(true_completion_filename)
    return true_completion_df

def student_completed_task(student_id, task_id, true_completion_df):
    student_results = true_completion_df.loc[true_completion_df['student_id'] == student_id]
    student_task_result = student_results[task_id].values[0]
    return student_task_result == 'Completed'

def get_num_complete(task_id, true_completion_df):
    task_results = true_completion_df[task_id]
    return task_results.str.count('Completed').sum()

def get_num_incomplete(task_id, true_completion_df):
    task_results = true_completion_df[task_id]
    return task_results.str.count('Incomplete').sum()

def get_num_not_started(task_id, true_completion_df):
    task_results = true_completion_df[task_id]
    return task_results.str.count('Not started').sum()

# Return the completion rate for the task, of the students who started the task
def get_task_completion_distribution(task_id, true_completion_df=None):
    # Load the true completion df
    if true_completion_df is None:
        true_completion_df = load_true_completion_df()

    # Get the completion distribution for this task
    task_results = true_completion_df[task_id]

    # Return the completion dist
    total_students = len(task_results)
    task_completion_dist = {
        'Completed': get_num_complete(task_id, true_completion_df)/total_students,
        'Incomplete': get_num_incomplete(task_id, true_completion_df)/total_students,
        'Not started': get_num_not_started(task_id, true_completion_df)/total_students
    }

    return task_completion_dist

# Return the percentage of students who completed the task
def get_true_task_completion_rate(task_id, true_completion_df=None):
    # Load the true completion df
    if true_completion_df is None:
        true_completion_df = load_true_completion_df()

    # Get the completion distribution for this task
    task_results = true_completion_df[task_id]

    # Count the number of 'Completed'
    num_completed = get_num_complete(task_id, true_completion_df)
    total_students = len(task_results)

    return num_completed/total_students

# Return the completion rate for the task, of the students who started the task
def get_engaged_task_completion_rate(task_id, true_completion_df=None):
    # Load the true completion df
    if true_completion_df is None:
        true_completion_df = load_true_completion_df()

    # Count the number of 'Completed'
    num_completed = get_num_complete(task_id, true_completion_df)
    num_started = num_completed + get_num_incomplete(task_id, true_completion_df)

    # Calculate the completion rate and standard error of the mean
    completion_rate = num_completed/num_started
    sem = (completion_rate*(1-completion_rate)/num_started)**0.5

    return completion_rate, sem
