import os
import base64
import re
from agent_runner.audio_helper_cip import get_audio_from_transcript
from agent_runner.thought_action_helper import extract_information
from agent_runner.print_message_helper import print_message

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def add_rectangles_to_webpage(browser, logger):
    # Read in the javascript code as a string from the file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_filename = os.path.join(current_dir, f'get_web_elements.js')
    file =  open(js_filename, "r")
    js_script = file.read()

    # Execute the javascript code
    rects, items_raw = browser.execute_script(js_script)

    logger.info(f"Finished adding {len(items_raw)} elements (rectangles) to the webpage!")

    return rects, items_raw

# Create a string that describes the elements in natural language (for the prompt)
def create_rect_text_description(items_raw, logger):
    try:
        format_ele_text = []
        count = 0
        for web_ele_id in range(len(items_raw)):
            label_text = items_raw[web_ele_id]['text']
            ele_tag_name = items_raw[web_ele_id]['element'].tag_name
            ele_type = items_raw[web_ele_id]['element'].get_attribute("type")
            ele_aria_label = items_raw[web_ele_id]['element'].get_attribute("aria-label")
            input_attr_types = ['text', 'search', 'password', 'email', 'tel']

            if not label_text:
                if (ele_tag_name.lower() == 'input' and ele_type in input_attr_types) or ele_tag_name.lower() == 'textarea' or (ele_tag_name.lower() == 'button' and ele_type in ['submit', 'button']):
                    if ele_aria_label:
                        format_ele_text.append(f"[{web_ele_id}]: <{ele_tag_name}> \"{ele_aria_label}\";")
                    else:
                        format_ele_text.append(f"[{web_ele_id}]: <{ele_tag_name}> \"{label_text}\";" )

            elif label_text and len(label_text) < 200:
                if not ("<img" in label_text and "src=" in label_text):
                    if ele_tag_name in ["button", "input", "textarea"]:
                        if ele_aria_label and (ele_aria_label != label_text):
                            format_ele_text.append(f"[{web_ele_id}]: <{ele_tag_name}> \"{label_text}\", \"{ele_aria_label}\";")
                        else:
                            format_ele_text.append(f"[{web_ele_id}]: <{ele_tag_name}> \"{label_text}\";")
                    else:
                        if ele_aria_label and (ele_aria_label != label_text):
                            format_ele_text.append(f"[{web_ele_id}]: \"{label_text}\", \"{ele_aria_label}\";")
                        else:
                            format_ele_text.append(f"[{web_ele_id}]: \"{label_text}\";")

            # Increment the count
            count += 1

        format_ele_text = '\t'.join(format_ele_text)
        logger.info(f"Finished creating text description for {count} elements")
        return format_ele_text
    
    except Exception as _:
        # An element went stale! We need to retry
        logger.error(f"Error creating text description for elements.")
        return ""

def remove_rects(driver_task, rects, logger):
    if rects:
        logger.info(f"Removing {len(rects)} rectangles...")
        count = 0
        for rect_ele in rects:
            try:
                driver_task.execute_script("arguments[0].remove()", rect_ele)
                count += 1
            except:
                # NOTE - might want to add an error signal here, like return False
                logger.error('Failed to remove a rectangle. Continuing...')
                pass
        rects = []
        logger.info(f"Removed {count} rectangles.")
    
    return rects

# interact with webpage and add rectangles on elements
def get_web_element_rect(browser, max_tries, logger):
    # Try to add rectangles to the webpage
    for i in range(max_tries):    
        logger.info("Adding rectangles to the webpage")

        # Add rectangles to the webpage
        rects, items_raw = add_rectangles_to_webpage(browser, logger)
        format_ele_text = create_rect_text_description(items_raw, logger)

        if format_ele_text:
            # Successfully added rectangles to the webpage!
            return rects, [web_ele['element'] for web_ele in items_raw], format_ele_text
        else:
            # Remove the rectangles from the webpage
            remove_rects(browser, rects, logger)

            # Try again
            logger.error(f"Failed to add rectangles to the webpage, {max_tries - i} tries left.")

    # Failed to add rectangles to the webpage
    return None, None, None

def format_msg(it, init_msg, pdf_obs, warn_obs, web_img_b64, web_text, audio_text, logger, prev_actions):
    msg = ""

    msg = f"Observation:{warn_obs} please analyze the attached screenshot, then output a Description, Thought, and Action. I've provided the tag name of each element and the text that it contains (if text exists). Please focus more on the screenshot and then refer to the textual information.\n{web_text}"

    # Add the audio transcription if it exists
    if audio_text:
        logger.info(f"Audio transcription: {audio_text}")
        msg += f"\nTranscript of lecture video:\n\"{audio_text}\""

    if len(prev_actions) > 0:
        msg += "\n\nIn the last few steps, you have taken the following actions:"
        for i, action in enumerate(prev_actions):
            if action[0] is None:
                msg += f"\n{i + 1}. Your action was not formatted correctly."
            elif action[1] is None or len(action[1]) == 0:
                msg += f"\n{i + 1}. {action[0]}"
            elif len(action[1]) > 0:
                msg += f"\n{i + 1}. {action[0]} {action[1][0]}"

    msg_format = {
        'role': 'user',
        'content': [
            {
                'type': 'text', 
                'text': msg
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{web_img_b64}"}
            }
        ]
    }

    return msg_format

def get_new_observation(fail_obs, pdf_obs, warn_obs, it, args, driver_task, task_dir, init_msg, client, logger, prev_actions):
    # Get the web element rects
    rects, web_eles, web_eles_text = get_web_element_rect(driver_task, 3, logger)
    
    # If the web element rects cannot be obtained, return None
    if not rects:
        return None, None, None, None

    # Take a screenshot of the page
    img_path = os.path.join(task_dir, 'screenshot{}.png'.format(it))
    driver_task.save_screenshot(img_path)

    # Get the current audio transcript
    audio_text = get_audio_from_transcript(driver_task, logger)

    # Encode the image
    b64_img = encode_image(img_path)

    # Format the message and append it to the messages
    curr_msg = format_msg(it, init_msg, pdf_obs, warn_obs, b64_img, web_eles_text, audio_text, logger, prev_actions)

    logger.info('New message constructed!')
    print_message(curr_msg, logger)

    return curr_msg, rects, web_eles, web_eles_text

def clip_message_and_obs(msg, max_img_num):
    clipped_msg = []
    img_num = 0
    for idx in range(len(msg)):
        curr_msg = msg[len(msg) - 1 - idx]
        if curr_msg['role'] != 'user':
            clipped_msg = [curr_msg] + clipped_msg
        else:
            if type(curr_msg['content']) == str:
                clipped_msg = [curr_msg] + clipped_msg
            elif img_num < max_img_num:
                img_num += 1
                clipped_msg = [curr_msg] + clipped_msg
            else:
                msg_no_pdf = curr_msg['content'][0]["text"].split("Observation:")[0].strip() + "Observation: A screenshot and some texts. (Omitted in context.)"
                msg_pdf = curr_msg['content'][0]["text"].split("Observation:")[0].strip() + "Observation: A screenshot, a PDF file and some texts. (Omitted in context.)"
                curr_msg_clip = {
                    'role': curr_msg['role'],
                    'content': msg_no_pdf if "You downloaded a PDF file" not in curr_msg['content'][0]["text"] else msg_pdf
                }
                clipped_msg = [curr_msg_clip] + clipped_msg
    return clipped_msg

# Get the last three actions from the messages
def get_prev_actions(messages, logger):
    pattern = r'Description:|Thought:|Action:|Observation:'
    actions = []
    for msg in messages:
        if msg['role'] == 'assistant':
            msg_content = msg['content']
            chosen_action = re.split(pattern, msg_content)[3].strip()
            action_key, info = extract_information(chosen_action)
            actions.append((action_key, info))

    if len(actions) > 3:
        actions = actions[-3:]

    logger.info(f"Previous actions: {actions}")
    return actions

# Get an updated messages array containing a new observation
def get_updated_messages(messages, fail_obs, pdf_obs, warn_obs, it, args, 
                         driver_task, task_dir, init_msg, client, 
                         logger):
    
    # Get the last three actions
    prev_actions = get_prev_actions(messages, logger)

    # Construct a new message with the current screenshot
    new_observation, rects, web_eles, _ = get_new_observation(fail_obs, pdf_obs, warn_obs, it, args, driver_task, task_dir, init_msg, client, logger, prev_actions)

    if new_observation is None:
        logger.error('Failed to get new message.')
        return None, rects, web_eles
    else:
        # Append the new message to the messages
        logger.info('Adding new message!')
        messages.append(new_observation)
        messages = clip_message_and_obs(messages, args.max_attached_imgs)

        return messages, rects, web_eles