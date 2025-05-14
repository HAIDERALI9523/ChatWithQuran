import streamlit as st
from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from vanna.remote import VannaDefault
import logging
from grid_display import display_grid
import pandas as pd
import auth as auth
import re



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("streamlit_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Quran AI Assistant",
    page_icon="📚",
    layout="wide",  # Changed to wide layout
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed
)

# Custom CSS for better appearance
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f9f9f9;
        padding: 0 !important;
    }

    /* Header styling */
    .header-container {
        padding: 1rem 2rem;
        background-color: white;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
    }

    /* Chat container styling */
    .chat-container {
        max-width: 1000px;
        margin: 80px auto 120px auto;
        padding: 0 20px;
    }

    /* Message styling */
    .user-message {
        background-color: #e7f5ff;
        padding: 15px 20px;
        border-radius: 15px;
        margin: 10px 0;
        max-width: 85%;
        margin-left: auto;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    .assistant-message {
        background-color: white;
        padding: 15px 20px;
        border-radius: 15px;
        margin: 10px 0;
        max-width: 85%;
        margin-right: auto;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Styling for the response content */
    .response-content h1, .response-content h2, .response-content h3 {
        margin-top: 16px;
        margin-bottom: 8px;
        font-weight: bold;
    }

    .response-content h1 {
        font-size: 1.5em;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
    }

    .response-content h2 {
        font-size: 1.3em;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
    }

    .response-content h3 {
        font-size: 1.1em;
    }

    .response-content p {
        margin-bottom: 16px;
        line-height: 1.6;
    }

    .response-content ul, .response-content ol {
        margin-bottom: 16px;
        padding-left: 2em;
    }

    .response-content li {
        margin-bottom: 8px;
    }

    .response-content strong, .response-content b {
        font-weight: 600;
    }

    .response-content em, .response-content i {
        font-style: italic;
    }

    .response-content blockquote {
        padding: 0 1em;
        color: #6a737d;
        border-left: 0.25em solid #dfe2e5;
        margin-bottom: 16px;
    }

    /* Input container styling */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 1rem 2rem;
        border-top: 1px solid #e0e0e0;
        z-index: 1000;
    }

    .input-box {
        max-width: 1000px;
        margin: 0 auto;
    }

    /* Auth form styling */
    .auth-container {
        max-width: 500px;
        margin: 100px auto;
        padding: 30px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .auth-tabs {
        margin-bottom: 20px;
    }

    /* Button styling */
    .stButton>button {
        background-color: #50C878;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }

    /* Footer styling */
    .footer {
        text-align: center;
        padding: 10px;
        color: #666;
        font-size: 12px;
        position: fixed;
        bottom: 70px;
        left: 0;
        right: 0;
        background-color: #f9f9f9;
    }

    /* Grid Display Styling */
    .data-grid-container {
        margin: 20px 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .data-grid-header {
        background-color: #f0f7ff;
        padding: 15px;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .data-grid-title {
        font-weight: bold;
        font-size: 16px;
        color: #333;
    }

    .data-grid-search {
        margin: 10px 0;
    }

    .data-grid-search input {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }

    .data-grid-content {
        padding: 0;
        background-color: white;
        overflow-x: auto;
    }

    .data-grid-footer {
        padding: 15px;
        background-color: #f9f9f9;
        border-top: 1px solid #e0e0e0;
        display: flex;
        justify-content: flex-end;
    }

    .download-button {
        background-color: #50C878;
        color: white;
        border: none;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }

    /* Table styling */
    .data-grid-table {
        width: 100%;
        border-collapse: collapse;
    }

    .data-grid-table th {
        background-color: #f0f7ff;
        padding: 12px 15px;
        text-align: left;
        font-weight: bold;
        border-bottom: 1px solid #ddd;
        position: sticky;
        top: 0;
    }

    .data-grid-table td {
        padding: 10px 15px;
        border-bottom: 1px solid #eee;
    }

    .data-grid-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    .data-grid-table tr:hover {
        background-color: #f0f7ff;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .chat-container {
            margin: 70px auto 150px auto;
        }
        .user-message, .assistant-message {
            max-width: 90%;
        }
    }
</style>
""", unsafe_allow_html=True)

enhanced1 = f"""
        Answer the following question about the Quran within 1300 letters  with detailed references, please don't generate sql just give me detailed answered in text form using your own context with proper headings and i want conclusion of both 2-3 context:

        Please include relevant Surah and Ayat numbers when applicable, and provide context for your answer.
        Format your answer with markdown headings, bullet points, and bold text for important terms, please don't generate sql just give me detailed answere and top 2 context in text form using your own context with proper headings
        and i want conclusion of both 2-3 context within 1300 letters don't exceed 1300 and also give taferr of al_Jalalayn but don't exceed 1300 letters"""

# Uncomment Next 4 lines to run vanna locally with chatgpt
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# Initialize Vanna with your existing setup
@st.cache_resource
def initialize_vanna():
    logger.info("Starting Vanna setup process")

    # Uncomment Next 5 lines to run vanna using vanna api
    # api_key = 'e7c46615470b43d196aa1e2e8eece0a2'
    # vanna_model_name = 'chatwithquran'
    #
    # # Initialize Vanna
    # vn = VannaDefault(model=vanna_model_name, api_key=api_key)

    # Uncomment Next 1 line to run vanna locally with chatgpt api
    vn = MyVanna(config={'api_key': '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', 'model': 'gpt-4o-mini'})
    # Connect to SQLite database
    logger.info("Connecting to SQLite database")
    db_path = 'qurantranslation'
    vn.connect_to_sqlite(db_path)
    vn.allow_llm_to_see_data = True
    logger.info("Database connection established")
    # Comment to disable training
    # vn = train_vanna(vn)
    return vn

def train_vanna(vn):
    # Train with DDL
    logger.info("Training with DDL statements")
    vn.train(ddl="""
        CREATE TABLE qurantranslation (
            Name TEXT,
            Surah INTEGER,
            Ayat INTEGER,
            Arabic TEXT,
            Translation_Tahir_ul_Qadri TEXT,
            Translation_ArthurJ TEXT,
            Translation_Marmaduke_Pickthall TEXT,
            Tafaseer_al_Jalalayn TEXT,
            Tafaseer_Tanwir_al_Miqbas TEXT,
            EnglishTitle TEXT,
            ArabicTitle TEXT,
            RomanTitle TEXT,
            NumberOfVerses INTEGER,
            NumberOfRukus TEXT,
            PlaceOfRevelation TEXT,
            PRIMARY KEY (Surah, Ayat)
        );
    """)

    # Train with documentation if file exists
    try:
        logger.info("Adding business documentation")
        doc_file_path = 'Documentation1.txt'

        # Open file with UTF-8 encoding
        with open(doc_file_path, 'r', encoding='utf-8') as file:
            docs = file.read().split(',')

        for doc in docs:
            # Clean up the documentation string
            doc = doc.strip().strip('"').strip()
            if doc:  # Check if doc is not empty
                # Train the model
                vn.train(documentation=doc)
                logger.info(f"Trained with documentation: {doc[:50]}...")

        logger.info("Documentation training completed")
    except FileNotFoundError:
        logger.warning(f"Documentation file {doc_file_path} not found. Skipping documentation training.")

    # Train with example SQL
    logger.info("Training with example SQL query")
    vn.train(question = "What does quran says about word?", sql="""
    SELECT * FROM qurantranslation
    WHERE
        Translation_Tahir_ul_Qadri like '% word %' OR
        Translation_ArthurJ REGEXP like '% word %' OR
        Translation_Marmaduke_Pickthall like '% word %' OR
        Tafaseer_al_Jalalayn REGEXP like '% word %' OR
        Tafaseer_Tanwir_al_Miqbas like '% word %' ;
    """)
    vn.train(question="What are the number of surat and ayat in quran", sql="""
        SELECT 
            COUNT(DISTINCT surah) AS total_surahs,
            COUNT(*) AS total_ayats
        FROM qurantranslation;
        """)
    # Get final training data
    logger.info("Retrieving final training data")
    training_data = vn.get_training_data()
    logger.info("Setup complete - Vanna is ready to use")

    return vn

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'auth_message' not in st.session_state:
    st.session_state.auth_message = None
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = None

# Initialize Vanna
vanna_model = initialize_vanna()

# Initialize users file at startup
auth.initialize_users_file()
logger.info(f"Initialized users file: {auth.USERS_FILE}")


# Function to handle login
def login(username_or_email, password):
    logger.info(f"Login attempt for: {username_or_email}")
    success, message = auth.authenticate_user(username_or_email, password)
    logger.info(f"Login result: {success}, {message}")

    if success:
        # If login was with email, get the actual username
        if '@' in username_or_email:
            # Find the username for this email
            actual_username = None
            with open(auth.USERS_FILE, 'r') as file:
                for line in file:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split()
                    if len(parts) >= 3 and parts[2] == username_or_email:
                        actual_username = parts[0]
                        break

            if actual_username:
                st.session_state.username = actual_username
            else:
                # Fallback to using the email as username
                st.session_state.username = username_or_email
        else:
            st.session_state.username = username_or_email

        st.session_state.authenticated = True
        st.session_state.email = auth.get_user_email(st.session_state.username)
        st.session_state.auth_message = "Login successful!"
        st.session_state.auth_status = "success"
        return True
    else:
        st.session_state.auth_message = message
        st.session_state.auth_status = "error"
        return False


# Function to handle registration
def register(username, password, email):
    logger.info(f"Registration attempt for user: {username}")
    success, message = auth.register_user(username, password, email)
    logger.info(f"Registration result: {success}, {message}")

    if success:
        st.session_state.auth_message = "Registration successful! You can now login."
        st.session_state.auth_status = "success"
        return True
    else:
        st.session_state.auth_message = message
        st.session_state.auth_status = "error"
        return False


# Function to handle logout
def logout():
    logger.info(f"Logout for user: {st.session_state.username}")
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.email = None
    st.session_state.conversation = []
    st.session_state.auth_message = "You have been logged out."
    st.session_state.auth_status = "info"


# Function to extract response from error message
def extract_response_from_error(error_str):
    # Check if the error contains a response we can extract
    if "Couldn't run sql:" in error_str:
        # Extract the text between "Couldn't run sql:" and "': near"
        start_marker = "Couldn't run sql: "
        end_marker = "': near"

        start_idx = error_str.find(start_marker)
        if start_idx != -1:
            start_idx += len(start_marker)
            end_idx = error_str.find(end_marker, start_idx)

            if end_idx != -1:
                # Extract the actual response
                extracted_response = error_str[start_idx:end_idx].strip()
                return extracted_response

    # If we couldn't extract a response, return None
    return None


# Function to format markdown for better display
def format_markdown(text):
    if text is None:
        return "No response received."

    # Replace markdown headers with HTML headers
    text = re.sub(r'###\s+(.*)', r'<h3>\1</h3>', text)
    text = re.sub(r'##\s+(.*)', r'<h2>\1</h2>', text)
    text = re.sub(r'#\s+(.*)', r'<h1>\1</h1>', text)

    # Format bold text
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

    # Format italic text
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)

    # Format lists
    text = re.sub(r'^\d+\.\s+(.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\s+(.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)

    # Wrap paragraphs
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    for p in paragraphs:
        if not p.strip():
            continue
        if not (p.strip().startswith('<h') or p.strip().startswith('<li')):
            p = f'<p>{p}</p>'
        formatted_paragraphs.append(p)

    formatted_text = '\n'.join(formatted_paragraphs)

    # Replace newlines with <br> for line breaks within paragraphs
    formatted_text = formatted_text.replace('\n', '<br>')

    return formatted_text


# Function to ask a question
# Modify your ask_question function to return a DataFrame when appropriate
def ask_question(question, username):
    try:
        logger.info(f"Received question from {username}: {question}")
        # question = f'Please select all columns while generating SQL like :Select * from .... : Please answer this question for all context: {question}'

        # This will likely generate and execute SQL
        sql_results = vanna_model.generate_sql(question, allow_llm_to_see_data=True)
        # Clean invalid prefix if GPT adds it
        if sql_results.lower().startswith("intermediate_sql"):
            logger.warning("Removing invalid SQL prefix")
            sql_results = "\n".join(sql_results.splitlines()[1:])

        logger.info(f"Got SQL results")

        response = None  # Initialize response variable

        try:
            # Try to run the SQL and get DataFrame results
            response = vanna_model.run_sql(sql_results)
            if isinstance(response, pd.DataFrame):
                return response
            # If not a DataFrame, continue with text processing
        except Exception as sql_error:
            logger.error(f"SQL execution error: {str(sql_error)}")
            # Continue with text processing

        # Try to get a formatted response
        try:
            formatted_response = vanna_model.generate_sql(response if response is not None else question, allow_llm_to_see_data=True)
            return formatted_response
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error: {error_str}")

            # Extract response from error if possible
            if "Couldn't run sql:" in error_str:
                # This means Vanna tried to execute the response as SQL but it was text
                start_marker = "Couldn't run sql:  Execution failed on sql '"
                end_marker = "': unrecognized token"

                start_idx = error_str.find(start_marker)
                if start_idx != -1:
                    start_idx += len(start_marker)
                    end_idx = error_str.find(end_marker, start_idx)

                    if end_idx != -1:
                        extracted_response = error_str[start_idx:end_idx].strip()
                        return extracted_response

            return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return f"Error: {str(e)}"


# Display authentication message if exists
if st.session_state.auth_message:
    if st.session_state.auth_status == "success":
        st.success(st.session_state.auth_message)
    elif st.session_state.auth_status == "error":
        st.error(st.session_state.auth_message)
    else:
        st.info(st.session_state.auth_message)

    # Clear message after display
    st.session_state.auth_message = None
    st.session_state.auth_status = None

# Main app logic
if not st.session_state.authenticated:
    # Display login/register form with better styling
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.title("Welcome to Quran AI Assistant")
    st.markdown("Please login or register to continue.")

    # Create tabs for login and register
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        login_identifier = st.text_input("Username or Email", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        st.info("Use your username (e.g., 'haider'), not your email")
        login_button = st.button("Login", key="login_button", use_container_width=True)

        if login_button:
            if not login_identifier or not login_password:
                st.error("Please enter both username/email and password.")
                logger.warning("Login attempt with empty fields")
            else:
                login(login_identifier, login_password)
                st.rerun()

    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        register_button = st.button("Register", key="register_button", use_container_width=True)

        if register_button:
            if not reg_username or not reg_email or not reg_password or not reg_confirm_password:
                st.error("Please fill in all fields.")
                logger.warning("Registration attempt with empty fields")
            elif reg_password != reg_confirm_password:
                st.error("Passwords do not match.")
                logger.warning("Registration attempt with mismatched passwords")
            else:
                if register(reg_username, reg_password, reg_email):
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
else:
    # User is authenticated, show the chat interface

    # Header with user info and logout button
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Quran AI Assistant")
    with col2:
        st.markdown(f"<div style='text-align: right;'>Welcome, <b>{st.session_state.username}</b>!</div>",
                    unsafe_allow_html=True)
        if st.button("Logout", key="logout_button"):
            logout()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat container for messages
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Welcome message if no conversation yet
    if not st.session_state.conversation:
        st.markdown("""
            <div class="assistant-message">
                <p><b>Quran AI Assistant:</b></p>
                <div class="response-content">
                    <p>Welcome to the Quran AI Assistant! I'm here to help answer your questions about the Quran's teachings, stories, and guidance. What would you like to know?</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Display conversation history
        for exchange in st.session_state.conversation:
            # User message
            st.markdown(f"""
                <div class="user-message">
                    <p><b>You:</b> {exchange["question"]}</p>
                </div>
                """, unsafe_allow_html=True)

            # Assistant message start
            st.markdown(f"""
                <div class="assistant-message">
                    <p><b>Quran AI Assistant:</b></p>
                    <div class="response-content">
                """, unsafe_allow_html=True)

            # Check if the answer is still loading
            if isinstance(exchange["answer"], str) and exchange["answer"] == "Thinking...":
                st.markdown("Thinking...", unsafe_allow_html=True)
            else:
                try:
                    # Try to convert to DataFrame and display as grid
                    if isinstance(exchange["answer"], pd.DataFrame):
                        display_grid(exchange["answer"])
                    elif isinstance(exchange["answer"], str) and (
                            '|' in exchange["answer"] and '\n' in exchange["answer"]):
                        # This looks like a table, try to display as grid
                        display_grid(exchange["answer"])
                    else:
                        # Display as formatted text
                        answer = exchange["answer"]
                        if isinstance(answer, pd.DataFrame):
                            formatted_answer = format_markdown(
                                answer.to_string()) if not answer.empty else "No response received."
                        elif isinstance(answer, str):
                            formatted_answer = format_markdown(answer) if answer.strip() else "No response received."
                        else:
                            formatted_answer = "No response received."

                        st.markdown(formatted_answer, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error displaying response: {str(e)}")
                    formatted_answer = format_markdown(str(exchange["answer"])) if exchange[
                        "answer"] else "No response received."
                    st.markdown(formatted_answer, unsafe_allow_html=True)

            # Close the assistant message div
            st.markdown("""
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Close chat container
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown('<div class="footer">Powered by Vanna AI | Quran Knowledge Assistant</div>', unsafe_allow_html=True)

    # Input container at the bottom
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<div class="input-box">', unsafe_allow_html=True)

    # Create a form for the chat input
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            question = st.text_area("Ask a question about the Quran",
                                    placeholder="Example: What does the Quran say about kindness?",
                                    label_visibility="collapsed",
                                    height=80)
        with col2:
            submit_button = st.form_submit_button("Send", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Process the question when the button is clicked
    if submit_button and question:
        # Add user question to conversation immediately
        st.session_state.conversation.append({
            "question": question,
            "answer": "Thinking..."
        })
        st.rerun()  # Rerun to show the question immediately

    # Check if we need to update a "Thinking..." message
    if (st.session_state.conversation and
            isinstance(st.session_state.conversation[-1]["answer"], str) and
            st.session_state.conversation[-1]["answer"] == "Thinking..."):
        with st.spinner(""):
            try:
                # Get answer from Vanna
                answer = ask_question(st.session_state.conversation[-1]["question"], st.session_state.username)

                # Update the last conversation entry with the real answer
                st.session_state.conversation[-1]["answer"] = answer

                # Rerun to display the answer
                st.rerun()
            except Exception as e:
                # Update with error message
                st.session_state.conversation[-1]["answer"] = f"Error: {str(e)}"
                st.rerun()

