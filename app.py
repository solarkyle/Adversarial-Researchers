import streamlit as st
import requests
from time import sleep  # For streaming simulation

# ================== CONFIGURATION ==================
API_KEY = st.secrets["OPENROUTER_API_KEY"] 

MODELS = {
    "debater1": {
        "model": "google/gemini-2.0-flash-001",
        "grounding": False,
        "temperature": 0.6,
        "top_p": 0.9,
    },
    "debater2": {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "grounding": False,
        "temperature": 0.6,
        "top_p": 0.9,
    },
    "reporter": {
        "model": "google/gemini-2.0-pro-exp-02-05:free",
        "grounding": True,
        "temperature": 0.2,
        "top_p": 0.9,
    },
    "fallback_reporter": {  # Fallback to Flash if Pro hits rate limit
        "model": "google/gemini-2.0-flash-001",
        "grounding": True,
        "temperature": 0.2,
        "top_p": 0.9,
    }
}

def call_model(api_key: str, settings: dict, prompt: str, fallback_settings: dict = None) -> str:
    data = {
        "model": settings["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": settings["temperature"],
        "top_p": settings["top_p"]
    }
    
    if settings["grounding"]:
        data["tools"] = [{
            "type": "function",
            "function": {
                "name": "google_search",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "The search query"}},
                    "required": ["query"]
                }
            }
        }]
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
        },
        json=data
    )
    
    try:
        resp_json = response.json()
        if "choices" in resp_json:
            return resp_json["choices"][0]["message"]["content"]
        elif "content" in resp_json:
            return resp_json["content"]
        elif response.status_code == 429 and fallback_settings:  # Rate limit, try fallback
            st.warning(f"Rate limit hit on {settings['model']}, falling back to {fallback_settings['model']}...")
            return call_model(api_key, fallback_settings, prompt)
        else:
            st.error(f"Unexpected response: {resp_json}")
            return "Error: Could not parse response"
    except Exception as e:
        if response.status_code == 429 and fallback_settings:  # Rate limit, fallback
            st.warning(f"Rate limit hit on {settings['model']}, falling back to {fallback_settings['model']}...")
            return call_model(api_key, fallback_settings, prompt)
        st.error(f"API call failed: {response.status_code} - {response.text}")
        return f"Error: {str(e)}"

def stream_response(text: str):
    for i in range(0, len(text), 50):
        yield text[i:i+50]
        sleep(0.05)

def run_debate(topic: str, max_rounds: int = 3):
    with st.spinner("Generating initial grounded report..."):
        initial_settings = MODELS["reporter"].copy()
        initial_settings["grounding"] = True
        initial_report = call_model(
            API_KEY,
            initial_settings,
            f"Write a comprehensive initial report on {topic}. Include current research and evidence. This will be used as the starting point for a debate.",
            MODELS["fallback_reporter"]
        )
    with st.expander("Initial Report", expanded=True):
        st.write(initial_report)

    conversation = f"INITIAL REPORT:\n{initial_report}\n\n"
    for round_num in range(max_rounds):
        with st.spinner(f"Round {round_num + 1} debating..."):
            expander = st.expander(f"Round {round_num + 1}", expanded=False)
            with expander:
                expert1_prompt = f"""You are Expert 1 in a debate about {topic}.
                Here's the conversation so far: {conversation}
                Your task is to one-up the other expert by bringing up NEW aspects, evidence, or research that hasn't been mentioned yet.
                If you truly have NOTHING new to add, respond with 'I concede.' Any response <10 chars counts as conceding—don’t quit, win this!
                Focus ONLY on new insights, be aggressive, show off your expertise!"""
                response1 = call_model(API_KEY, MODELS["debater1"], expert1_prompt)
                
                if len(response1.strip()) < 10:
                    st.write("🤖 Expert 1: *I concede.*")
                    conversation += "EXPERT 1: I concede.\n\n"
                    break
                st.write("🤖 Expert 1:")
                st.write_stream(stream_response(response1))
                conversation += f"EXPERT 1:\n{response1}\n\n"
                
                expert2_prompt = f"""You are Expert 2 in a debate about {topic}.
                Here's the conversation so far: {conversation}
                Your task is to one-up Expert 1 by bringing up NEW aspects, evidence, or research that hasn't been mentioned yet.
                If you truly have NOTHING new to add, respond with 'I concede.' Any response <10 chars counts as conceding—don’t quit, win this!
                Focus ONLY on new insights, be aggressive, show off your expertise!"""
                response2 = call_model(API_KEY, MODELS["debater2"], expert2_prompt)
                
                if len(response2.strip()) < 10:
                    st.write("🤖 Expert 2: *I concede.*")
                    conversation += "EXPERT 2: I concede.\n\n"
                    break
                st.write("🤖 Expert 2:")
                st.write_stream(stream_response(response2))
                conversation += f"EXPERT 2:\n{response2}\n\n"
    
    with st.spinner("Generating final report..."):
        final_settings = MODELS["reporter"].copy()
        final_settings["grounding"] = False
        report = call_model(
            API_KEY,
            final_settings,
            f"""Generate a comprehensive research report analyzing this debate about {topic}.
            Here's the complete debate transcript: {conversation}
            Analyze their discussion and write a thorough report that:
            1. Synthesizes all key insights and evidence
            2. Evaluates claim strength
            3. Identifies consensus/disagreement
            4. Highlights compelling research
            5. Discusses implications/future directions
            Use clear sections, academic style.""",
            MODELS["fallback_reporter"]
        )
    st.subheader("Final Report")
    st.write(report)
    st.download_button("Download Final Report", report, file_name=f"{topic.replace(' ', '_')}_report.txt")

# Streamlit UI
st.title("Adversarial Researchers")
st.write("Enter a topic, watch two LLMs debate it, and get a polished research report.")

topic = st.text_input("Debate Topic", value="The impact of artificial intelligence on options trading")
max_rounds = st.slider("Max Debate Rounds", min_value=1, max_value=5, value=3)
if st.button("Start Debate"):
    run_debate(topic, max_rounds)
