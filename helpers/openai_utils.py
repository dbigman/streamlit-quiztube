import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
import whisper
import openai


def get_quiz_data(text, openai_api_key):
    template = f"""
    You are a helpful assistant programmed to generate questions based on any text provided. For every chunk of text you receive, you're tasked with designing 10 distinct questions. Each of these questions will be accompanied by 4 possible answers: one correct answer and three incorrect ones. 

    For clarity and ease of processing, structure your response in a way that emulates a Python list of lists. 

    Your output should be shaped as follows:

    1. An outer list that contains 5 inner lists.
    2. Each inner list represents a set of question and answers, and contains exactly 4 strings in this order:
    - The generated question.
    - The correct answer.
    - The first incorrect answer.
    - The second incorrect answer.

    Your output should mirror this structure:
    [
        ["Generated Question 1", "Correct Answer 1", "Incorrect Answer 1.1", "Incorrect Answer 1.2", "Incorrect Answer 1.3"],
        ["Generated Question 2", "Correct Answer 2", "Incorrect Answer 2.1", "Incorrect Answer 2.2", "Incorrect Answer 2.3"],
        ...
    ]

    It is crucial that you adhere to this format as it's optimized for further Python processing.

    """
    try:
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        chain = LLMChain(
            llm=ChatOpenAI(openai_api_key=openai_api_key, 
            model = "gpt-4-1106-preview"), 
            prompt=chat_prompt           
        )
        return chain.run(text)
    except Exception as e:
        if "AuthenticationError" in str(e):
            st.error("Incorrect API key provided. Please check and update your API key.")
            st.stop()
        else:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

def transcribe_audio(audio_path):
    model = whisper.load_model("large")
    return model.transcribe(audio_path)



def correct_text(text, openai_api_key):
    template = f"""
    You are a helpful assistant programmed to make corrections in grammar and structure for text provided. For every chunk of text you receive, you will make the necessary corrections. 

    It is crucial that you adhere to this format as it's optimized for further Python processing.

    """
    try:
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_message_prompt = HumanMessagePromptTemplate.from_template("{text}")
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        chain = LLMChain(
            llm=ChatOpenAI(openai_api_key=openai_api_key, 
            model = "gpt-4-1106-preview"), 
            prompt=chat_prompt,
            max_tokens = 3000,
            # temperature = 0.1           
        )
        return chain.run(text)
    except Exception as e:
        if "AuthenticationError" in str(e):
            st.error("Incorrect API key provided. Please check and update your API key.")
            st.stop()
        else:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

