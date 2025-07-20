from predict_dropout.system_prompt import SYSTEM_PROMPT
from predict_dropout.system_prompt_no_examples import SYSTEM_PROMPT_NO_EXAMPLES
from agent_runner.parse_agent_logs import get_lesson_description_from_agent_run
from cip_helpers.completion_helper import get_engaged_task_completion_rate
from cip_helpers.lessons_helper import get_slides_for_lesson


# Construct a description of this lesson using all the information that we have - including
# the actual results of the lesson
def get_previous_lesson_description(current_task, run_it, true_dropout_distribution, true_completion_df, agents_folder, include_data):
    log_filename = f'{agents_folder}/{current_task["id"]}/agent_logs.log'
    agent_lesson_description = get_lesson_description_from_agent_run(current_task['id'], run_it, log_filename)
    lesson_slides = get_slides_for_lesson(current_task['id'])

    # Construct a description of the lesson using all of the information that we have
    lesson_description = f"**{current_task['name']}:**\n"
    lesson_description += f"{current_task['name']} is a lesson with {len(lesson_slides)} steps." 

    # Include the completion rate for the lesson
    if include_data:
        lesson_completion_rate, _ = get_engaged_task_completion_rate(current_task['id'], true_completion_df)
        lesson_description += f" {lesson_completion_rate * 100:.2f}% of the students who started this lesson completed it."

    # Include the flags for the lesson
    if 'flags' in current_task:
        lesson_description += " This lesson is marked as " + ' and '.join(current_task['flags']) + "."
    else:
        lesson_description += " This lesson is part of the core curriculum of this course."

    # Include the agent's description of each step
    lesson_description += " Here is a summary of each step:\n"
    for i,slide in enumerate(lesson_slides):
        slide_str = f"- Step {i + 1} ({slide}):\n"

        # Add the agent's description of the slide if available
        description = agent_lesson_description.get(slide, None)
        if description:
            slide_str += f"{description}\n"
        else:
            slide_str += "   - We are missing a description for this step.\n"

        # Add the dropout rate for the slide 
        if include_data:
            slide_dropout = true_dropout_distribution[current_task['id']].get(slide, 0.0)
            slide_str += f"   - {slide_dropout * 100:.2f}% of students dropped out at this step.\n"

        lesson_description += slide_str + "\n"
    return lesson_description

def get_all_previous_lesson_descriptions(current_task, run_it, lesson_tasks, true_dropout_distribution, true_completion_df, agents_folder, include_data):
    lesson_descriptions = ""
    for lesson in lesson_tasks:
        if lesson['id'] == current_task['id']:
            break
        else:
            lesson_description = get_previous_lesson_description(lesson, run_it, true_dropout_distribution, true_completion_df, agents_folder, include_data)
            lesson_descriptions += lesson_description + "\n\n"

    return lesson_descriptions

# Construct a description of the lesson using all of the information that we have
# NOT including the actual results of the lesson
def get_current_task_description(current_task, run_it, agents_folder):
    log_filename = f'{agents_folder}/{current_task["id"]}/agent_logs.log'
    agent_lesson_description = get_lesson_description_from_agent_run(current_task['id'], run_it, log_filename)
    lesson_slides = get_slides_for_lesson(current_task['id'])

    lesson_description = f"#### **{current_task['name']}:**\n"
    lesson_description += f"{current_task['name']} is a lesson with {len(lesson_slides)} steps. " 
    if 'flags' in current_task:
        lesson_description += "This lesson is marked as " + ' and '.join(current_task['flags']) + ". "
    else:
        lesson_description += "This lesson is part of the core curriculum of this course. "

    lesson_description += "Here is a summary of each step:\n"
    for i,slide in enumerate(lesson_slides):
        description = agent_lesson_description.get(slide, None)
        if description:
            lesson_description += f"- Step {i + 1} ({slide}):\n{description}\n"
        else:
            lesson_description += f"- Step {i + 1} ({slide}):\n   - We are missing a description for this step.\n"

    return lesson_description

def get_prediction_format(current_task):
    lesson_slides = get_slides_for_lesson(current_task['id'])
    prediction_format = "Prediction:\n"
    for i, slide in enumerate(lesson_slides):
        prediction_format += f"    - Slide {i+1} ({slide}): **X.XXXX**\n"

    prediction_format

    return prediction_format

def get_system_prompt(current_task, run_it, lesson_tasks, true_dropout_distribution, true_completion_df, include_data=True, include_examples=True):
    agents_folder = '../agents2'

    system_prompt = ""
    if include_examples:
        system_prompt = SYSTEM_PROMPT.replace('LESSON_NAME', current_task['name'])
        lesson_descriptions = get_all_previous_lesson_descriptions(current_task, run_it, lesson_tasks, true_dropout_distribution, true_completion_df, agents_folder, include_data)
        system_prompt = system_prompt.replace('PREVIOUS_LESSONS', lesson_descriptions)
    else:
        system_prompt = SYSTEM_PROMPT_NO_EXAMPLES.replace('LESSON_NAME', current_task['name'])
    
    # Add the upcoming lesson description and prediction format
    lesson_description = get_current_task_description(current_task, run_it, agents_folder)
    system_prompt = system_prompt.replace('LESSON_DESCRIPTION', lesson_description)
    system_prompt = system_prompt.replace('PREDICTION_FORMAT', get_prediction_format(current_task))

    return system_prompt