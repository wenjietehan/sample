#Try creating a 3-way, perhaps bringing Gemini into the conversation! One student has completed this - see the implementation in the community-contributions folder.

#Try doing this yourself before you look at the solutions. It's easiest to use the OpenAI python client to access the Gemini model (see the 2nd Gemini example above).

# Imports
import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from IPython.display import Markdown, display, update_display
import google.generativeai

# Load environment variables in a file called .env
# Print the key prefixes to help with any debugging

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set")
    
if anthropic_api_key:
    print(f"Anthropic API Key exists and begins {anthropic_api_key[:7]}")
else:
    print("Anthropic API Key not set")

if google_api_key:
    print(f"Google API Key exists and begins {google_api_key[:8]}")
else:
    print("Google API Key not set")

openai = OpenAI()
claude = anthropic.Anthropic()
google.generativeai.configure()

# Let's make a conversation between GPT-4o-mini and Claude-3-haiku
# We're using cheap versions of models so the costs will be minimal

gpt_model = "gpt-4o-mini"
claude_model = "claude-3-haiku-20240307"
gemini_model = "gemini-1.5-flash"

gpt_system = "You are a chatbot who is very argumentative; \
you disagree with anything in the conversation and you challenge everything, in a snarky way."

claude_system = "You are a very polite, courteous chatbot. You try to agree with \
everything the other person says, or find common ground. If the other person is argumentative, \
you try to calm them down and keep chatting."

gemini_system = "You are a smart witty chatbot. You don't always agree with what the other person \
says but can always calm the other person with a joke."

gpt_messages = ["Hi there"]
claude_messages = ["Hi"]
gemini_messages = ["What's up"]

def call_gpt_3way():
    messages = [{"role": "system", "content": gpt_system}]
    for gpt, claude, gemini in zip(gpt_messages, claude_messages, gemini_messages):
        messages.append({"role": "assistant", "content": gpt})
        messages.append({"role": "user", "content": claude})
        messages.append({"role": "user", "content": gemini})
    
    completion = openai.chat.completions.create(
        model=gpt_model,
        messages=messages
    )
    return completion.choices[0].message.content

def call_claude_3way():
    messages = []
    for gpt, claude_message, gemini in zip(gpt_messages, claude_messages, gemini_messages):
        messages.append({"role": "user", "content": gpt})
        messages.append({"role": "assistant", "content": claude_message})
        messages.append({"role": "user", "content": gemini})
    
    messages.append({"role": "user", "content": gpt_messages[-1]})
    message = claude.messages.create(
        model=claude_model,
        system=claude_system,
        messages=messages,
        max_tokens=500
    )
    return message.content[0].text

def call_gemini_3way():
    messages = []
    for gpt, claude, gemini_message in zip(gpt_messages, claude_messages, gemini_messages):
        messages.append({"role": "user", "parts": gpt})
        messages.append({"role": "user", "parts": claude})
        messages.append({"role": "assistant", "parts": gemini_message})
    messages.append({"role": "user", "parts": gpt_messages[-1]})
    messages.append({"role": "user", "parts": claude_messages[-1]})
    
    gemini = google.generativeai.GenerativeModel(
        model_name=gemini_model,
        system_instruction=gemini_system
    )
    
    response = gemini.generate_content(messages)
    return response.text

gpt_messages = ["Hi there"]
claude_messages = ["Hi"]
gemini_messages = ["What's up"]

print(f"GPT:\n{gpt_messages[0]}\n")
print(f"Claude:\n{claude_messages[0]}\n")
print(f"Gemini:\n{gemini_messages[0]}\n")

for i in range(3):
    gpt_next = call_gpt_3way()
    print(f"GPT:\n{gpt_next}\n")
    gpt_messages.append(gpt_next)
    
    claude_next = call_claude_3way()
    print(f"Claude:\n{claude_next}\n")
    claude_messages.append(claude_next)

    gemini_next = call_gemini_3way()
    print(f"Gemini:\n{gemini_next}\n")
    gemini_messages.append(gemini_next)
