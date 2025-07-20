import json
import os
import numpy as np

import sys
sys.path.insert(1, '../../../tasks')
from task_helper import get_completion_tasks

sys.path.insert(1, '../../../evaluation')
from completion_helper import load_true_completion_df, get_engaged_task_completion_rate
from rmse_helper import get_rmse

def load_results(results_file):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    results_file = os.path.join(current_dir, results_file)
    return json.load(open(results_file))

def get_run_rmse(tasks, results_file, true_completion_df):
    run_predictions = load_results(results_file)

    predictions = []
    actuals = []
    # print('Truth, Pred. (Task Name)')
    for task in tasks:
        predicted_completion_rate = run_predictions.get(task['id'], None)
        predictions.append(predicted_completion_rate)
        task_completion_rate, sem = get_engaged_task_completion_rate(task['id'], true_completion_df)
        actuals.append(task_completion_rate)

        # print(f'{task_completion_rate:.3f}, {predicted_completion_rate:.3f} ({task["name"]})')
    
    rmse = get_rmse(predictions, actuals)

    return rmse

def main():
    tasks = get_completion_tasks()
    true_completion_df = load_true_completion_df()

    rmses = []
    for run_it in range(10):
        # print(f'Run {run_it}')
        rmse = get_run_rmse(tasks, f'predictions/run_{run_it}.json', true_completion_df)
        print(f'RMSE: {rmse:.3f}')
        rmses.append(rmse)
        
    avg_rmse = np.mean(rmses)
    sem_rmse = np.std(rmses) / np.sqrt(len(rmses))

    print(f'Average RMSE: {avg_rmse:.3f} ± {sem_rmse:.3f}')

if __name__ == "__main__":
    main()