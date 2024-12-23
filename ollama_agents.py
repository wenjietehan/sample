# imports
import os
import json
import gradio as gr
import ollama
import pandas as pd

system_message = "You are a helpful assistant for an Airline called FlightAI. "
system_message += "Give short, courteous answers, no more than 1 sentence. "
system_message += "Always be accurate. If you don't know the answer, say so."

MODEL = 'llama3.2'

# Let's start by making a useful function
ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}

# Get ticket price tool
def get_ticket_price(destination_city):
    print(f"Tool get_ticket_price called for {destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, "Unknown")

# Flight booking tool
# intialise data of lists.
tickets = {'Orig_city':['new york', 'new york', 'los angeles', 'los angeles'],
        'Dest_city':['london', 'paris', 'tokyo', 'berlin'],
        'Economy':[799, 899, 1400, 499],
        'Business':[1299, 1399, 1900, 999]}
 
# Create DataFrame
df = pd.DataFrame(tickets)

def book_tickets(destination_city, num_of_tickets, orig_city, ticket_class):
    print(f"Tool book_tickets called for {orig_city} to {destination_city}")

    orig_city = 'new york' if orig_city is None else orig_city.lower()
    dest_city = 'london' if destination_city is None else destination_city.lower()
    tickets = '1' if num_of_tickets is None else num_of_tickets
    t_class = 'Economy' if ticket_class is None else ticket_class
    
    if 'economy' in t_class.lower():
        t_class = 'Economy'
    elif 'business' in t_class.lower():
        t_class = 'Business'

    price = df.query(f"Orig_city == '{orig_city}' & Dest_city == '{dest_city}'")[t_class].iloc[0]
    total_price = int(price)*int(tickets)

    return (total_price)
    
# Construct the content for role tool
def format_tool_content(message):
    arguments = message.tool_calls[0].function.arguments
    name = message.tool_calls[0].function.name

    if name == 'get_ticket_price':
        city = arguments.get('destination_city')
        price = get_ticket_price(city)
        response = {
            "role": "tool",
            "content": json.dumps({"destination_city": city,"price": price})
        }
    elif name == 'book_tickets':
        dest_city = arguments.get('destination_city')
        orig_city = arguments.get('orig_city')
        num_tickets = arguments.get('num_of_tickets')
        ticket_class = arguments.get('ticket_class')

        price = book_tickets(dest_city, num_tickets, orig_city, ticket_class)

        response = {
            "role": "tool",
            "content": json.dumps(
                {"orig_city": orig_city, 
                 "destination_city": dest_city, 
                 "num_of_tickets": num_tickets, 
                 "ticket_class": ticket_class, 
                 "price": price})
        }

    return response
    
def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = ollama.chat(model=MODEL, messages=messages, tools=[get_ticket_price, book_tickets])

    available_functions = {
        'get_ticket_price': get_ticket_price,
        'book_tickets': book_tickets
    }
    
    if response.message.tool_calls:
        for tool in response.message.tool_calls or []:
              function_name = tool.function.name
              function_to_call = available_functions.get(function_name)
              if function_to_call:
                  print('Calling function:', tool.function.name)
                  print('Arguments:', tool.function.arguments)
                  print('Function output:', function_to_call(**tool.function.arguments))

                  message = response['message']
                  response = format_tool_content(response.message)
                  messages.append(message)
                  messages.append(response)
                  print(messages)
                  response = ollama.chat(model=MODEL, messages=messages)
              else:
                print('Function not found:', function_name)
            
    return response['message']['content']

gr.ChatInterface(fn=chat, type="messages").launch()
