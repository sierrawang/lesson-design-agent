import json
import os
import numpy as np
import random

from tasks.task_helper import get_dropout_tasks
from cip_helpers.dropout_helper import load_true_dropout_distribution, dropout_distribution_js_divergence

def load_results(results_file):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    results_file = os.path.join(current_dir, results_file)
    return json.load(open(results_file))

def get_run_divergence(tasks, results_file, dropout_distribution):
    run_predictions = load_results(results_file)

    divergences = []
    for task in tasks:
        predicted_dropout = run_predictions.get(task['id'], None)
        true_dropout = dropout_distribution[task['id']]
        js_divergence = dropout_distribution_js_divergence(true_dropout, predicted_dropout)
        # print(f'{js_divergence:.3f} ({task["name"]})')

        divergences.append(js_divergence)
    
    average_divergence = np.mean(divergences)

    return average_divergence

def main():
    tasks = get_dropout_tasks()
    dropout_distribution = load_true_dropout_distribution()

    average_divergences = []
    for run_it in range(30):
        # print(f'Run {run_it}')
        average_divergence = get_run_divergence(tasks, f'predictions/run_{run_it}.json', dropout_distribution)
        print(f'Average: {average_divergence:.3f}')
        average_divergences.append(average_divergence)
        # print()

    avg_result = np.mean(average_divergences)
    sem_result = np.std(average_divergences) / np.sqrt(len(average_divergences))
    print(f'Average: {avg_result:.3f} ± {sem_result:.3f}')

# Perform a two-tail bootstrap hypothesis test for the difference in means
def bootstrap(results1, results2, bootstrap_samples=100000):
    # Get the number of students in each group
    N = len(results1)
    M = len(results2)
    
    # Create a universal sample
    universal_sample = results1 + results2
    
    # Count the number of times the difference in means is greater than the observed difference
    count = 0

    # Calculate the observed difference in means
    results1_mean = np.mean(results1)
    results2_mean = np.mean(results2)
    observed_difference = np.mean(results1) - np.mean(results2)
    abs_observed_difference = abs(observed_difference)
    
    # Sample with replacement and calculate the difference in means
    for i in range(bootstrap_samples):
        # Resample the data
        results1_resample = random.choices(universal_sample, k=N) # sample with replacement
        results2_resample = random.choices(universal_sample, k=M) # sample with replacement
        
        # Calculate the mean of the resampled data
        mu_results1 = np.mean(results1_resample)
        mu_results2 = np.mean(results2_resample)
        
        # Calculate the difference in means
        sample_difference = abs(mu_results1 - mu_results2)
        
        # Update the count if the difference in means is greater than the observed difference
        # (which implies that the null hypothesis (no difference) is false)
        if sample_difference > abs_observed_difference:
            count += 1

    pvalue = count / bootstrap_samples

    return results1_mean, results2_mean, pvalue

# Get the p-value between the two methods
def get_pvalue(predictions_folder1, predictions_folder2):
    tasks = get_dropout_tasks()
    dropout_distribution = load_true_dropout_distribution()

    divergences1 = []
    divergences2 = []
    for run_it in range(30):
        average_divergence1 = get_run_divergence(tasks, f'{predictions_folder1}/run_{run_it}.json', dropout_distribution)
        average_divergence2 = get_run_divergence(tasks, f'{predictions_folder2}/run_{run_it}.json', dropout_distribution)

        divergences1.append(average_divergence1)
        divergences2.append(average_divergence2)

    mean1, mean2, p_value = bootstrap(divergences1, divergences2)
    print(f'Mean 1: {mean1:.3f}, Mean 2: {mean2:.3f}, p-value: {p_value:.3f}')
    return p_value

if __name__ == "__main__":
    # main()
    get_pvalue('predictions', '../../predict_dropout/predictions')
    get_pvalue('predictions', 'predictions_no_data')
    get_pvalue('predictions', 'predictions_no_examples')