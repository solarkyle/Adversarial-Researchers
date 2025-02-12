import requests

# ================== CONFIGURATION ==================
API_KEY = 'open router key'

TOPIC = "The impact of artificial intelligence on options trading"
MAX_ROUNDS = 10

MODELS = {
    "debater1": {
        "model": "google/gemini-2.0-flash-001",
        "grounding": False,  # Only initial report uses grounding
        "temperature": 0.6,  # Higher temp for more creative responses
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
    }
}

def call_model(api_key: str, settings: dict, prompt: str) -> str:
    """Call any model through OpenRouter"""
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
                    "properties": {
                        "query": {"type": "string", "description": "The search query"}
                    },
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
    return response.json()['choices'][0]['message']['content']

def run_debate():
    """Run a debate between two models on the configured topic"""
    # Get initial grounded report
    print("\nGenerating initial report with ground truthing...")
    initial_settings = MODELS["reporter"].copy()
    initial_settings["grounding"] = True
    initial_report = call_model(
        API_KEY,
        initial_settings,
        f"""Write a comprehensive initial report on {TOPIC}.
        Include current research and evidence.
        This will be used as the starting point for a debate."""
    )
    print("\n=== Initial Report ===")
    print(initial_report)
    
    # Start debate
    conversation = f"INITIAL REPORT:\n{initial_report}\n\n"
    
    for round_num in range(MAX_ROUNDS):
        print(f"\n--- Round {round_num + 1} ---")
        
        # Expert 1's turn
        expert1_prompt = f"""You are Expert 1 in a debate about {TOPIC}.
        
Here's the conversation so far:
{conversation}

Your task is to one-up the other expert by bringing up NEW aspects, evidence, or research that hasn't been mentioned yet.
Really try to show off your knowledge and prove your superior expertise!

If you truly have NOTHING new to add (be honest!), just respond with "I concede."
any response thats less than 10 characters counts as you conceding, so try extremely hard, don't be a quitter, win this!
Otherwise, focus ONLY on introducing new insights - don't repeat what's been said.
Be aggressive in showing your expertise and challenging the other expert's knowledge!"""
        
        response1 = call_model(API_KEY, MODELS["debater1"], expert1_prompt)
        
        if len(response1.strip()) < 10:  # Check for concession
            print("\n🤖 Expert 1: I concede.")
            conversation += "EXPERT 1: I concede.\n\n"
            break
            
        print("\n🤖 Expert 1:")
        print(response1)
        conversation += f"EXPERT 1:\n{response1}\n\n"
        
        # Expert 2's turn
        expert2_prompt = f"""You are Expert 2 in a debate about {TOPIC}.
        
Here's the conversation so far:
{conversation}

Your task is to one-up Expert 1 by bringing up NEW aspects, evidence, or research that hasn't been mentioned yet.
Really try to show off your knowledge and prove your superior expertise!

If you truly have NOTHING new to add (be honest!), just respond with "I concede."
any response thats less than 10 characters counts as you conceding, so try extremely hard, don't be a quitter, win this!
Otherwise, focus ONLY on introducing new insights - don't repeat what's been said.
Be aggressive in showing your expertise and challenging Expert 1's knowledge!"""
        
        response2 = call_model(API_KEY, MODELS["debater2"], expert2_prompt)
        
        if len(response2.strip()) < 10:  # Check for concession
            print("\n🤖 Expert 2: I concede.")
            conversation += "EXPERT 2: I concede.\n\n"
            break
            
        print("\n🤖 Expert 2:")
        print(response2)
        conversation += f"EXPERT 2:\n{response2}\n\n"
    
    # Generate final report
    print("\n=== Generating Final Report ===")
    report = call_model(
        API_KEY,
        MODELS["reporter"],
        f"""Generate a comprehensive research report analyzing this debate about {TOPIC}.
        
Here's the complete debate transcript:
{conversation}

Analyze their discussion and write a thorough report that:
1. Synthesizes all the key insights and evidence presented
2. Evaluates the strength of different claims and perspectives
3. Identifies areas of consensus and disagreement
4. Highlights the most compelling research cited
5. Discusses implications and future directions

Use clear sections and academic style. Be thorough in exploring all the ideas and evidence that emerged in the debate."""
    )
    
    print("\n=== FINAL REPORT ===")
    print(report)

if __name__ == "__main__":
    run_debate()
