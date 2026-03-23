"""
Bare-minimum test: call Groq API directly WITHOUT LangChain.
This isolates whether the 43s delay is in the API or in LangChain.
"""
import time
import os
from groq import Groq

os.environ["GROQ_API_KEY"] = "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"

client = Groq()

print("Sending request to Groq API directly (no LangChain)...")
t0 = time.time()

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    temperature=0.1,
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Reply in JSON."},
        {"role": "user", "content": "Extract the name and email from this text: 'My name is Lav Kaushik, email vvuthelav4796@gmail.com'. Return JSON with keys: name, email."}
    ]
)

elapsed = time.time() - t0
print(f"\n[TIMER] Raw Groq API call: {elapsed:.2f}s")
print(f"Response: {response.choices[0].message.content}")
