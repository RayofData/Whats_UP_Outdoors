from google import genai
import json

client = genai.Client()


def describe_trail(trail_data):
    """Return a natural-language summary of the supplied trail details."""
    prompt = f"""
    Write a short, natural hiking trail overview using only the supplied data.

    You may make careful interpretations, but do not invent facts.
    Treat iNaturalist observations as reported sightings near the trail,
    not as guaranteed wildlife encounters.

    Trail data:
    {json.dumps(trail_data, indent=2)}
    """

    try:
        response = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
        )

        return response.output_text or "AI summary unavailable."

    except Exception:
        return "AI summary unavailable."