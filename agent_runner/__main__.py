from concurrent.futures import ThreadPoolExecutor, as_completed
from agent_runner.initializer import initialize_task
from agent_runner.execution import execute_lesson_many_times
from agent_runner.task_loader import load_accounts_q, parse_args
from tasks.task_helper import get_all_tasks

# Run an agent on the given lesson
def do_lesson(lesson, args, accounts_q, output_folder, num_runs, site_url='https://codeinplace.stanford.edu'):
    # Initialize the task (get the task driver, logger, output directory, and cip account info)
    task_driver, logger, output_dir, account_info = initialize_task(lesson['id'], args, accounts_q, output_folder, site_url)

    # Execute the task num_runs times!
    execute_lesson_many_times(task_driver, logger, output_dir, lesson, args, site_url, num_runs)

    # Close the task driver
    task_driver.close()

    # Put the account back in the queue
    accounts_q.put(account_info)

def do_all_lessons():
    # Parse the command line arguments
    args = parse_args()

    # Load the tasks
    all_tasks = get_all_tasks()
    lesson_tasks = [task for task in all_tasks if task['type'] == 'lesson' and task['id'] != 'using-libraries']

    # Load the account credentials
    accounts_q = load_accounts_q()

    # Run each task on its own thread. 
    # The threads will block until there is an account available to use.
    with ThreadPoolExecutor(max_workers=args.max_threads) as executor:
        futures = []
        for lesson in lesson_tasks:
            futures.append(executor.submit(do_lesson, lesson, args, accounts_q, 'agents', 15))

        for future in as_completed(futures):
            future.result()

def do_injection():
    # Parse the command line arguments
    args = parse_args()

    # Load the account credentials
    accounts_q = load_accounts_q()

    lesson = {
        "name": "Art of Problem Solving",
        "id": "decomposition",
        "type": "lesson",
        'max_iter': 50
    }

    output_folder = 'injection'
    num_runs = 1
    site_url = 'http://localhost:3000'

    do_lesson(lesson, args, accounts_q, output_folder, num_runs, site_url)

if __name__ == "__main__":
    do_all_lessons()
    # do_injection()