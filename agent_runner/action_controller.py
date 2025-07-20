import platform
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

def reload_page(driver_task):
    driver_task.refresh()
    time.sleep(2)

def exec_action_click(info, web_ele, driver_task):
    driver_task.execute_script("arguments[0].setAttribute('target', '_self')", web_ele)
    web_ele.click()
    time.sleep(1) # 3 for baseline_agent

# Remove any leading and trailing backticks, double quotes, single quotes, and spaces
def parse_code_line(line):
    stripped_content = line.strip("`\"' ")
    return stripped_content

# Write the code to the Code in Place editor!
# This function will first delete the existing code in the editor and then paste the new code.
def exec_action_code(code, driver_task, logger):
    logger.info(f'Writing code to the editor:\n{code}')
    
    # Prepare the code string for JavaScript
    code_js = code.replace('\\', '\\\\').replace('\n', '\\n').replace("'", "\\'")
    
    try:
        # JavaScript script to set the value in the Monaco editor
        script = f"""
        var editor = document.querySelector('.monaco-editor')
                    ? document.querySelector('.monaco-editor').CodeMirror || 
                    document.querySelector('.monaco-editor').editor || 
                    monaco.editor.getEditors()[0]
                        : null;
        if (editor) {{
            editor.setValue('{code_js}');
        }} else {{
            console.log('Editor not found');
        }}
        """
        
        # Execute the script
        driver_task.execute_script(script)
        logger.info('Code injected into the editor.')

        # Wait to observe the result
        time.sleep(2) # 2 for baseline_agent, not sure how long to wait here...
        return ""
    except Exception as e:
        logger.error(f'Error writing code to the editor: {e}')
        reload_page(driver_task)
        return "Error writing code to the editor. The editor may not be available."

def exec_action_type(info, web_ele, driver_task):
    warn_obs = ""
    type_content = info['content']

    ele_tag_name = web_ele.tag_name.lower()
    ele_type = web_ele.get_attribute("type")
    # outer_html = web_ele.get_attribute("outerHTML")
    if (ele_tag_name != 'input' and ele_tag_name != 'textarea') or (ele_tag_name == 'input' and ele_type not in ['text', 'search', 'password', 'email', 'tel']):
        warn_obs = f"note: The web element you're trying to type may not be a textbox, and its tag name is <{web_ele.tag_name}>, type is {ele_type}."

    # Clear the textbox
    try:
        # Another way to delete
        if platform.system() == 'Darwin':
            web_ele.send_keys(Keys.COMMAND + "a")
        else:
            web_ele.send_keys(Keys.CONTROL + "a")
        web_ele.send_keys(" ")
        web_ele.send_keys(Keys.BACKSPACE)
    except:
        pass

    actions = ActionChains(driver_task)
    actions.click(web_ele).perform()
    actions.pause(1)

    try:
        driver_task.execute_script("""window.onkeydown = function(e) {if(e.keyCode == 32 && e.target.type != 'text' && e.target.type != 'textarea' && e.target.type != 'search') {e.preventDefault();}};""")
    except:
        pass

    actions.send_keys(type_content)
    actions.pause(2)

    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(0.5) # 10 for baseline_agent
    return warn_obs

def exec_action_scroll(info, web_eles, driver_task, args, obs_info, logger):
    try:
        scroll_ele_number = info['number']
        scroll_ele_number = scroll_ele_number.lower()
        
        # Get the scrollable container
        scroll_container = None
        if scroll_ele_number == "code_editor":
            scroll_container = driver_task.find_element(By.CSS_SELECTOR, '#code-editor')
        elif scroll_ele_number == "terminal":
            scroll_container = driver_task.find_element(By.CSS_SELECTOR, '#terminal-pre')
        elif scroll_ele_number == "assignment_description":
            scroll_container = driver_task.find_element(By.CSS_SELECTOR, '#ide-main-content > div.w-100.h-100')
        elif scroll_ele_number == "home_page":
            scroll_container = driver_task.find_element(By.CSS_SELECTOR, '#todo-container')
        elif scroll_ele_number == "lesson_page":
            scroll_container = driver_task.find_element(By.CSS_SELECTOR, '#root > div > div:nth-child(2) > div > div > div > div > main')

        if scroll_container:
            # Scroll the container!
            logger.info(f'Scrolling element {scroll_ele_number}...')
            scroll_content = info['content']
            scroll_amount = args.window_height * 2 // 3
            if scroll_content == 'down':
                driver_task.execute_script("arguments[0].scrollTop += arguments[1];", scroll_container, scroll_amount)
            else:
                driver_task.execute_script("arguments[0].scrollTop -= arguments[1];", scroll_container, scroll_amount)
            time.sleep(0.5) # 3 for baseline_agent
            return ""
        else:
            logger.error('Scrollable container not found.')
            return 'Scrollable container not found.'
        
    except NoSuchElementException:
        logger.error('Scrollable container not found.')
        reload_page(driver_task)
        return 'Scrollable container not found.'

    except Exception as e:
        logger.error('Driver error when scrolling.')
        logger.error(f"{e}")
        reload_page(driver_task)
        return 'Driver error when scrolling.'

def action_controller(action_key, info, web_eles, driver_task, args, logger):
    # Reset the observation information
    fail_obs = ""
    pdf_obs = ""
    warn_obs = ""
    finish = False

    try:
        # Switch to the current window
        window_handle_task = driver_task.current_window_handle
        driver_task.switch_to.window(window_handle_task)

        if action_key == 'click':
            click_ele_number = int(info[0])

            if click_ele_number >= len(web_eles):
                logger.error('Invalid element number for click action.')
                fail_obs = "The element you're trying to interact with was not found. Please check the Numerical Label or Action."
            else:
                web_ele = web_eles[click_ele_number]

                ele_tag_name = web_ele.tag_name.lower()
                ele_type = web_ele.get_attribute("type")

                exec_action_click(info, web_ele, driver_task)

                if ele_tag_name == 'button' and ele_type == 'submit':
                    time.sleep(0.5) # 10 for baseline_agent

        elif action_key == 'wait':
            time.sleep(3) # 5 for baseline_agent

        elif action_key == 'type':
            type_ele_number = int(info['number'])

            if type_ele_number >= len(web_eles):
                logger.error('Invalid element number for type action.')
                fail_obs = "The element you're trying to interact with was not found. Please check the Numerical Label or Action."
            else:
                web_ele = web_eles[type_ele_number]
                warn_obs = exec_action_type(info, web_ele, driver_task)

        elif action_key == 'code':
            code = info['content']
            fail_obs = exec_action_code(code, driver_task, logger)

        elif action_key == 'scroll':
            fail_obs = exec_action_scroll(info, web_eles, driver_task, args, None, logger)

        elif action_key == 'goback':
            driver_task.back()
            time.sleep(2) 

        elif action_key == 'gohome':
            # Navigate to the home page
            driver_task.get('https://codeinplace.stanford.edu/cip4/studenthome')
            time.sleep(2)

        elif action_key == 'answer':
            # logger.info(f"Concluding thoughts: {info['content']}")
            finish = True

        else:
            raise NotImplementedError
    
    except NoSuchElementException as e:
        logger.error(f'Element not found: {e}')
        fail_obs = "The element you're trying to interact with was not found. Please check the Numerical Label or Action."
        reload_page(driver_task)
    
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        fail_obs = "An unexpected error occurred while executing the action."
        reload_page(driver_task)
    
    finally:
        # Cleanup actions?
        pass

    return fail_obs, pdf_obs, warn_obs, finish