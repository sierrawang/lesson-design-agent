from prompt_helper import get_system_prompt
from gpt_helper import get_prediction
import json
import os
from tasks.task_helper import get_dropout_tasks, get_example_lesson_tasks
from cip_helpers.completion_helper import load_true_completion_df
from cip_helpers.dropout_helper import load_true_dropout_distribution

# Get the predicted dropout distribution for a specific run of a task
# This will be in the form of a dictionary with the slide names as keys and the dropout rates as values
def predict_dropout_for_run(run_it, current_task, lesson_tasks, true_dropout_distribution, true_completion_df):
    # Get the system prompt based on the agent results
    # system_prompt = get_system_prompt(current_task, run_it, lesson_tasks, true_dropout_distribution, true_completion_df, include_data=False)
    system_prompt = get_system_prompt(current_task, run_it, lesson_tasks, true_dropout_distribution, true_completion_df, include_examples=False)
    # print(system_prompt)

    # Call the GPT to predict the completion rate
    prediction = get_prediction(system_prompt, 5)
    print(f'{current_task["id"]}: {prediction}')

    return prediction

def predict_dropout_for_runs(run_it, eval_tasks, lesson_tasks, true_dropout_distribution, true_completion_df, output_folder):
    # Predict the dropout distribution for each task in this run
    results = {}
    for current_task in eval_tasks:
        task_id = current_task['id']
        results[task_id] = predict_dropout_for_run(run_it, current_task, lesson_tasks, true_dropout_distribution, true_completion_df)

    # Save the results to a file
    output_filename = f'{output_folder}/run_{run_it}.json'
    with open(output_filename, 'w') as output_file:
        json.dump(results, output_file)

    print(f'Saved results to {output_filename}')

def run_predict_dropout(output_folder='./predictions'):
    # Load the tasks and true task completion
    eval_tasks = get_dropout_tasks()

    # Use the lesson tasks (except for using-libraries) as the training data
    example_lesson_tasks = get_example_lesson_tasks()

    # Load the true completion and dropout distribution
    true_completion_df = load_true_completion_df()
    true_dropout_distribution = load_true_dropout_distribution()

    # Get the dropout distribution predictions for each run and save them to a file
    for run_it in range(15):
        print(f'Getting predictions for run {run_it}...')
        # Predict the dropout distribution for each task in this run
        predict_dropout_for_runs(run_it, eval_tasks, example_lesson_tasks, true_dropout_distribution, true_completion_df, output_folder)

# Check for missing predictions (likely due to formatting errors) 
# and re-run
def check_for_missing(output_folder='./predictions'):
    # Load the tasks and true task completion
    eval_tasks = get_dropout_tasks()

    # Use the lesson tasks (except for using-libraries) as the training data
    example_lesson_tasks = get_example_lesson_tasks()

    # Load the true completion and dropout distribution
    true_completion_df = load_true_completion_df()
    true_dropout_distribution = load_true_dropout_distribution()

    # Loop over every run
    for run_it in range(30):
        # Load the results
        results_file = f'{output_folder}/run_{run_it}.json'
        results = json.load(open(results_file))

        # Loop over every task and check if the prediction is missing
        missing = []
        for current_task in eval_tasks:
            task_id = current_task['id']
            if len(results[task_id].items()) == 0:
                missing.append(current_task)

        print(f'Run {run_it}: missing {missing}')

        # Predict the dropout distribution for each missing task
        for current_task in missing:
            task_id = current_task['id']
            results[task_id] = predict_dropout_for_run(run_it, current_task, example_lesson_tasks, true_dropout_distribution, true_completion_df)

        # Overwrite the old output file
        with open(results_file, 'w') as output_file:
            json.dump(results, output_file)

# Check for predictions that don't sum to 1 and re-run
# This is likely due to a formatting error
def check_for_bugs(output_folder='./predictions'):
    # Load the tasks and true task completion
    eval_tasks = get_dropout_tasks()

    # Use the lesson tasks (except for using-libraries) as the training data
    example_lesson_tasks = get_example_lesson_tasks()

    # Load the true completion and dropout distribution
    true_completion_df = load_true_completion_df()
    true_dropout_distribution = load_true_dropout_distribution()

    # Loop over every run
    for run_it in range(30):
        # Load the results
        results_file = f'{output_folder}/run_{run_it}.json'
        results = json.load(open(results_file))

        # Loop over every task and check if the prediction is missing
        buggy = []
        for current_task in eval_tasks:
            task_id = current_task['id']
            
            # Check if the sum of the predictions is not 1
            prediction = results[task_id]
            dist_sum = sum(prediction.values())
            rounded_sum = round(dist_sum, 10)
            # print(rounded_sum)
            if rounded_sum != 1:
                # print(f'{task_id}: sum={rounded_sum}')
                buggy.append(current_task)

        print(f'Run {run_it}: buggy {buggy}')

        # # Predict the dropout distribution for each missing task
        # for current_task in buggy:
        #     task_id = current_task['id']
        #     results[task_id] = predict_dropout_for_run(run_it, current_task, example_lesson_tasks, true_dropout_distribution, true_completion_df)

        # # Overwrite the old output file
        # with open(results_file, 'w') as output_file:
        #     json.dump(results, output_file)

if __name__ == '__main__':
    run_predict_dropout('./predictions_ablations')
    # check_for_missing('./predictions_no_examples')
    # check_for_bugs('./predictions_no_examples')