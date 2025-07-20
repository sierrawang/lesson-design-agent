from agent_runner.system_prompt import SYSTEM_PROMPT, INSTRUCTIONS
from cip_helpers.dropout_helper import load_true_dropout_distribution
from cip_helpers.completion_helper import load_true_completion_df, get_engaged_task_completion_rate
from cip_helpers.lessons_helper import get_slides_for_lesson
from tasks.task_helper import get_all_tasks

# Return a string describing the task and how students did on it
def format_example(task, true_completion_df, true_dropout_distribution):
    task_completion, sem = get_engaged_task_completion_rate(task['id'], true_completion_df)
    task_completion *= 100
    task_dropout = true_dropout_distribution[task['id']]
    lesson_slides = get_slides_for_lesson(task['id'])

    example_str = f"**{task['name']}**:\n"
    example_str += f"   - Percent of students who completed the lesson: {task_completion:.2f}%\n"
    example_str += f"   - Number of pages: {len(lesson_slides)}\n"
    example_str += f"   - Of the students who did not complete the lesson, the percent that dropped out at each page:\n"
    i = 1
    for slide in lesson_slides:
        percent_dropout = task_dropout.get(slide, 0.0) * 100
        example_str += f"      - Step {i} ({slide}): {percent_dropout:.2f}%\n"
        i += 1
        
    return example_str

def format_examples(current_task):
    all_tasks = get_all_tasks()
    true_completion_df = load_true_completion_df()
    true_dropout_distribution = load_true_dropout_distribution()
    examples_str = ""
    i = 1
    for task in all_tasks:
        if task['type'] != 'lesson':
            # Only include lessons
            continue

        if task['id'] == current_task['id']:
            # We have reached the current task, so we stop
            break

        example = format_example(task, true_completion_df, true_dropout_distribution)
        examples_str += f"{i}. {example}\n"
        i += 1

    return examples_str


# Construct a string with the instructions except for the excluded index
def add_instructions(prompt, exclude_index=None):
    instructions_str = ""
    examples_str = ""
    for i, instruction in enumerate(INSTRUCTIONS):
        if exclude_index is not None and i == exclude_index:
            continue
        instructions_str += f"-   {instruction[0]}\n\n"
        examples_str += f"-   {instruction[0]}\n    {instruction[1]}\n\n"

    prompt = prompt.replace('INPUT_INSTRUCTIONS', instructions_str)
    prompt = prompt.replace('INPUT_EXAMPLE_RESPONSES', examples_str)

    return prompt

# Prompt the agent to go through the lesson and
# 1. Describe each slide in detail
# 2. Talk about what is confusing on each slide
# 3. Talk about what prior knowledge would be necessary to be able to understand the slide
# 4. Talk about whether this would be confusing for students, and if so, for whom
def init_lesson_prompt(task, logger, exclude_index=None):
    logger.info(f"Generating new system prompt for run {task['name']}...")

    system_prompt = SYSTEM_PROMPT.replace('LESSON_NAME', task['name'])
    system_prompt = add_instructions(system_prompt, exclude_index)

    logger.info("System prompt generated successfully:")
    logger.info(system_prompt)

    return system_prompt
