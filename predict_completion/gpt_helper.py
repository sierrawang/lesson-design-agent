import re
from agent_runner.openai_helper import call_gpt, get_openai_client

# Extract the predicted completion rate from the GPT response
def parse_gpt_response(response):
    content = response.strip()
    # print(content)

    # Use regex to search for the pattern "**Prediction: X.XX**" where X.XX is a floating-point number
    pattern = r"\*\*Prediction:\s*([0-9]+\.?[0-9]*|\.[0-9]+)\*\*"
    match = re.search(pattern, content)
    if match:
        try:
            # Extract the matched number as a float
            return float(match.group(1))
        except ValueError:
            return None
    return None

# Get the predicted dropout distribution for a specific run of a task
# This will be in the form of a dictionary with the slide names as keys and the dropout rates as values
def get_prediction(system_prompt, max_iter=5):
    # Call the GPT to predict the completion rate
    messages = [
        {
            "role": "user",
            "content": system_prompt
        }
    ]

    # Initialize the OpenAI client
    client = get_openai_client()

    for _ in range(max_iter):
        # Call the GPT API
        response, prompt_tokens, completion_tokens = call_gpt(client, "o1-preview", messages)

        prediction = parse_gpt_response(response)
        if prediction is not None:
            return prediction

    return None