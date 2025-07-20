import os
import json

# Load the lessons in order from the roadmap
def load_lessons_in_order():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lessons_in_order_filename = os.path.join(current_dir, '../cip_data/downloaded_data/lessons_in_order.json')
    return json.load(open(lessons_in_order_filename))

# Return the slides for the given lesson
def get_slides_for_lesson(lesson_id, lessons_in_order=None):
    if lessons_in_order is None:
        lessons_in_order = load_lessons_in_order()

    slides = []
    for lesson in lessons_in_order:
        if lesson[0] == lesson_id:
            slides = lesson[1]
            break
    return slides