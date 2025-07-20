from prompt_helper import get_system_prompt
from gpt_helper import get_prediction
import json

import sys
sys.path.insert(1, '../../../tasks')
from task_helper import get_all_tasks, get_completion_tasks

sys.path.insert(1, '../../../evaluation')
from completion_helper import load_true_completion_df
from dropout_helper import load_true_dropout_distribution

# Get the predicted dropout distribution for a specific run of a task
# This will be in the form of a dictionary with the slide names as keys and the dropout rates as values
def predict_completion_for_run(run_it, current_task, lesson_tasks, true_dropout_distribution, true_completion_df):
    # Get the system prompt based on the agent results
    system_prompt = get_system_prompt(current_task, run_it, lesson_tasks, true_dropout_distribution, true_completion_df)
    # print(system_prompt)

    # Call the GPT to predict the completion rate
    prediction = get_prediction(system_prompt, 5)
    print(f'{current_task["id"]}: {prediction}')

    return prediction

def predict_completion_for_runs(run_it, eval_tasks, lesson_tasks, true_dropout_distribution, true_completion_df, output_folder='./predictions'):
    # Predict the dropout distribution for each task in this run
    results = {}
    for current_task in eval_tasks:
        task_id = current_task['id']
        results[task_id] = predict_completion_for_run(run_it, current_task, lesson_tasks, true_dropout_distribution, true_completion_df)

    # Save the results to a file
    output_filename = f'{output_folder}/run_{run_it}.json'
    with open(output_filename, 'w') as output_file:
        json.dump(results, output_file)

    print(f'Saved results to {output_filename}')

if __name__ == '__main__':
    # Load the tasks and true task completion
    eval_tasks = get_completion_tasks()

    # Use the lesson tasks (except for using-libraries) as the training data
    all_tasks = get_all_tasks()
    lesson_tasks = [task for task in all_tasks if task['type'] == 'lesson' and task['id'] != 'using-libraries']

    # Load the true completion and dropout distribution
    true_completion_df = load_true_completion_df()
    true_dropout_distribution = load_true_dropout_distribution()

    # Get the dropout distribution predictions for each run and save them to a file
    for run_it in range(30):
        print(f'Getting predictions for run {run_it}...')
        # Predict the dropout distribution for each task in this run
        predict_completion_for_runs(run_it, eval_tasks, lesson_tasks, true_dropout_distribution, true_completion_df)