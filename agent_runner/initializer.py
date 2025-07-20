import logging
import os
import json
import time
from selenium import webdriver
from agent_runner.action_controller import action_controller
from agent_runner.observation_helper import get_web_element_rect, remove_rects

# Create the directory with the given name
def init_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

# Set up the logger for this task
def setup_logger(output_dir, task_id):
    # Create a log file for this task
    log_file_path = os.path.join(output_dir, 'agent_logs.log')

    # Create a unique logger for the task using its ID
    logger = logging.getLogger(task_id)

    # Add a file handler
    handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set the logging level
    logger.setLevel(logging.INFO)

    # Disable propagation to the root logger
    logger.propagate = False

    return logger

# Get an array of login actions for the agent by grabbing account credentials from the queue
def get_login_actions(accounts_q):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    init_actions = json.load(open(os.path.join(current_dir, 'login_actions.json')))
    account_info = accounts_q.get() # Grab account credentials (this will block until an account is available)
    init_actions[1]['info']['content'] = account_info['username']
    init_actions[2]['info']['content'] = account_info['password']
    return init_actions, account_info

# Create a directory for the login screenshots
def make_login_dir(output_dir):
    login_dir = os.path.join(output_dir, 'login')
    init_dir(login_dir)
    return login_dir

# Set up the browser driver configuration
def driver_config(args):
    # Initialize the driver options
    options = webdriver.ChromeOptions()

    # Set whether the device scale factor is forced
    if args.save_accessibility_tree:
        args.force_device_scale = True

    # Force the device scale factor to 1
    if args.force_device_scale:
        options.add_argument("--force-device-scale-factor=1")

    # Check whether the browser is headless
    if args.headless:
        # print("Running in headless mode.")
        options.add_argument("--headless")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

    return options

# Set up the browser - set the configuration, 
# open the Code in Place website, and prevent the 
# page from scrolling down when pressing the SPACE key
def setup_browser(args, site_url):
    # Set up the browser driver configuration
    options = driver_config(args)

    # Open the browser
    driver_task = webdriver.Chrome(options=options)

    # Set the window size
    driver_task.set_window_size(args.window_width, args.window_height)
    
    # Load the web page
    driver_task.get(f'{site_url}/welcome')

    # Inject the script to prevent the page from scrolling down when pressing the SPACE key
    driver_task.execute_script("""window.onkeydown = function(e) {if(e.keyCode == 32 && e.target.type != 'text' && e.target.type != 'textarea') {e.preventDefault();}};""")
    time.sleep(3)

    return driver_task

# Log in to code in place
def login(agent, logger, path, args, output_dir=None):
    fail_obs = ""
    warn_obs = ""
    finish = False

    # Execute the path
    i = 0
    for action_data in path:
        # Parse the action
        action, info = action_data['action'], action_data['info']

        # Add the rectangles to the web page
        rects, web_eles, _ = get_web_element_rect(agent, 10, logger)

        if output_dir:
            # Save the screenshot
            agent.save_screenshot(os.path.join(output_dir, f'{i}_{action}_{info}.png'))

        if rects is None:
            # The rectangles could not be added, so we are likely in an error state!
            return None, None, None, None, True

        # Execute the action
        fail_obs, pdf_obs, warn_obs, finish = action_controller(action, info, web_eles, agent, args, logger)

        # Remove the rectangles
        remove_rects(agent, rects, logger)

        i += 1

    return agent, fail_obs, pdf_obs, warn_obs, finish

# Set up the browser, log in, and navigate to the lesson 
def get_task_driver(logger, args, accounts_q, output_dir, site_url):
    login_actions, account_info = get_login_actions(accounts_q)
    login_dir = make_login_dir(output_dir)
    task_driver = setup_browser(args, site_url)
    login(task_driver, logger, login_actions, args, login_dir)
    return task_driver, account_info

# Initialize the agent to execute the lesson:
#    a. Set up the output directory and logging
#    b. Start up the browser
#    c. Log in to the Code in Place website
#    d. Navigate to the lesson
def initialize_task(task_id, args, accounts_q, output_folder, site_url):
    # Initialize the output directory for this task
    output_dir = f'{output_folder}/{task_id}'
    init_dir(output_dir)

    # Set up the logger for this task
    logger = setup_logger(output_dir, task_id)

    # Start the agent and log in to the Code in Place website
    task_driver, account_info = get_task_driver(logger, args, accounts_q, output_dir, site_url)

    return task_driver, logger, output_dir, account_info