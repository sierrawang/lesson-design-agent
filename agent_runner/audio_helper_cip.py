import os
import json

# Get the filename for the downloaded transcript of the current page, if it exists
def get_transcript_filename(driver_task):
    current_url = driver_task.current_url

    # Warning - this only works for getting lesson video transcripts!
    if "/cip4/learn/" in current_url:
        # Get the lesson and slide id from the URL
        url_parts = current_url.split("/")
        lesson_id = url_parts[-2]
        slide_id = url_parts[-1]

        # Construct the filename for the transcript
        current_dir = os.path.dirname(os.path.abspath(__file__))
        transcript_filename = os.path.join(current_dir, f"../../cip_data/downloaded_data/lesson_video_transcripts/{lesson_id}_{slide_id}.json")
        return transcript_filename
    else:
        return ""

def get_audio_from_transcript(driver_task, logger):
    # Get the filename of the transcript for the current page
    current_transcript_filename = get_transcript_filename(driver_task)

    # Check if the transcript file exists
    if os.path.exists(current_transcript_filename):
        logger.info(f"Transcript file exists! ({current_transcript_filename})")
        # Load the transcript as a JSON object
        transcript = json.load(open(current_transcript_filename, 'r'))

        audio_text = ""
        for item in transcript:
            audio_text += item["text"] + " "

        return audio_text
    else:
        # There is no transcript file for the current page
        return ""
