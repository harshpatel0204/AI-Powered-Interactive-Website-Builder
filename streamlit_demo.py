import re
import time

import streamlit as st
from openai import OpenAI

from config.settings import settings

# Configuration
GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_BASE_URL = settings.GEMINI_BASE_URL
GEMINI_MODEL = settings.GEMINI_MODEL


# Load system prompt from external text file
def load_system_prompt():
    try:
        with open("prompt/website_builder_prompt.txt", "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error loading system prompt: {str(e)}"


# Loaded system prompt
SYSTEM_PROMPT = load_system_prompt()

# Questions
questions = [
    "Hi there! Let's begin setting up your website. Could you tell me what your site will be about?",
    "That sounds exciting! What's the name of your store?",
    "Lovely name! What kinds of products are you planning to offer?",
    "Great selection! What are your key goals for this e-commerce store? (For example: driving more traffic, building brand awareness, starting a newsletter, etc.)",
    "Impressive ambitions! What's your unique selling proposition that makes your store stand out from the rest?",
    "Wonderful! Could you share a little about the background or story behind your business?",
]

# Initialize session state
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "completed" not in st.session_state:
    st.session_state.completed = False
if "generated_html" not in st.session_state:
    st.session_state.generated_html = ""
if "website_generated" not in st.session_state:
    st.session_state.website_generated = False
if "update_chat_history" not in st.session_state:
    st.session_state.update_chat_history = []


def generate_website_summary():
    """Generate website summary using the API"""
    try:
        formatted_prompt = SYSTEM_PROMPT.format(
            answer1=(st.session_state.answers[0]),
            answer2=(st.session_state.answers[1]),
            answer3=(st.session_state.answers[2]),
            answer4=(st.session_state.answers[3]),
            answer5=(st.session_state.answers[4]),
            answer6=(st.session_state.answers[5]),
        )

        print("Formatted Prompt:", formatted_prompt)

        with open("summary/formatted_prompt.txt", "w", encoding="utf-8") as f:
            f.write(formatted_prompt)

        client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url=GEMINI_BASE_URL,
        )

        response = client.chat.completions.create(
            model=GEMINI_MODEL, messages=[{"role": "user", "content": formatted_prompt}]
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def update_website(update_request, current_html):
    """Update the website based on user request"""
    try:
        update_prompt = f"""
        You are a web developer assistant. The user has a website and wants to make some changes to it.
        
        Current HTML code:
        {current_html}
        
        User's update request:
        {update_request}
        
        Please provide the updated HTML code with the requested changes. Make sure to:
        1. Keep the existing structure intact where possible
        2. Apply the requested changes accurately
        3. Maintain proper HTML formatting
        4. Ensure the code is complete and functional
        
        Return only the complete HTML code without any additional explanation.
        """

        client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url=GEMINI_BASE_URL,
        )

        response = client.chat.completions.create(
            model=GEMINI_MODEL, messages=[{"role": "user", "content": update_prompt}]
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error updating website: {str(e)}"


def reset_chat():
    """Reset the chat"""
    st.session_state.current_question = 0
    st.session_state.answers = []
    st.session_state.chat_history = []
    st.session_state.completed = False
    st.session_state.generated_html = ""
    st.session_state.website_generated = False
    st.session_state.update_chat_history = []


# Streamlit App UI
st.title("🏪 Website Builder Assistant")
st.markdown("Let's build your website step by step!")

# Sidebar
with st.sidebar:
    st.header("Progress")
    if not st.session_state.website_generated:
        progress = len(st.session_state.answers) / len(questions)
        st.progress(progress)
        st.write(
            f"Questions answered: {len(st.session_state.answers)}/{len(questions)}"
        )
    else:
        st.success("✅ Website Generated!")
        st.write("You can now update your website using the chat below.")

    if st.button("🔄 Start Over"):
        reset_chat()
        st.rerun()

# Main content
if not st.session_state.website_generated:
    # Initial chat interface for questions
    st.subheader("Chat")

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(message["content"])
                time.sleep(0.3)
        else:
            with st.chat_message("user"):
                st.write(message["content"])

    # Handle current state
    if not st.session_state.completed:
        if st.session_state.current_question < len(questions):
            current_q = questions[st.session_state.current_question]

            if (
                not st.session_state.chat_history
                or st.session_state.chat_history[-1]["content"] != current_q
            ):
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": current_q}
                )
                with st.chat_message("assistant"):
                    st.write(current_q)

            # if user_input := st.chat_input("Type your answer here..."):
            user_input = st.chat_input("Type your answer here...")
            if user_input:
                st.session_state.chat_history.append(
                    {"role": "user", "content": user_input}
                )
                st.session_state.answers.append(user_input)
                st.session_state.current_question += 1

                if st.session_state.current_question >= len(questions):
                    st.session_state.completed = True
                    completion_msg = "Thank you for answering all the questions! 🎉 Now I can generate your website summary."
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": completion_msg}
                    )

                st.rerun()

    else:
        # with st.chat_message("assistant"):
        #     st.write(
        #         "Thank you for answering all the questions! 🎉 Now I can generate your website summary."
        #     )

        if st.button("🚀 Generate Website Summary", type="primary"):
            with st.spinner("Generating your website summary..."):
                summary = generate_website_summary()
                print("Generated Summary:", summary)

                with open("summary/generated_summary.txt", "w", encoding="utf-8") as f:
                    f.write(summary)

                # Extract HTML from summary
                html_match = re.search(
                    r"<html.*?>.*?</html>", summary, re.DOTALL | re.IGNORECASE
                )

                if html_match:
                    st.session_state.generated_html = html_match.group(0)
                    st.session_state.website_generated = True
                    st.rerun()
                else:
                    st.error("No HTML code found in the generated summary.")

else:
    # Website generated - show preview and update interface
    st.subheader("🎨 Your Generated Website")

    # Create tabs for preview and updates
    tab1, tab2, tab3 = st.tabs(["🖥️ Preview", "💬 Update Website", "📋 HTML Code"])

    with tab1:
        st.markdown("### Live Preview")
        try:
            st.components.v1.html(
                st.session_state.generated_html, height=800, scrolling=True
            )
        except Exception as e:
            st.error(f"Error rendering HTML: {str(e)}")

    with tab2:
        st.markdown("### Update Your Website")
        st.write("Ask me to make changes to your website! For example:")
        st.info(
            """
        • "Change the background color to blue"
        • "Add a contact form"
        • "Make the header bigger"
        • "Add more product images"
        • "Change the font style"
        """
        )

        # Display update chat history
        for message in st.session_state.update_chat_history:
            if message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.write(message["content"])
            else:
                with st.chat_message("user"):
                    st.write(message["content"])

        # Update chat input
        if update_request := st.chat_input(
            "What would you like to change about your website?"
        ):
            print("Update Request:", update_request)
            # Add user message to chat
            st.session_state.update_chat_history.append(
                {"role": "user", "content": update_request}
            )

            with st.chat_message("user"):
                st.write(update_request)

            # Show spinner and update website
            with st.spinner("Updating your website..."):
                updated_response = update_website(
                    update_request, st.session_state.generated_html
                )

                # Extract HTML from the response
                html_match = re.search(
                    r"<html.*?>.*?</html>", updated_response, re.DOTALL | re.IGNORECASE
                )

                if html_match:
                    st.session_state.generated_html = html_match.group(0)
                    assistant_message = "✅ Website updated successfully! Check the Preview tab to see the changes."
                else:
                    assistant_message = "⚠️ I made some changes but couldn't extract clean HTML. Please check the HTML Code tab."

                # Add assistant response to chat
                st.session_state.update_chat_history.append(
                    {"role": "assistant", "content": assistant_message}
                )

                with st.chat_message("assistant"):
                    st.write(assistant_message)

            st.rerun()

    with tab3:
        st.markdown("### HTML Source Code")
        st.code(st.session_state.generated_html, language="html")
        st.download_button(
            label="📥 Download HTML File",
            data=st.session_state.generated_html,
            file_name="generated_website.html",
            mime="text/html",
        )

    # Show answers in expandable section
    with st.expander("📋 View All Your Answers"):
        for i, (question, answer) in enumerate(
            zip(questions, st.session_state.answers)
        ):
            st.write(f"**Q{i+1}:** {question}")
            st.write(f"**A{i+1}:** {answer}")
            st.divider()
