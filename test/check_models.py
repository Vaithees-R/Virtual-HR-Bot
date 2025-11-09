import google.generativeai as genai

# --- PASTE THE SAME KEY YOU USED BEFORE ---
# Make sure it's the one that fixed the "400" error
try:
    genai.configure(api_key="AIzaSyBWrEvuL2r1AqBLCRvk3Jct-5rtYUVIFVY")
except Exception as e:
    print(f"Error configuring API key: {e}")
    exit()

print("--- Listing all models your key can use ---")

try:
    for m in genai.list_models():
        # We only care about models that can 'generateContent'
        if 'generateContent' in m.supported_generation_methods:
            print(f"Found model: {m.name}")
            
except Exception as e:
    print(f"An error occurred while listing models: {e}")

print("------------------------------------------")
print("Finished.")