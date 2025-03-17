from flask import Flask, request, jsonify, render_template
from twilio.twiml.voice_response import VoiceResponse
import openai
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os
from openai import OpenAI
import json
import os.path
import datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone
from pytz import timezone 
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from elevenlabs import ElevenLabs, VoiceSettings
from pydub import AudioSegment
from pydub.playback import play
import io
from speech_recognition import text_to_speech, speech_to_text, save_audio_file
import base64

from elevenlabs import ElevenLabs, VoiceSettings
import elevenlabs





SCOPES = ["https://www.googleapis.com/auth/calendar"]



app = Flask(__name__)


#TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
#TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
#TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
#FIREBASE_CONFIG = {
#     'apiKey': os.getenv('FIREBASE_API_KEY'),
#     'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
#     'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
#     'projectId': os.getenv('FIREBASE_PROJECT_ID'),
#     'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
#     'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
#     'appId': os.getenv('FIREBASE_APP_ID'),
# }

def reverse_name(name):
    reversed_name = name[::-1]
    return f"Your name backwards is {reversed_name}"

def text_to_speech(text):
        
        
        #USE GRACE(LEGACY) VOICE#
        #voice ID: oWAxZDx7w5VEj9dCyTzz

        client = ElevenLabs(
            api_key="sk_dce04ff3e0541155c2e8cd48bb13478184f276599b45607a",
        )
        audio_generator = client.text_to_speech.convert(
            model_id="eleven_turbo_v2_5",
            voice_id="oWAxZDx7w5VEj9dCyTzz",
            optimize_streaming_latency=0,
            output_format="mp3_22050_32",
            text=text,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.3,
                style=0.5,
            ),
        )
        elevenlabs.play(audio_generator)


def get_credentials():
     # Check if token exists and load credentials from it
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json")
        except json.decoder.JSONDecodeError:
            print("Invalid token.json file. Regenerating credentials...")
            os.remove("token.json")

    # If there are no valid credentials, generate new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds

def get_next_5_events():

    creds = get_credentials()
    print("get_next_5_events was called")

    try:
        service = build("calendar", "v3", credentials=creds)

        # Get current time in ISO format
        now = dt.datetime.now().isoformat() + "Z"

        # Fetch the next 5 events
        event_result = service.events().list(calendarId="primary", timeMin=now, 
                                             maxResults=5, singleEvents=True, 
                                             orderBy="startTime").execute()
        events = event_result.get("items", [])

        if not events:
            response = "No upcoming events found!"
            return response

        event_list = []

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append(f"{start}: {event['summary']}")
        
        return "\n".join(event_list)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"an error occured: {error}"
    
def get_upcoming_events(number):
    creds = get_credentials()

    print("get_upcoming_events was called")
   
    try:
        service = build("calendar", "v3", credentials=creds)

        # Get current time in ISO format
        now = dt.datetime.now().isoformat() + "Z"

        # Fetch the next "number" events
        event_result = service.events().list(calendarId="primary", timeMin=now, 
                                             maxResults=number, singleEvents=True, 
                                             orderBy="startTime").execute()
        events = event_result.get("items", [])

        if not events:
            response = "No upcoming events found!"
            return response

        event_list = []

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append(f"{start}: {event['summary']}")
        
        return "\n".join(event_list)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"an error occured: {error}"
    
def check_availability(start_time, end_time):
    creds = get_credentials()

    print("check_availability was called")

    try:
        service = build("calendar", "v3", credentials=creds)
        # Convert start_time and end_time to UTC
        start_time_utc = start_time.astimezone(dt.timezone.utc)
        end_time_utc = end_time.astimezone(dt.timezone.utc)

        body = {
            "timeMin": start_time_utc.isoformat(),
            "timeMax": end_time_utc.isoformat(),
            "timeZone": 'UTC',
            "items": [{"id": "primary"}]
        }

      

        freebusy_info = service.freebusy().query(body=body).execute()
        busy_times = freebusy_info['calendars']['primary']['busy']

        print(f"This is the start date to check: {start_time_utc}")
        print(f"List of busy times returned by API: {busy_times}")

        #add some code here to append all free times into a free times array
        #this array can be used to check if another time on that day is available

        if not busy_times:
            return "This time slot is available"
        else:
            res1 = "This time slot is busy:\n"
            return res1

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"an error occured: {error}"



def find_available_time(day):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Define start and end time for the day
    time_min = dt.time(8, 0)   # 8 AM
    time_max = dt.time(21, 0)  # 9 PM

    # Combine date and time, then convert to UTC
    time_min_utc = dt.datetime.combine(day, time_min).astimezone(dt.timezone.utc).isoformat(timespec='seconds')
    time_max_utc = dt.datetime.combine(day, time_max).astimezone(dt.timezone.utc).isoformat(timespec='seconds')

    # Prepare the request body for the freebusy query
    body = {
        "timeMin": time_min_utc,
        "timeMax": time_max_utc,
        "timeZone": "UTC",
        "items": [{"id": "primary"}]
    }

    # Execute the freebusy query
    freebusy_info = service.freebusy().query(body=body).execute()
    busy_times = freebusy_info['calendars']['primary']['busy']

    busy_times_edt = []
    for busy_period in busy_times:
        # Parse start and end times from the busy period
        start_time_utc = dt.datetime.fromisoformat(busy_period['start'].replace('Z', '+00:00'))
        end_time_utc = dt.datetime.fromisoformat(busy_period['end'].replace('Z', '+00:00'))

        # Convert to Eastern Time (EDT/EST as needed)
        start_time_edt = start_time_utc.astimezone(ZoneInfo("America/New_York"))
        end_time_edt = end_time_utc.astimezone(ZoneInfo("America/New_York"))

        # Format the times to ISO 8601 with 'seconds' precision
        busy_times_edt.append({
            'start': start_time_edt.isoformat(timespec='seconds'),
            'end': end_time_edt.isoformat(timespec='seconds')
        })

    print(f"this is the raw busy_times_edt array:{busy_times_edt}")

    
    # Format busy times for the output
    busy_times_str = ', '.join([f"{bt['start']} to {bt['end']} " for bt in busy_times_edt])

    print(f"Busy time ranges returned by find_availability function: {busy_times_str}")

    return f"Any time between 8 AM EDT to 9 PM EDT except for {busy_times_str} is available."


def get_gpt_response(messages):
    client = OpenAI(
        # MAKE SURE TO PUT THIS IN ENV FILE AFTER TESTING!!!
        # MAKE SURE TO PUT THIS IN ENV FILE AFTER TESTING!!!
        # MAKE SURE TO PUT THIS IN ENV FILE AFTER TESTING!!!
        api_key="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"
        # MAKE SURE TO PUT THIS IN ENV FILE AFTER TESTING!!!
        # MAKE SURE TO PUT THIS IN ENV FILE AFTER TESTING!!!
        # MAKE SURE TO PUT THIS IN ENV FILE AFTER TESTING!!!
    )

    tools = [
    {
        "type": "function",
        "function": {
            "name": "reverse_name",
            "description": "Reverses a given name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name to reverse",
                    },
                },
                "required": ["name"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_events",
            "description": "Retrieves upcoming events in the Google Calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "integer",
                        "description": "The number of upcoming events to look for"
                    }
                },
                "required": ["number"],  # Add this line if the parameter is required
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Checks if a date and time is available in Google Calendar", #add "also checks for available times in a given day" here after adding functionality
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "The start date of the event"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date of the event"
                    }
                },
                "required": ["start_date"],  # Make both required if needed
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"find_available_time",
            "description":"gets the free times within a certain day",
            "parameters":{
                "type":"object",
                "properties":{
                    "day":{
                        "type":"string",
                        "description":"The day that is used to check for availabilites"
                    }
                },
                "required":["day"]
            }
        }
    }
]

    print("Sending request to OpenAI...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        if function_name == "reverse_name":
            function_response = reverse_name(function_args["name"])
        elif function_name == "get_next_5_events":
            function_response = get_next_5_events()
        elif function_name == "get_upcoming_events":
            function_response = get_upcoming_events(function_args["number"])
        elif function_name == "check_availability":

            start_date = dt.datetime.fromisoformat(function_args["start_date"])
            end_date_str = function_args.get("end_date")
            if end_date_str is None:
                end_date = start_date + dt.timedelta(minutes=30)
            else:
                end_date = dt.datetime.fromisoformat(end_date_str)

            function_response = check_availability(start_date,end_date)
        elif function_name == "find_available_time":
            day = dt.datetime.fromisoformat(function_args["day"])
            function_response = find_available_time(day)
        else:
            function_response = "Function not found."

        messages.append(message.model_dump())
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": function_response,
        })

        print(f"Function '{function_name}' was called.")

        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return second_response.choices[0].message.content
    else:
        return message.content

    
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Endpoint to handle speech-to-text conversion using OpenAI Whisper
    """
    try:
        if request.is_json:
            # Handle base64 encoded audio data
            audio_data = base64.b64decode(request.json['audio'].split(',')[1])
        elif 'audio' in request.files:
            # Handle file upload
            audio_data = request.files['audio'].read()
        else:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Save the audio file temporarily
        temp_path = save_audio_file(audio_data)
        if not temp_path:
            return jsonify({'error': 'Failed to save audio file'}), 500
        
        try:
            # Transcribe the audio using Whisper
            transcribed_text = speech_to_text(temp_path)
            
            if transcribed_text:
                # Generate speech response using ElevenLabs
                text_to_speech(transcribed_text)
                
                return jsonify({
                    'success': True,
                    'transcription': transcribed_text
                })
            else:
                return jsonify({'error': 'Failed to transcribe audio'}), 500
                
        finally:
            # Clean up the temporary file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def upload_page():
    return render_template('upload.html')

if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=True, port=5000)
    
# Comment out or remove the terminal conversation loop
#    current_time = dt.datetime.now()
#    print("Starting conversation. Type 'exit' to quit.")
#    messages = [
#        {
#            "role": "system", 
#            "content": (
#                f"You are a helpful assistant capable of general conversation.\n"
#                f"You can also reverse names when asked. Maintain context of the conversation "
#                f"and provide accurate, coherent responses. If a user mentions a date without specifying the year, "
#                f"assume the current year and use the current month and day for context, this is the current date: {current_time}. For phrases like 'next month on the 3rd', "
#                f"interpret the date relative to the current date which is {current_time}."
#                f"if asked to provide a range of open times within a given day,"
#                f"reply with something similar to this example:There are multiple times available on the 23rd between 8 AM to 9 PM."
#                f"Just let me know your preferred time within that range!"
#                f"If there are unavailable time ranges, be specific, say the time ranges that are unavailable"
#            )
#        }
#    ]
#
#    while True:
#        user_msg = input("You: ")
#        if user_msg.lower() == "exit":
#            print("Ending conversation.")
#            break
#
#        messages.append({"role": "user", "content": user_msg})
#        gpt_response = get_gpt_response(messages)
#
#        text_to_speech(gpt_response)
#        print(f"GPT: {gpt_response}")
#
#        messages.append({"role": "assistant", "content": gpt_response})
#        print("-" * 50)