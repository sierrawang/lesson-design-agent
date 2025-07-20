import re
from agent_runner.openai_helper import call_gpt, get_openai_client

# Return a dictionary with the predicted dropout distribution
def parse_gpt_response(response):
    # Split the response by newlines
    lines = response.split("\n")

    # Initialize the dictionary to store the predicted dropout distribution
    predicted_dropout_distribution = {}

    pattern = r'\s*- Slide (\d+) \(([^)]+)\): \*\*(\d+\.\d+)\*\*'

    # Parse the response
    for line in lines:
        match = re.match(pattern, line)
        if match is not None:
            # slide_number = match.group(1)
            slide_name = match.group(2)
            completion_rate = float(match.group(3))
            predicted_dropout_distribution[slide_name] = completion_rate

    # Normalize the completion rates
    total_completion_rate = sum(predicted_dropout_distribution.values())
    for slide in predicted_dropout_distribution:
        predicted_dropout_distribution[slide] = predicted_dropout_distribution[slide] / total_completion_rate

    return predicted_dropout_distribution

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