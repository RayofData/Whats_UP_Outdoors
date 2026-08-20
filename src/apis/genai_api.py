"""Handle requests to the Google Gemini API."""

from google import genai


client = genai.Client()

def generate_text(prompt):
    response = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt,
    )

    return response.output_text