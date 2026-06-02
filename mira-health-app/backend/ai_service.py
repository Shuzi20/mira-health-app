import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def predict_health(full_name: str, dob: str, glucose: float, haemoglobin: float, cholesterol: float) -> str:

    prompt = f"""
    You are a medical AI assistant. Based on the following patient blood test results,
    provide a brief health risk assessment in 2-3 sentences.
    Only mention possible conditions — do not give treatment advice.

    Patient Name  : {full_name}
    Date of Birth : {dob}
    Glucose       : {glucose} mg/dL
    Haemoglobin   : {haemoglobin} g/dL
    Cholesterol   : {cholesterol} mg/dL

    Provide a short, clear health prediction based on these values.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful medical AI assistant that analyzes blood test results."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content