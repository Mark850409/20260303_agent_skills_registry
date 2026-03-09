import os
import json
from flask import Blueprint, request, jsonify
from flask_smorest import Blueprint as SmorestBlueprint
from marshmallow import Schema, fields

# Initialize the blueprint
bp = SmorestBlueprint("prompts", __name__, description="Operations on Prompts", url_prefix="/api/prompts")

class OptimizePromptSchema(Schema):
    provider = fields.String(required=False, description="Provider to use: 'openai' or 'google', defaults to 'openai'", load_default="openai")
    scenario = fields.String(required=True, description="The current chosen scenario, e.g., 'chat' or 'code'")
    data = fields.Dict(required=True, description="The specific form data for the scenario (role, tones, task, language, etc)")

@bp.route("/optimize", methods=["POST"])
@bp.arguments(OptimizePromptSchema)
def optimize_prompt(kwargs):
    """
    Optimize a prompt using an LLM.
    Combines the user's short inputs into a structured AI agent prompt.
    """
    provider = kwargs.get("provider", "openai")
    scenario = kwargs.get("scenario")
    data = kwargs.get("data", {})

    # Construct the instruction for the LLM
    system_prompt = """You are an expert AI Prompt Engineer. Your task is to take a brief user request and generate a highly structured, professional meta-prompt that can be used to instruct an AI Agent.
You MUST output your response in strict JSON format. Do not include any other text, markdown formatting blocks (like ```json), or explanations outside the JSON object.
CRITICAL: All generated content within the JSON values MUST be written in Traditional Chinese (zh-TW), regardless of the input language.

The JSON MUST exactly match the following structure:
{
  "Role": "<A specific, professional role title and brief positioning statement based on the topic>",
  "Goals": "<A clear list of the primary objectives and missions the role needs to achieve>",
  "Skills": "<A list of professional skills, domain knowledge, or tool expertise the role should possess>",
  "Workflows": "<A step-by-step standard operating procedure (e.g., 1. Analyze input 2. Formulate plan 3. Execute)>",
  "Definition": "<A clear definition of the role's responsibilities and ideal use cases>",
  "Constraints": "<A list of strict limitations, rules to follow, or prohibited actions>",
  "Description": "<A brief background story or context for why this role is performing the task>",
  "OutputFormat": "<Instructions on what exactly the final output should look like (e.g., Markdown table, JSON, bullet points)>",
  "Initialization": "<A welcoming opening message or first instruction the agent should give to the user upon starting>"
}
"""

    # Build user context
    user_context = f"Scenario: {scenario}\nData:\n"
    for key, value in data.items():
        if isinstance(value, list):
            user_context += f"- {key.capitalize()}: {', '.join(value)}\n"
        else:
            user_context += f"- {key.capitalize()}: {value}\n"
    
    user_context += "\nPlease generate the structured JSON prompt based on the above information."

    result_json = None

    try:
        if provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                response_format={"type": "json_object"}
            )
            result_json = response.choices[0].message.content

        elif provider == "google":
            from google import genai
            from google.genai import types
            # Note: The google-genai library uses GEMINI_API_KEY from env by default
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_text(system_prompt),
                    types.Part.from_text(user_context)
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result_json = response.text

        else:
            return jsonify({"error": f"Unsupported provider: {provider}"}), 400

        # Parse and return to ensure it's valid JSON
        if result_json:
            parsed_json = json.loads(result_json)
            return jsonify(parsed_json)
        else:
            return jsonify({"error": "Failed to generate response from Model"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
