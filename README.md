# Nexus Query

**Nexus Query** is a powerful, YouTube-powered AI research agent built with Streamlit. It intelligently searches YouTube for the most relevant video on any topic, automatically extracts the full transcript, and uses Groq's ultra-fast LLMs to deliver a precise, detailed, and professionally sourced answer based on the video content.

With a bold YouTube-inspired red theme, real-time processing, and seamless integration of search + transcription + reasoning, it turns any question into deep, video-backed insight.

## Live Demo

[https://saadajee-nexus-query.streamlit.app](https://saadajee-nexus-query.streamlit.app)

## Features

- Real-time YouTube video search via SerpApi
- Automatic transcript extraction using `youtube-transcript-api`
- Intelligent answer generation powered by Groq (Llama 3.3 70B, Llama 3.2 70B, Mixtral, and more)
- Clean, bold YouTube red dark theme with professional typography
- Full session management: clear conversation, status tracking
- Responsive design for desktop and mobile
- Source citation with direct YouTube link
- Fallback to general knowledge when transcripts are unavailable
- Production-ready error handling and status feedback

## How It Works

1. You ask a question or describe a topic
2. Nexus Query searches YouTube for the best matching video
3. It retrieves the full English transcript (manual or auto-generated)
4. Groq analyzes the transcript and generates a thorough, accurate answer
5. The response includes key insights and a direct link to the source video

Perfect for learning complex topics, researching concepts, or quickly understanding explanations from trusted creators.

## Tech Stack

- **Frontend**: Streamlit
- **LLM Backend**: Groq (Llama 3.3, Llama 3.2, Mixtral)
- **Video Search**: SerpApi (YouTube engine)
- **Transcription**: youtube-transcript-api
- **Requests**: Standard Python `requests`

## Local Development

1. Clone the repository:
  ```
  git clone https://github.com/Saadajee/nexus-query.git
  cd nexus-query
  ```
2. Create a virtual environment and install dependencies:
  ```
  python -m venv venv
  source venv/bin/activate  
  # On Windows: venv\Scripts\activate
  pip install streamlit groq requests youtube-transcript-api
  ```
3. Create _.streamlit/secrets.toml_ in the project root:
  ```
  GROQ_API_KEY = "gsk_your_groq_key_here"
  SERPAPI_KEY = "your_serpapi_key_here"
  ```
4. Run the app:
  ```
  streamlit run app.py
  ```

## Deployment
Deploy for free on Streamlit Community Cloud:

- Connect your GitHub repository
- Set GROQ_API_KEY and SERPAPI_KEY in app secrets
- Main file: app.py

## Sample Queries

- "Explain quantum entanglement in simple terms"
- "How does photosynthesis work?"
- "What is the difference between HTTP and HTTPS?"
- "Best way to learn Python for beginners"

## Acknowledgments

- Powered by Groq for lightning-fast inference
- Video search via SerpApi
- Transcript extraction via youtube-transcript-api
