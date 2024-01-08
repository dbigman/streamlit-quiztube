import streamlit as st
from youtube_transcript_api import (
    YouTubeTranscriptApi, YouTubeRequestFailed, VideoUnavailable, InvalidVideoId, TooManyRequests,
    TranscriptsDisabled, NoTranscriptAvailable, NotTranslatable, TranslationLanguageNotAvailable,
    CookiePathInvalid, CookiesInvalid, FailedToCreateConsentCookie, NoTranscriptFound
)

import pysrt

from pytube import extract
import html
from unidecode import unidecode
from pytube import YouTube
import logging
import os
from pydub import AudioSegment


def extract_video_id_from_url(url):
    try:
        return extract.video_id(url)
    except Exception:
        st.error("Please provide a valid YouTube URL.")
        example_urls = [
            'http://youtu.be/SA2iWivDJiE',
            'http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu',
            'http://www.youtube.com/embed/SA2iWivDJiE',
            'http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US',
            'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
            'https://www.youtube.com/watch?time_continue=9&v=n0g-Y0oo5Qs&feature=emb_logo'
        ]
        st.info("Here are some valid formats: " + " ,".join(example_urls))
        st.stop()


def get_transcript_text(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item["text"] for item in transcript])
    except (YouTubeRequestFailed, VideoUnavailable, InvalidVideoId, TooManyRequests, NoTranscriptAvailable, NotTranslatable,
            TranslationLanguageNotAvailable, CookiePathInvalid, CookiesInvalid, FailedToCreateConsentCookie):
        st.error("An error occurred while fetching the transcript. Please try another video.")
        st.stop()    
    except TranscriptsDisabled:
        st.error("Subtitles are disabled for this video. Please try another video.")
        st.stop()
    except NoTranscriptFound:
        st.error("The video doesn't have English subtitles. Please ensure the video you're selecting is in English or has English subtitles available.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}. Please try again.")
        st.stop()

def get_transcript_from_srt():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # Read the uploaded file into a string
        srt_string = uploaded_file.read().decode()

        # Parse the .srt file from the string
        subs = pysrt.from_string(srt_string)

        # Extract and combine the text from each subtitle
        text = ' '.join(sub.text for sub in subs)

        # Now 'text' contains all the subtitle texts combined
        return text
    
def process_srt_file(srt_file):
    # Read the uploaded file into a string
    srt_string = srt_file.read().decode('ISO-8859-1')

    # Decode HTML entities for a copy of srt_string
    srt_string_copy = html.unescape(srt_string)

    # Parse the .srt file from the string and its copy
    subs = pysrt.from_string(srt_string)
    subs_copy = pysrt.from_string(srt_string_copy)

    # Extract and combine the text from each subtitle and its copy
    text = ' '.join(sub.text for sub in subs)
    text_copy = ' '.join(sub.text for sub in subs_copy)

    # Use unidecode to remove non-ASCII characters for both text and its copy
    text = unidecode(text)
    text_copy = unidecode(text_copy)

    return text, text_copy




def download_youtube_video(youtube_link):
    """
    This function downloads a YouTube video.

    Parameters:
    youtube_link (str): The link to the YouTube video to download.

    Returns:
    str: The filename of the downloaded video, or None if the download failed.
    """
    try:
        # Create a YouTube object
        youtube = YouTube(youtube_link)

        # Download the first stream of the video and save it as 'temp_video'
        youtube.streams.first().download(filename="temp_video")

        # Return the filename of the downloaded video
        return "temp_video.mp4"
    except Exception as e:
        # Log any errors that occur during the download
        logging.error(f"Error downloading video: {e}")

        # Return None if the download failed
        return None

def convert_mp4_to_mp3(video_path):
    """
    This function converts an MP4 video file to an MP3 audio file.

    Parameters:
    video_path (str): The path to the MP4 video file to convert.

    Returns:
    str: The path to the converted MP3 file, or None if the conversion failed.
    """
    try:
        # Split the video path into name and extension
        name, _ = os.path.splitext(video_path)

        # Create the path for the MP3 file by replacing the extension with .mp3
        mp3_path = name + ".mp3"

        # Convert the MP4 file to MP3 and save it
        AudioSegment.from_file(video_path).export(mp3_path, format="mp3")

        # Return the path to the converted MP3 file
        return mp3_path
    except Exception as e:
        # Log any errors that occur during the conversion
        logging.error(f"Error converting to MP3: {e}")

        # Return None if the conversion failed
        return None