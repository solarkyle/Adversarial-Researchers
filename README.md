# Adversarial-Researchers

## Concept
This project implements a novel approach to extracting knowledge from Large Language Models (LLMs) through competitive debate. The core idea is that when LLMs are placed in an antagonistic setting where they must "one-up" each other, they tend to surface more of their internal knowledge than through standard prompting.

# Test it out here
https://adversarial-researchers.streamlit.app/

### How it Works
1. **Initial Grounding**: Start with a grounded report from a model with access to real-time information
2. **Competitive Extraction**: Two models engage in a debate, each trying to outdo the other by introducing new concepts and evidence
3. **Exhaustive Knowledge**: Models continue until they genuinely can't think of anything new to add
4. **Fact Synthesis**: A final model analyzes the entire debate with ground truthing to create a comprehensive, verified report

### The Psychology Behind It
The system leverages several interesting behaviors of LLMs:
- Models seem to "try harder" when challenged by peers
- Competitive prompting encourages more thorough knowledge retrieval
- The desire to "win" pushes models to surface less obvious information
- Sequential one-upmanship helps avoid repetition

## Features
- Uses different models with different strengths
- Passes complete conversation history for context
- Aggressive prompting to encourage knowledge extraction
- Automatic concession when knowledge is exhausted
- Ground truthing for initial and final reports
- Easy configuration of models and parameters

## Configuration
```python
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
    }
}
```

## Usage
```python
python debate_system.py
```

The system will:
1. Generate initial grounded report
2. Run debate until concession or max rounds
3. Generate final analysis report

## Requirements
- OpenRouter API key
- Python 3.x
- requests library

## How to Get the Most Out of It
1. **Topic Selection**: Choose topics that have depth and multiple aspects to explore
2. **Model Selection**: Use models with different training or capabilities
3. **Temperature**: Higher for debaters (more creative), lower for reporter (more accurate)
4. **Prompting**: The antagonistic prompting is key - it pushes models to dig deeper

## Why This Works
Traditional Q&A with LLMs often gets surface-level knowledge. This system:
1. Creates competitive pressure to reveal more
2. Forces models to find unique angles
3. Builds on previous points without repetition
4. Validates through ground truthing

## Limitations
- Model responses depend on temperature settings
- Ground truthing only available for certain models
- Quality of debate depends on prompt engineering
- Final report limited by model context window
- Models rarely concede even when prompted (needs improvement)

## Example Run
A debate on "The impact of artificial intelligence on options trading" was run using this system:
- Full debate logs available in `chat_logs.md`
- Final synthesis report in `final_report.md`
- Total cost: ~$0.05 via OpenRouter
- Neither model conceded despite instructions, highlighting need for better concession detection

## Future Improvements
- Add more sophisticated debate strategies
- Start the initial report with perplexity sonar reasoning
- Implement better fact-checking mechanisms
- Add support for more models
- Improve prompt engineering
- Add debate topic templates

## Contributing
Feel free to contribute ideas for improving the debate strategy or knowledge extraction process. Focus areas:
- Better prompting strategies
- New model combinations
- Improved fact validation
- Topic templates
