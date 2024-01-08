import streamlit as st
from helpers.youtube_utils import extract_video_id_from_url, get_transcript_text
from helpers.openai_utils import get_quiz_data
from helpers.openai_utils import correct_text
from helpers.quiz_utils import string_to_list, get_randomized_options
from helpers.toast_messages import get_random_toast
from helpers.youtube_utils import process_srt_file
import os
import dotenv

from unidecode import unidecode
import html

st.set_page_config(
    page_title="Video Quizzer",
    page_icon=":factory:",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Check if user is new or returning using session state.
# If user is new, show the toast message.
if 'first_time' not in st.session_state:
    message, icon = get_random_toast()
    st.toast(message, icon=icon)
    st.session_state.first_time = False

with st.sidebar:
    st.header("Project Info")
    st.write("""
    I am adapting code from **Sven Bosau** to create a quiz from a video transcript.

    
    """)

    st.divider()
    st.subheader("🔗 Links", anchor=False)
    st.markdown(
        """
        Markdown links here
    
        """

    )

    st.divider()
    st.subheader("Sidebar Section 1", anchor=False)
    # st.write("QuizTube proudly stands as Sven's innovative entry for the Streamlit Hackathon held in September 2023. A testament to the power of imagination and code!")
    st.write(" ")

    st.divider()
    # st.write("Made with ♥ in Dresden, Germany")
    st.write("Sidebar Section 2")


#------------------------
#-     Main Page        -
#------------------------

st.title(":red[Video Transcriber and Quizzer] — Watch. Learn. Quiz.", anchor=False)
st.write("""
Ever watched a video and wondered how well you understood its content? Here's a fun twist: Instead of just watching the video, come here and test your comprehension!

**How does it work?** 
1. Upload the transcription file (.srt).


Once you've uploaded, voilà! Dive deep into questions crafted just for you, ensuring you've truly grasped the content of the video. Let's put your knowledge to the test! 
""")

# This is neat, but I don't need it for this project
# with st.expander("💡 Video Tutorial"):
#     with st.spinner("Loading video.."):
#         st.video("https://youtu.be/yzBr3L2BIto", format="video/mp4", start_time=0)


with st.form("user_input"):
    # YOUTUBE_URL = st.text_input("Enter the YouTube video link:", placeholder="https://youtu.be/bcYwiwsDfGE?si=qQ0nvkmKkzHJom2y")
    # OPENAI_API_KEY = st.text_input("Enter your OpenAI API Key:", placeholder="sk-XXXX", type='password')
    
    # Don't need to ask for the API key, as it will be in the .env file
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  
    
    # Initialize submitted to False
    submitted = False
    
    # Getting the transcript from a .srt file
    st.markdown("### Upload an .srt file")
    srt_file = st.file_uploader("", type=['srt'])
    if srt_file is not None:
        # Check if the uploaded file has the correct extension
        if not srt_file.name.endswith('.srt'):
            st.error("Invalid file type. Please upload a .srt file.")
        else:          
            text, text_copy = process_srt_file(srt_file)
            # Display copy of the text. 
            # st.text_area("Transcript", text_copy, height=200)
            # Make another text area for the corrected text
            corrected_text = correct_text(text_copy, OPENAI_API_KEY )
            st.text_area("Corrected Transcript", corrected_text, height=300)

    submitted = st.form_submit_button("Craft my quiz!")


if submitted or ('quiz_data_list' in st.session_state):
    #if not YOUTUBE_URL:
    #    st.info("Please provide a valid YouTube video link. Head over to [YouTube](https://www.youtube.com/) to fetch one.")
     #   st.stop()
    #elif not OPENAI_API_KEY:
    #    st.info("Please fill out the OpenAI API Key to proceed. If you don't have one, you can obtain it [here](https://platform.openai.com/account/api-keys).")
    #    st.stop()
        
    with st.spinner("Crafting your quiz..."):
        if submitted:
            # video_id = extract_video_id_from_url(YOUTUBE_URL)
            # video_transcription = get_transcript_text(video_id)
            video_transcription = text
            quiz_data_str = get_quiz_data(video_transcription, OPENAI_API_KEY)
            st.session_state.quiz_data_list = string_to_list(quiz_data_str)

            if 'user_answers' not in st.session_state:
                st.session_state.user_answers = [None for _ in st.session_state.quiz_data_list]
            if 'correct_answers' not in st.session_state:
                st.session_state.correct_answers = []
            if 'randomized_options' not in st.session_state:
                st.session_state.randomized_options = []

            for q in st.session_state.quiz_data_list:
                options, correct_answer = get_randomized_options(q[1:])
                st.session_state.randomized_options.append(options)
                st.session_state.correct_answers.append(correct_answer)

        with st.form(key='quiz_form'):
            # st.subheader("Quiz Time: Test Your Knowledge!", anchor=False)
            st.subheader("Quiz Time: Test Your Knowledge!")
            for i, q in enumerate(st.session_state.quiz_data_list):
                options = st.session_state.randomized_options[i]
                default_index = st.session_state.user_answers[i] if st.session_state.user_answers[i] is not None else 0
                response = st.radio(q[0], options, index=default_index)
                user_choice_index = options.index(response)
                st.session_state.user_answers[i] = user_choice_index  # Update the stored answer right after fetching it


            results_submitted = st.form_submit_button(label='Unveil My Score!')

            if results_submitted:
                score = sum([ua == st.session_state.randomized_options[i].index(ca) for i, (ua, ca) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers))])
                st.success(f"Your score: {score}/{len(st.session_state.quiz_data_list)}")

                if score == len(st.session_state.quiz_data_list):  # Check if all answers are correct
                    st.balloons()
                else:
                    incorrect_count = len(st.session_state.quiz_data_list) - score
                    if incorrect_count == 1:
                        st.warning(f"Almost perfect! You got 1 question wrong. Let's review it:")
                    else:
                        st.warning(f"Almost there! You got {incorrect_count} questions wrong. Let's review them:")

                for i, (ua, ca, q, ro) in enumerate(zip(st.session_state.user_answers, st.session_state.correct_answers, st.session_state.quiz_data_list, st.session_state.randomized_options)):
                    with st.expander(f"Question {i + 1}", expanded=False):
                        if ro[ua] != ca:
                            st.info(f"Question: {q[0]}")
                            st.error(f"Your answer: {ro[ua]}")
                            st.success(f"Correct answer: {ca}")