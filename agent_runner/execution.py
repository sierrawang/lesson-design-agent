import os
import time

from agent_runner.prompt_helper import init_lesson_prompt
from agent_runner.observation_helper import remove_rects, get_updated_messages
from agent_runner.thought_action_helper import call_gpt4_api, extract_action_from_gpt4v_response
from agent_runner.action_controller import action_controller
from agent_runner.system_prompt import INSTRUCTIONS
from agent_runner.openai_helper import get_openai_client
from agent_runner.print_message_helper import print_message, print_messages

def is_home_page(driver, site_url):
    return driver.current_url == f"{site_url}/cip4/studenthome"

# Execute a single iteration of the task
# Return -1 if the task failed, 0 if the task is not complete, and 1 if the task is complete
def execute_task_iteration(
        it, args, agent_driver, task_dir, init_msg, messages, client, 
        fail_obs, pdf_obs, warn_obs, logger, site_url='https://codeinplace.stanford.edu'):
    logger.info(f'Task Iteration: {it}')

    # Get an updated messages array containing a new observation
    messages, rects, web_eles = get_updated_messages(
        messages, fail_obs, pdf_obs, warn_obs, it, args, agent_driver, task_dir, init_msg, client, logger) # prev_agent_str
    if messages is None:
        # Failed to get a new observation message
        return -1, "", "", "", messages

    # Call GPT API
    _, _, gpt_call_error, openai_response = call_gpt4_api(args, client, messages, 10, logger, 0.5)
    
    if gpt_call_error:
        logger.error('GPT API call failed.')
        return -1, "", "", "", messages
    else:
        logger.info('API call complete!')

    # Update the messages with the response from GPT
    gpt_4v_res = openai_response.choices[0].message.content
    if not isinstance(gpt_4v_res, str):
        logger.error('GPT did not return a string.')
        return -1, "", "", "", messages

    agent_message = { 'role': 'assistant', 'content': gpt_4v_res }
    
    # Log the new LLM response and add it to the messages array
    logger.info('New message received!')
    print_message(agent_message, logger)
    messages.append(agent_message)

    # Extract the action information from the GPT-4v response
    action_key, info, fail_obs = extract_action_from_gpt4v_response(gpt_4v_res, logger)
    finish = False
    if not fail_obs:
        # Interpret and execute the action
        fail_obs, pdf_obs, warn_obs, finish = action_controller(
            action_key, info, web_eles, agent_driver, args, logger)
    
    # Log the current URL
    logger.info(f'Current URL: {agent_driver.current_url}')

    # If the agent has returned to the home page, the task is complete
    if is_home_page(agent_driver, site_url):
        finish = True

    # Remove and reset the rects on the webpage
    rects = remove_rects(agent_driver, rects, logger)

    if finish:
        # The task is complete!
        return 1, fail_obs, pdf_obs, warn_obs, messages
    else:
        # The task is not complete yet
        return 0, fail_obs, pdf_obs, warn_obs, messages

def execute_task(logger, messages, args, task, task_driver, init_msg, run_output_dir, site_url):
    # Get an OpenAI client
    client = get_openai_client(logger)

    # Initialize tracking variables
    fail_obs = ""  # When error execute the action
    pdf_obs = ""  # When download PDF file
    warn_obs = ""  # Type warning

    # Try to accomplish the task in max_iter steps
    task_max_iter = task.get('max_iter', 30)
    iteration_result = 0
    for it in range(1, task_max_iter + 1):
        iteration_result, fail_obs, pdf_obs, warn_obs, messages, = execute_task_iteration(
            it, args, task_driver, run_output_dir, init_msg, messages, client, fail_obs, pdf_obs, warn_obs, logger, site_url)
        
        if iteration_result != 0:
            break

    if iteration_result == -1:
        logger.error('Task failed!')
    elif iteration_result == 1:
        logger.info('Task complete!')
    else:
        logger.error(f'Task did not complete in {task_max_iter} iterations!')

    return iteration_result, messages

# Do the following args.num_agents times:
#    a. Ensure that the agent is on the home page
#    b. Execute the task
#    c. Reset the agent's progress
def execute_lesson(task_driver, logger, output_dir, task, args):
    logger.info(f"Executing lesson {task['name']}!")
        
    # Initialize an output directory for this run
    run_output_dir = os.path.join(output_dir, f"screenshots")
    
    # Create the output directory!
    os.makedirs(run_output_dir, exist_ok=True)

    # Initialize the system prompt
    system_prompt = init_lesson_prompt(task, logger)

    # Initialize the task messages
    messages = [{'role': 'system', 'content': system_prompt}]

    # Execute the task
    _, messages = execute_task(logger, messages, args, task, task_driver, "", run_output_dir)

    # Save the messages
    print_messages(messages, save_dir=run_output_dir)

    logger.info(f"Finished lesson {task['name']}!")

# Navigate to the overview page of the lesson
def navigate_to_lesson(task_driver, task_id, logger, site_url):
    logger.info(f"Navigating to the overview page of lesson {task_id}...")

    # Navigate to the overview page of the lesson
    task_driver.get(f'{site_url}/cip4/learn/{task_id}')

    # Wait for the page to load
    time.sleep(3)

    logger.info(f'Current URL: {task_driver.current_url}')

# Do the following args.num_agents times
def execute_lesson_many_times(task_driver, logger, output_dir, task, args, site_url, num_runs=1, ablation=False):
    logger.info(f"Executing lesson {task['name']}!")

    # Do the lesson args.num_agents times
    for run_it in range(num_runs):
        exclude_index = None
        if ablation:
            exclude_index = run_it % len(INSTRUCTIONS)
            
        # Initialize the system prompt
        system_prompt = init_lesson_prompt(task, logger, exclude_index=exclude_index)

        # Initialize an output directory for this run
        run_output_dir = os.path.join(output_dir, f"run_{run_it}")

        # We already completed this iteration, we can move on
        if os.path.exists(run_output_dir):
            logger.info(f"Run {run_it} already exists! Skipping...")
            continue

        logger.info(f"Starting run {run_it}!")
        
        # Create the output directory!
        os.makedirs(run_output_dir, exist_ok=True)

        # Initialize the task messages
        messages = [{'role': 'system', 'content': system_prompt}]

        # Navigate to the lesson
        navigate_to_lesson(task_driver, task['id'], logger, site_url)

        # Execute the task
        _, messages = execute_task(logger, messages, args, task, task_driver, "", run_output_dir, site_url)

        # Save the messages
        print_messages(messages, save_dir=run_output_dir)

        logger.info(f"Finished run {run_it}!")