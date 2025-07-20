import time
import re

def extract_information(text):
    patterns = {
        "answer": r"^ANSWER",
        "click": r"Click \[?(\d+)\]?",
        "type": r"Type \[?(\d+)\]?[; ]+\[?(.[^\]]*)\]?",
        "code": r"Code[; ]+[`\"'\s]*(?:python[`\"'\s]*)*([\s\S]*?)[`\"'\s]*$",
        "scroll": r"Scroll \[?(\d+|home_page|assignment_instructions|code_editor|lesson_page)\]?[; ]+\[?(up|down)\]?",
        "wait": r"^Wait",
        "goback": r"^GoBack",
        "gohome": r"^GoHome"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            if key in ["click", "wait", "goback", "google", "gohome", "answer"]:
                # no content
                return key, match.groups()
            else:
                return key, {"number": match.group(1), "content": match.group(2)} if key in ["type", "scroll"] else {"content": match.group(1)}
    return None, None

# Call the GPT API
def call_gpt4_api(args, openai_client, messages, max_retry, logger, temp=0):
    retry_times = 0
    while True:
        try:
            logger.info(f'Calling {args.api_model} API...')
            # print(f'Calling {args.api_model} API...')
            openai_response = openai_client.chat.completions.create(
                model=args.api_model, 
                messages=messages, 
                # max_tokens=1000, 
                seed=args.seed,
                temperature=temp,
            )

            prompt_tokens = openai_response.usage.prompt_tokens
            completion_tokens = openai_response.usage.completion_tokens

            logger.info(f'Prompt Tokens: {prompt_tokens}; Completion Tokens: {completion_tokens}')

            gpt_call_error = False
            return prompt_tokens, completion_tokens, gpt_call_error, openai_response

        except Exception as e:
            logger.error(f'Error occurred, retrying. Error type: {type(e).__name__}')
            # print(f'Error occurred, retrying. Error type: {type(e).__name__}')

            if type(e).__name__ == 'RateLimitError':
                time.sleep(10)

            elif type(e).__name__ == 'APIError':
                time.sleep(15)

            elif type(e).__name__ == 'InvalidRequestError':
                gpt_call_error = True
                return None, None, gpt_call_error, None

            else:
                gpt_call_error = True
                return None, None, gpt_call_error, None

        retry_times += 1
        if retry_times == max_retry:
            logger.info('Retrying too many times')
            # print('Retrying too many times')
            return None, None, True, None
        
# Extract the action from the GPT-4v response
# Return the action key, the information, and the failure observation
def extract_action_from_gpt4v_response(gpt_4v_res, logger):
    pattern = r'### Description:|### Thought:|### Action:|Observation:'

    try:
        assert 'Description' in gpt_4v_res and 'Thought:' in gpt_4v_res and 'Action:' in gpt_4v_res
        bot_description = re.split(pattern, gpt_4v_res)[1].strip()
        logger.info(f'Parsed Description: {bot_description}')
        bot_thought = re.split(pattern, gpt_4v_res)[2].strip()
        logger.info(f'Parsed Thought: {bot_thought}')
        chosen_action = re.split(pattern, gpt_4v_res)[3].strip()
        action_key, info = extract_information(chosen_action)
        logger.info(f'Parsed Action: {action_key}, {info}')

        if action_key is None:
            logger.error(f'Format ERROR: Action is not in the correct format.')
            fail_obs = "Format ERROR: Action is not in the correct format."
            return "", "", fail_obs
        else:
            return action_key, info, ""
    
    except AssertionError as e:
        logger.error(f'Format ERROR: Both "Thought" and "Action" should be included in your reply.')
        fail_obs = "Format ERROR: Both 'Thought' and 'Action' should be included in your reply."
        return "", "", fail_obs