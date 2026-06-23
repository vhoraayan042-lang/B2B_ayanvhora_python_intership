
import streamlit as st
import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()  # load all the environment variables from the .env file
api_key=os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

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
                "correct": "correct choice option",
            },
            {
                "mcq": "multiple choice question",
                "options": {
                    "a": "choice here",
                    "b": "choice here",
                    "c": "choice here",
                    "d": "choice here",
                },
                "correct": "correct choice option",
            },
            {
                "mcq": "multiple choice question",
                "options": {
                    "a": "choice here",
                    "b": "choice here",
                    "c": "choice here",
                    "d": "choice here",
                },
                "correct": "correct choice option",
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

    formatted_template = PROMPT_TEMPLATE.format(
        text_content=text_content, quiz_level=quiz_level, RESPONSE_JSON=RESPONSE_JSON
    )

   # Make API request
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=formatted_template
        )
        response_text = response.text.strip()
    except Exception as e:
        st.error(f"API Error occurred: {e}")
        return []

    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "").replace("```", "").strip()
    elif response_text.startswith("```"):
        response_text = response_text.replace("```", "").strip()
        
    try:
        data = json.loads(response_text)
        return data.get("mcqs", [])
    except Exception as e:
        st.error("Failed to parse quiz data. Please try again.")
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

        # Display questions and radio buttons
        selected_options = []
        correct_answers = []
        for question in questions:
            options = list(question["options"].values())
            selected_option = st.radio(question["mcq"], options, index=None)
            selected_options.append(selected_option)
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