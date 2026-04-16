import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", "dummy_key"))

def generate_ad_copy(business_context: dict, assets_text: str):
    prompt = f"""
    You are an expert AI marketing assistant. Given the following business context and extracted text from assets, 
    generate ad copy, social media posts, and content for a PDF brochure.
    
    Business Context:
    {json.dumps(business_context, indent=2)}
    
    Extracted Text from Assets (if any):
    {assets_text}
    
    Return the result strictly as a JSON object with this structure:
    {{
      "ad_copy": "Headline, body, CTA",
      "social_posts": [
         "Post 1 for Twitter",
         "Post 2 for Instagram",
         "Post 3 for LinkedIn"
      ],
      "brochure_content": "Detailed text to be put on a professional PDF brochure for this business."
    }}
    """
    
    # Note: the model name might need updating depending on exactly what Groq supports today
    # "llama3-70b-8192" is typically supported.
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    return json.loads(content)
