import google.generativeai as genai

# This is the key you have from Google AI Studio
YOUR_GEMINI_API_KEY = "AIzaSyCDHWOfD9oP4BQMNsdep58wdo5HeWZdnUM"

genai.configure(api_key=YOUR_GEMINI_API_KEY)

# Use a fast model for chat/questions
model = genai.GenerativeModel('gemini-1.5-flash')

# Example for your question generator
prompt = "Generate 5 technical interview questions for an HR bot about Python"
response = model.generate_content(prompt)

print(response.text)