# imports

import os
import json
import gradio as gr
import ollama

system_message = "You are a helpful assistant for an Airline called FlightAI. "
system_message += "Give short, courteous answers, no more than 1 sentence. "
system_message += "Always be accurate. If you don't know the answer, say so."

MODEL = 'llama3.2'

# Let's start by making a useful function
ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}

def get_ticket_price(destination_city):
    print(f"Tool get_ticket_price called for {destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, "Unknown")

# We have to write that function handle_tool_call:
def handle_tool_call(cityname):
    city = cityname.get('destination_city')
    price = get_ticket_price(city)
    response = {
        "role": "tool",
        "content": json.dumps({"destination_city": city,"price": price}),
    }

    return response, city
    
def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = ollama.chat(model=MODEL, messages=messages, tools=[get_ticket_price])

    available_functions = {
        'get_ticket_price': get_ticket_price
    }
    
    if response.message.tool_calls:
        for tool in response.message.tool_calls or []:
              function_to_call = available_functions.get(tool.function.name)
              if function_to_call:
                  print('Calling function:', tool.function.name)
                  print('Arguments:', tool.function.arguments)
                  print('Function output:', function_to_call(**tool.function.arguments))
                  message = response['message']
                  response, city = handle_tool_call(tool.function.arguments)
                  messages.append(message)
                  messages.append(response)
                  response = ollama.chat(model=MODEL, messages=messages)
              else:
                print('Function not found:', tool.function.name)
            
    return response['message']['content']

gr.ChatInterface(fn=chat, type="messages").launch()
