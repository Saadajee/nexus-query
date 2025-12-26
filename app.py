import streamlit as st
from groq import Groq
import requests
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    RequestBlocked,
    IpBlocked,
    VideoUnplayable,
    AgeRestricted,
)

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Nexus Query",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    :root {
        --bg-primary: #0f0f0f;
        --bg-secondary: #1f1f1f;
        --accent-red: #ff0000;
        --accent-light: #ff3333;
        --text-primary: #ffffff;
        --text-secondary: #aaaaaa;
        --border: #333333;
        --input-bg: #212121;
    }
    
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Roboto', sans-serif;
    }
    
    .header {
        text-align: center;
        padding: 2rem 0 1.5rem;
    }
    
    .header img {
        height: 60px;
        margin-bottom: 0.5rem;
    }
    
    .header h1 {
        color: var(--accent-red);
        font-size: 2.8rem;
        margin: 0;
        letter-spacing: 1px;
    }
    
    .subtitle {
        color: var(--text-secondary);
        font-size: 1.2rem;
        margin: 0.5rem 0 2rem;
    }
    
    .search-container {
        max-width: 800px;
        margin: 0 auto 2rem;
        padding: 0 1rem;
    }
    
    .search-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        background-color: var(--input-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.75rem 1rem;
    }
    
    .search-input {
        flex: 1;
        background: transparent;
        border: none;
        color: var(--text-primary);
        font-size: 1.1rem;
        outline: none;
    }
    
    .search-input::placeholder {
        color: var(--text-secondary);
    }
    
    .search-button button {
        background-color: var(--accent-red) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        width: 100%;
    }
    
    .search-button button:hover {
        background-color: var(--accent-light) !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }
    
    .stChatMessage {
        background-color: var(--bg-secondary);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.75rem 0;
        border-left: 5px solid var(--accent-red);
    }
    
    section[data-testid="stChatInput"] {
        display: none !important;
    }
    
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-red), transparent);
        opacity: 0.6;
        margin: 2rem 0;
    }
    
    .stCaption {
        color: var(--text-secondary);
        text-align: center;
        font-size: 0.9rem;
    }
    
    a {
        color: var(--accent-light);
        text-decoration: none;
    }
    
    a:hover {
        color: #ff6666;
        text-decoration: underline;
    }
    
    @media (max-width: 768px) {
        .header h1 {font-size: 2.2rem;}
        .search-row {flex-direction: column;}
        .search-button {width: 100%;}
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_groq_client():
    # Load API keys from secrets and return clients
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        serpapi_key = st.secrets["SERPAPI_KEY"]
        return {"groq": Groq(api_key=api_key), "serpapi": serpapi_key}
    except Exception:
        st.error("Missing API keys. Add GROQ_API_KEY and SERPAPI_KEY to .streamlit/secrets.toml")
        st.stop()

def search_youtube_video(query, num_results=5):
    # Search YouTube using SerpApi and return list of video details
    params = {
        "engine": "youtube",
        "search_query": query,
        "api_key": st.session_state.clients["serpapi"],
        "gl": "us",
        "hl": "en"
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        videos = []
        if "video_results" in data:
            for item in data["video_results"][:num_results]:
                videos.append({
                    "title": item.get("title", "Untitled"),
                    "link": item.get("link"),
                    "channel": item.get("channel", {}).get("name", "Unknown"),
                    "duration": item.get("length", "Unknown") or item.get("duration", "Unknown")
                })
        return videos
    except Exception:
        return []

def get_youtube_transcript(video_url):
    # Extract video ID and fetch transcript using youtube_transcript_api
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]
        ytt = YouTubeTranscriptApi()
        try:
            transcript = ytt.fetch(video_id, languages=['en'])
            full_text = " ".join([snippet.text for snippet in transcript.snippets])
            return full_text, None
        except NoTranscriptFound:
            pass
        transcript_list = ytt.list(video_id)
        if len(transcript_list) == 0:
            return None, "No transcript available in any language."
        first_transcript = next(iter(transcript_list))
        transcript_data = first_transcript.fetch()
        full_text = " ".join([snippet.text for snippet in transcript_data.snippets])
        return full_text, None
    except TranscriptsDisabled:
        return None, "Transcripts are disabled for this video."
    except NoTranscriptFound:
        return None, "No transcript found (auto-captions may not be generated yet)."
    except RequestBlocked:
        return None, "Request blocked by YouTube (possible IP issue)."
    except IpBlocked:
        return None, "IP blocked by YouTube."
    except AgeRestricted:
        return None, "Video is age-restricted and requires authentication."
    except VideoUnplayable:
        return None, "Video is unplayable."
    except Exception as e:
        return None, f"Transcript error: {str(e)}"

# Apply custom styling
inject_custom_css()

# Header section
st.markdown("""
<div class="header">
    <img src="https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png" alt="YouTube Logo">
    <h1>Nexus Query</h1>
    <p class="subtitle">AI Video Search & Transcription Agent</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state variables
if "clients" not in st.session_state:
    st.session_state.clients = get_groq_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_video" not in st.session_state:
    st.session_state.current_video = None

if "transcription" not in st.session_state:
    st.session_state.transcription = None

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# Search input area
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col_search, col_button = st.columns([7, 2])

with col_search:
    prompt = st.text_input("Search Query", placeholder="Search for Videos and Get Transcripts...", key="top_search", label_visibility="collapsed")

with col_button:
    search_triggered = st.button("Search & Transcribe")

st.markdown('</div>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown("### Configuration")
    
    model_options = {
        "Llama 3.3 70B": "llama-3.3-70b-versatile",
        "Llama 3.2 90B Vision": "llama-3.2-90b-vision-preview",
        "Llama 3.1 70B": "llama3-70b-8192",
        "Llama 3.1 8B": "llama3-8b-8192",
        "Mixtral 8x7B": "mixtral-8x7b-32768",
        "Gemma 2 9B": "gemma2-9b-it"
    }
    
    selected_model_name = st.selectbox("Agent Model", options=list(model_options.keys()))
    selected_model = model_options[selected_model_name]
    
    st.markdown("### Status")
    if st.session_state.current_video:
        st.markdown(f"**Current Video:** {st.session_state.current_video['title'][:60]}...")
    if st.session_state.transcription:
        st.success("Transcript loaded")
    else:
        st.info("No transcript yet")
    
    if st.button("Clear Session"):
        st.session_state.messages = []
        st.session_state.current_video = None
        st.session_state.transcription = None
        st.session_state.last_prompt = ""
        st.rerun()

# Process new query when submitted
if prompt and (search_triggered or prompt != st.session_state.last_prompt):
    st.session_state.last_prompt = prompt
    
    if not prompt.strip():
        st.warning("Please enter a search query.")
    else:
        # Prevent processing the same query twice
        if st.session_state.messages and st.session_state.messages[-1].get("role") == "user" and st.session_state.messages[-1].get("content") == prompt:
            st.warning("This query was just processed. Please enter a new one or clear session.")
        else:
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Search YouTube
            with st.spinner("Searching YouTube..."):
                videos = search_youtube_video(prompt, num_results=5)
            
            if not videos:
                msg = "No relevant videos found."
                st.session_state.messages.append({"role": "assistant", "content": msg})
            else:
                video = videos[0]
                st.session_state.current_video = video
                
                # Message with selected video details
                video_msg = f"""**Selected Video:** {video['title']}

**Channel:** {video['channel']} | Duration: {video['duration']}

[Watch on YouTube]({video['link']})"""
                st.session_state.messages.append({"role": "assistant", "content": video_msg, "video_info": video})

                # Extract transcript
                with st.spinner("Extracting transcript..."):
                    transcript, error = get_youtube_transcript(video["link"])
                
                if error:
                    transcript_msg = f"Warning: {error}\n\nAnswering based on video metadata and general knowledge."
                    st.session_state.transcription = None
                else:
                    st.session_state.transcription = transcript
                    preview = transcript[:1000] + ("..." if len(transcript) > 1000 else "")
                    transcript_msg = f"""Transcript retrieved successfully

**Transcript preview:**

> {preview}"""
                
                st.session_state.messages.append({"role": "assistant", "content": transcript_msg})

                # Generate AI answer using Groq
                with st.spinner("Generating answer..."):
                    client = st.session_state.clients["groq"]
                    
                    context = transcript[:15000] if transcript else "No transcript available."
                    system_prompt = f"""You are Nexus Query, an expert YouTube research agent.
Answer the user's question using the provided video transcript when available.

User Question: "{prompt}"
Video Title: {video['title']}
Channel: {video['channel']}

Transcript excerpt:
\"\"\"{context}\"\"\"

Instructions:
- Be accurate, detailed, and professional
- Quote or reference the transcript when possible
- If no transcript, use reliable general knowledge
- Always cite the source video"""

                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.4,
                        max_tokens=2048
                    )
                    answer = response.choices[0].message.content
                
                final_msg = f"""{answer}

**Source Video:** [{video['title']}]({video['link']}) by {video['channel']}"""
                st.session_state.messages.append({"role": "assistant", "content": final_msg, "video_info": video})

# Chat history display container
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.markdown(
            "<div style='text-align: center; padding: 4rem 1rem; color: var(--text-secondary); font-size: 1.1rem;'>"
            "Enter a query above to search YouTube videos, extract transcripts, and get AI-powered answers."
            "</div>",
            unsafe_allow_html=True
        )
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("video_info"):
                info = msg["video_info"]
                st.markdown(f"**Source:** [{info['title']}]({info['link']}) by {info['channel']}")

# Footer
st.markdown("---")
st.caption(f"Model: {selected_model_name} | Powered by Groq | YouTube via SerpApi")