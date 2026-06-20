
import streamlit as st
import json
import os
from dotenv import load_dotenv

# from dotenv import API_KEY
load_dotenv()  # load all the environment variables from the .env file

from openai import OpenAI
OpenAI.api_key=os.getenv("OPENAI_API_KEY")
client = OpenAI()

@st.cache_data
def fetch_questions(text_content, quiz_level):

    RESPONSE_JSON = {
        "mcqs": [
            {
                "mcq": "multiple choice question1",
                "options": {
                    "a": "choice here1",
                    "b": "choice here2",
                    "c": "choice here3",
                    "d": "choice here4",
                },
                "correct": "a", 
            },
            {
                "mcq": "multiple choice question",
                "options": {
                    "a": "choice here",
                    "b": "choice here",
                    "c": "choice here",
                    "d": "choice here",
                },
                "correct": "b",
            },
            {
                "mcq": "multiple choice question",
                "options": {
                    "a": "choice here",
                    "b": "choice here",
                    "c": "choice here",
                    "d": "choice here",
                },
                "correct": "c",
            },
        ]
    }

    PROMPT_TEMPLATE = """
    Text: {text_content}
    You are an expert in generating MCQ type quiz on the basis of provided content.
    Given the above text, create a quiz of 3 multiple choice questions keeping difficulty level as {quiz_level}.
    Make sure the questions are not repeated and check all the questions to be conforming the text as well.
    Make sure to format your response like RESPONSE_JSON below and use it as a guide.
    Ensure to make an array of 3 MCQs referring the following response json.
    Here is the RESPONSE_JSON:

    {RESPONSE_JSON}
    """

    # json.dumps converts the dictionary into a proper double-quoted JSON string
    formatted_template = PROMPT_TEMPLATE.format(
        text_content=text_content, 
        quiz_level=quiz_level, 
        RESPONSE_JSON=json.dumps(RESPONSE_JSON)
    )

   # Make API request
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "user", "content": formatted_template}
            ]
        )
        
        # Extract response JSON
        extracted_response = response.choices[0].message.content
        print(extracted_response)
        
        return json.loads(extracted_response).get("mcqs", [])
        
    except Exception as e:
        print(f"Error occurred: {e}")
        # Return an empty list if there's an API or JSON error
        return []

def main():

    st.title("Quiz Generator App")

    # Text input for user to enter content
    text_content = st.text_area("paste the text content here:")

    # dropdown for selecting quiz level
    quiz_level = st.selectbox("select quiz level:", ["easy", "medium", "hard"])

    # Convert quiz level to lower casing
    quiz_level_lower = quiz_level.lower()
    
    # Initialize session_state
    session_state = st.session_state
    
    # Check if quiz_generated flag exists in session_state, if not initialize it
    if 'quiz_generated' not in session_state:
        session_state.quiz_generated = False
        
    # Track if Generate Quiz button is clicked
    if not session_state.quiz_generated:
        session_state.quiz_generated = st.button("Generate Quiz")

    if session_state.quiz_generated:
        # Define Questions and options
        questions = fetch_questions(text_content=text_content, quiz_level=quiz_level_lower)

        # Safety check in case the API returned an empty list due to an error
        if not questions:
            st.error("Could not generate questions. Please check your API key or try a different text.")
            return

        # Display questions and radio buttons
        selected_options = []
        correct_answers = []
        for question in questions:
            options = list(question["options"].values())
            selected_option = st.radio(question["mcq"], options, index=None)
            selected_options.append(selected_option)
            # Find the correct answer text based on the 'correct' key (a, b, c, or d)
            correct_answers.append(question["options"][question["correct"]])

        # Submit button
        if st.button("Submit"):
            # Display selected options
            marks = 0
            st.header("Quiz Result:")
            for i, question in enumerate(questions):
                    selected_option = selected_options[i]
                    correct_option = correct_answers[i]
                    st.subheader(f"{question['mcq']}")
                    st.write(f"You selected: {selected_option}")
                    st.write(f"Correct answer: {correct_option}")
                    if selected_option == correct_option:
                        marks += 1
            st.subheader(f"You scored {marks} out of {len(questions)}")

if __name__ == "__main__":
    main()