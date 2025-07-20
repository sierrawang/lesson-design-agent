import json
import os
import queue
import argparse

# Load the tasks from a file and return the list of tasks
def load_tasks(task_file):
    # Identify the correct file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    task_filename = os.path.join(current_dir, task_file)

    # Load the tasks from the file
    tasks = []
    with open(task_filename, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    print(f'Loaded {len(tasks)} tasks')

    return tasks

def load_accounts_q():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, 'credentials/cip_agent_credentials.json')
    accounts = json.load(open(filename, 'r'))
    accounts_q = queue.Queue()
    for account in accounts:
        accounts_q.put(account)
    return accounts_q

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_agents', type=int, default=5)
    parser.add_argument('--max_threads', type=int, default=10)
    parser.add_argument('--task_file', type=str, default="tasks/dropout_tasks.json")
    parser.add_argument("--api_model", default="gpt-4o", type=str, help="api model name")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--max_attached_imgs", type=int, default=3)
    parser.add_argument("--headless", type=bool, default=True)
    parser.add_argument("--save_accessibility_tree", action='store_true')
    parser.add_argument("--force_device_scale", action='store_true')
    parser.add_argument("--window_width", type=int, default=1024)
    parser.add_argument("--window_height", type=int, default=768)
    parser.add_argument("--listen_audio", type=bool, default=False)
    args = parser.parse_args()
    return args