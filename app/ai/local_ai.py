
import ollama
import json


MODEL_NAME = "qwen2.5:3b"


def ask_local_ai(prompt):
    """Send a prompt to the locally running Ollama model."""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def extract_project_information(document_text):
    """Extract structured project information using local AI."""

    prompt = f"""
You are an expert project reporting assistant.

Analyse the project document carefully.

Extract all available information and return ONLY valid JSON.

Use exactly this structure:

{{
    "project_name": "",
    "client": "",
    "project_manager": "",
    "project_status": "",
    "project_description": "",
    "project_start_date": "",
    "target_completion_date": "",
    "approved_budget": "",
    "current_completion": "",
    "milestones": [
        {{
            "name": "",
            "status": "",
            "progress": "",
            "target_date": ""
        }}
    ],
    "risks": [
        {{
            "risk_id": "",
            "description": "",
            "severity": "",
            "mitigation": ""
        }}
    ],
    "next_reporting_period": "",
    "reporting_notes": ""
}}

IMPORTANT RULES:

1. Extract every milestone, including its name.
2. Extract every risk, including its ID.
3. Preserve all dates, percentages and amounts.
4. Do not invent missing information.
5. Use empty strings for missing text fields.
6. Use empty arrays when no records exist.
7. Return valid JSON only. No explanations or markdown.

PROJECT DOCUMENT:

{document_text}
"""

    result = ask_local_ai(prompt)

    try:
        return json.loads(result)

    except json.JSONDecodeError:
        return {
            "error": "The AI did not return valid JSON.",
            "raw_response": result
        }

