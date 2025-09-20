import json
import re
from groq import Groq

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from .youtube import get_youtube_courses
from django.conf import settings

# --- Initialization ---
client = Groq(api_key=settings.GROQ_API_KEY)

# Switched to Hugging Face Embeddings for Deployment.
# This model is self-contained and doesn't require an external service like Ollama.
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'} # Use CPU for broad compatibility
)


# --- Resume Processing Function ---
def process_resume(file_path: str):
    """
    Reads a resume file (PDF), splits it into chunks, and creates a searchable
    vector store (a smart index) of its content.
    """
    if not file_path:
        return None
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        text = " ".join([page.page_content for page in pages])
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        
        # Create the smart index from the resume chunks
        vector_store = FAISS.from_texts(chunks, embedding=embeddings)
        print(f"Successfully processed resume: {file_path}")
        return vector_store
    except Exception as e:
        print(f"Error processing resume file: {e}")
        return None

# --- Main AI Function (Uses Groq) ---
def chat_with_ai(context: dict, message: str, history: str):
    """
    Generates an AI response using the Groq API.
    """
    resume_context = "No resume has been provided for this session yet."

    if context.get("resume_path"):
        vector_store = process_resume(context["resume_path"])
        if vector_store:
            # Find relevant text in the resume based on the current message
            relevant_chunks = vector_store.similarity_search(message, k=2)
            resume_context = " ".join([chunk.page_content for chunk in relevant_chunks])
            print("Found relevant resume context.")

    # Construct the prompt for the Groq API
    prompt = f"""
    You are an expert career counselor AI named Marvin. Your goal is to have a natural, multi-step conversation.

    **Conversation Rules:**
    1.  **Phase 1: Rapport Building (First 2 AI messages).** Your first message is a warm welcome. Your second message should be an open-ended question to make the user comfortable.
    2.  **Phase 2: Conditional Logic (AI's 3rd message).**
        - IF the user's status is 'school_student', continue the conversation naturally.
        - IF the user's status is 'college_student' or 'passout', politely ask them to attach their resume.
    3.  **Phase 3: Counseling.**
        - For school students, analyze their concerns and provide guidance.
        - For college/passout, once they provide a resume, analyze it and begin counseling.

    **User's Background Information:**
    - Name: {context.get("name", "the user")}
    - Status: {context.get("status", "N/A")}
    - Age: {context.get("age", "N/A")}
    - **Resume Context:** {resume_context}

    **Conversation History:**
    {history}

    The user just sent this message: "{message}"

    ---
    **IMPORTANT INSTRUCTION:** Your final output must ONLY be the words the counselor would say. Do not add any notes, explanations, or mention your internal rules or phases.

    Your next response as the AI Counselor:
    """

    # Groq API call for fast text generation
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
        max_tokens=1000,
        temperature=0.7
    )

    return chat_completion.choices[0].message.content


# --- Roadmap Generation (Uses Groq) ---
def generate_career_roadmap(session, history_text):
    """
    Generates a career roadmap using the Groq API.
    """
    resume_context = "No resume provided for this session."
    if session.resume_file and hasattr(session.resume_file, 'path'):
        vector_store = process_resume(session.resume_file.path)
        if vector_store:
            # Find relevant text in the resume based on the entire conversation
            relevant_chunks = vector_store.similarity_search(history_text, k=3)
            resume_context = " ".join([chunk.page_content for chunk in relevant_chunks])

    if session.status == 'school_student':
        prompt = f"""
        You are a JSON generation assistant. Analyze the following conversation and generate a JSON object.
        Conversation:
        ---
        {history_text}
        ---
        TASK: Based on the conversation, suggest 3 academic fields for the student.
        You MUST respond with ONLY a single, valid JSON object.
        The JSON object must have a key "roadmap" which contains a list of 3 objects.
        Each object MUST have these exact keys: "title" (string), "skills" (list of strings), "reasoning" (string).
        DO NOT add any text before or after the JSON object.
        """
    else:  # For college students and professionals
        prompt = f"""
        Analyze the conversation and resume context.
        Chat History: {history_text}
        Resume Context: {resume_context}

        TASK: Based on this information, suggest 3 detailed career pathways.
        You MUST format your response as a single, valid JSON object.
        The object must have one key "roadmap", a list of 3 pathway objects.
        Each object must have these exact keys: "title", "skills", "courses_to_find", "salary", "growth", "reasoning".
        - The "courses_to_find" value MUST be a list of 2-3 strings.
        - Each string MUST be a specific, searchable skill or course name (e.g., "User Interface Design", "UX Research Methods").
        """

    # Groq API call for structured JSON generation
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
        max_tokens=1500,
        temperature=0.3
    )

    try:
        llm_output_text = chat_completion.choices[0].message.content.strip()
        print("--- LLM Roadmap Response ---")
        print(llm_output_text)
        print("--------------------------")

        data = None
        # Enhanced regex to find JSON within triple backticks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', llm_output_text, re.DOTALL)

        if json_match:
            json_string = json_match.group(1)
            data = json.loads(json_string)
        elif llm_output_text.startswith('{') and llm_output_text.endswith('}'):
            # Fallback for when the model returns a raw JSON object
            data = json.loads(llm_output_text)
        else:
            raise ValueError("Could not find or parse a valid JSON object in the AI's response.")

        if session.status != 'school_student' and 'roadmap' in data:
            for pathway in data['roadmap']:
                verified_courses = []
                if 'courses_to_find' in pathway:
                    for skill_to_find in pathway['courses_to_find']:
                        courses = get_youtube_courses(skill_to_find, max_results=1)
                        if courses:
                            verified_courses.append(courses[0])
                pathway['courses'] = verified_courses
                del pathway['courses_to_find']

        return data

    except (json.JSONDecodeError, TypeError, KeyError, ValueError) as e:
        print(f"Error processing roadmap: {e}")
        return {"error": "Failed to decode or process the roadmap from AI response."}