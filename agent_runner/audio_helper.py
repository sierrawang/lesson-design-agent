import os
import json
from selenium.webdriver.common.by import By

# Get the filename for the downloaded transcript of the current page, if it exists
def get_transcript_filename(driver_task):
    current_url = driver_task.current_url

    # Warning - this only works for getting lesson video transcripts!
    if current_url.startswith("https://codeinplace.stanford.edu/cip4/learn/"):
        # Get the lesson and slide id from the URL
        url_parts = current_url.split("/")
        lesson_id = url_parts[-2]
        slide_id = url_parts[-1]

        # Construct the filename for the transcript
        current_dir = os.path.dirname(os.path.abspath(__file__))
        transcript_filename = os.path.join(current_dir, f"../cip_data/downloaded_data/lesson_video_transcripts/{lesson_id}_{slide_id}.json")
        return transcript_filename
    else:
        return ""

# Return the number of seconds since the start of the video
def get_current_video_timestamp(driver_task, logger):
    try:
        # Switch to the iframe that contains the YouTube video using its id 
        video_iframe = driver_task.find_element(By.CSS_SELECTOR, "iframe[src*='youtube.com/embed/']")
        driver_task.switch_to.frame(video_iframe)
        
        # Retrieve the current playback time from the <video> element within the iframe
        current_time = driver_task.execute_script("""
            // Check if the embedded video is accessible and retrieve current time
            const videoElement = document.querySelector('video');
            return videoElement ? videoElement.currentTime : 0;
        """)
        
        # Switch back to the main page context
        driver_task.switch_to.default_content()
        
        return current_time
    except Exception as e:
        logger.error(f"Error getting current video timestamp: {e}")
        return -1

# Get the audio transcription between the given timestamps from the transcript
def get_audio_between_timestamps(transcript, start_time, end_time):
    result = ""
    for item in transcript:
        # Get a timestamp for the current item (just use the start time)
        item_timestamp = item["start"]

        # If the item is within the given timestamps, add it to the result
        if item_timestamp >= start_time and item_timestamp <= end_time:
            result += item["text"] + " "
        
    return result

def get_recent_audio_from_transcript(driver_task, audio_info, logger):
    # Get the filename of the transcript for the current page
    current_transcript_filename = get_transcript_filename(driver_task)
    
    # If we are on a new page, reset the last video timestamp
    # This means that if we are watching a new video, 
    # we will grab all the audio from the beginning
    if current_transcript_filename != audio_info["last_video_filename"]:
        audio_info["last_video_timestamp"] = 0
        audio_info["last_video_filename"] = current_transcript_filename

    # Check if the transcript file exists
    if os.path.exists(current_transcript_filename):
        logger.info(f"Transcript file exists! ({current_transcript_filename})")
        # Load the transcript as a JSON object
        transcript = json.load(open(current_transcript_filename, 'r'))

        # Get the current video timestamp
        current_video_timestamp = get_current_video_timestamp(driver_task, logger)
        logger.info(f"Current video timestamp: {current_video_timestamp}")
        if current_video_timestamp == -1:
            return "", audio_info

        # Construct the audio transcription from the last video timestamp to the current timestamp
        audio_text = get_audio_between_timestamps(transcript, audio_info["last_video_timestamp"], current_video_timestamp)

        # Update the audio information
        audio_info["last_video_timestamp"] = current_video_timestamp
        audio_info["last_video_filename"] = current_transcript_filename

        return audio_text, audio_info
    else:
        # There is no transcript file for the current page
        return "", audio_info

# Get the recent audio from the queue or a downloaded transcript
def get_recent_audio(driver_task, audio_info, client, logger):
    logger.info("Getting recent audio...")
    audio_text = ""
    if audio_info["listen_audio"]:
        # Get the recent audio from the queue
        # audio_text = get_recent_audio_from_queue(client, audio_info)
        assert False, "This function is not currently implemented."
    else:
        # Get the recent audio from the transcript
        audio_text, audio_info = get_recent_audio_from_transcript(driver_task, audio_info, logger)

    return audio_text, audio_info

def setup_audio(listen_audio):
    # Initialize the information for audio recording
    audio_info = { 
        "listen_audio": listen_audio,
        "stop_event": None, 
        "audio_queue": None, 
        "recording_thread": None, 
        "last_video_timestamp": 0, 
        "last_video_filename": "" 
    }

    # If we are listening to audio, set up the audio queue and thread
    assert not audio_info["listen_audio"], "Not set up to listen to audio."
    # if audio_info["listen_audio"]:
    #     audio_info["stop_event"] = threading.Event()
    #     audio_info["audio_queue"] = queue.Queue()
    #     audio_info["recording_thread"] = run_recording_thread(audio_info["stop_event"], audio_info["audio_queue"])
    
    return audio_info

# Stop the audio recording thread
def stop_audio(audio_info):
    if audio_info["listen_audio"]:
        audio_info["stop_event"].set()
        audio_info["recording_thread"].join()

# # The following code is used to record audio from the input device and convert it to text using OpenAI API
# # For now, we will use a pre-recorded audio file instead of recording audio in real-time.

# import sounddevice as sd
# import soundfile as sf
# from pydub import AudioSegment
# import tempfile
# import numpy as np
# import queue
# import threading

# # Determine the index of the speaker device
# def get_speaker_device_index():
#     device_key = 'BlackHole 2ch'
#     device_index = -1
#     devices = sd.query_devices()
#     for idx, device in enumerate(devices):
#         if device['name'] == device_key:
#             device_index = idx

#     return device_index

# def record_audio(q, stop_event, device_index):
#     # Get the default samplerate for the input device
#     samplerate = int(sd.query_devices(device_index, 'input')['default_samplerate'])
    
#     # Callback function to add audio data to the queue
#     def audio_callback(indata, frames, time, status):
#         if status:
#             logging.error(f"Audio Callback Error: {status}")
#         q.put(indata.copy())

#     # Start listening to the audio input device
#     # The callback function will be called when audio data is available
#     with sd.InputStream(callback=audio_callback, channels=1, device=device_index, samplerate=samplerate):
#         while not stop_event.is_set():
#             sd.sleep(1000)

# # Check if the audio is silent by comparing the dBFS value (average loudness)
# # with the threshold
# def is_silent(audio_file, threshold=-50.0):
#     audio = AudioSegment.from_file(audio_file)
#     return audio.dBFS < threshold

# def get_recent_audio_from_queue(q, client):
#         # Check if the queue is not empty
#     if not q.empty():
#         logging.info("Queue is not empty.")
#         frames = []

#         # Combine all audio data in the queue
#         while not q.empty():
#             frames.append(q.get())
        
#         audio_data = np.concatenate(frames)
        
#         # Save audio data to a temporary WAV file
#         with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile:
#             # Write the audio data to the temporary file
#             sf.write(tmpfile.name, audio_data, 44100)

#             tmp_filename = tmpfile.name

#             # Open the file in read-binary mode
#             audio_file= open(tmp_filename, "rb")

#             # Check if the audio is silent
#             if is_silent(tmp_filename):
#                 logging.info("Audio is silent.")
#                 return ""

#             # Use OpenAI API to convert speech to text
#             transcription = client.audio.transcriptions.create(
#                 model="whisper-1", 
#                 file=audio_file
#             )
        
#         # Manually remove the temporary file
#         os.remove(tmp_filename)

#         return transcription.text
#     else:
#         return ""

# # Start the thread to listen to the audio input device
# def run_recording_thread(stop_event, audio_queue):
#     # Determine the index of the speaker device to listen to
#     device_index = get_speaker_device_index()

#     # Start a thread to record audio and add to the queue
#     recording_thread = threading.Thread(target=record_audio,
#                                         args=(audio_queue, stop_event, device_index))
#     recording_thread.start()

#     return recording_thread

