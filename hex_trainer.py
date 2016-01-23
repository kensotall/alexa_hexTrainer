"""
Ken Sanderson
1/23/2016

Hex Trainer Alexa Skill -- Game to improve ability to convert to and from hexadecimal

"""

from __future__ import print_function
from random import randint

MAX_RANGE = 20

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Skill's application ID to prevent someone else from configuring a skill that 
    sends requests to this function.
    """
    if (event['session']['application']['applicationId'] !=
             "amzn1.echo-sdk-ams.app.d4ed5480-ef4a-4390-9a5d-a04bdac6c0f5"):
         raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GameTypeIntent":
        return set_game_type_in_session(intent, session)
    elif intent_name == "AnswerIntent":
        return get_answer(intent, session)
    elif (intent_name == "PlayIntent") or (intent_name == "AMAZON.StartOverIntent") or (intent_name == "AMAZON.HelpIntent"):
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """At app opening"""
    session_attributes = {}
    card_title = "Hex Trainer - by Ken"
    speech_output = "Welcome to Ken's Hex Trainer App. " \
                    "Which type of practice would you like? " \
                    "decimal to hex, " \
                    "hex to decimal, " \
                    "or both."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please choose decimal to hex, hex to decimal, or both. "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_game_type_in_session(intent, session):
    """ Sets the game type in the session and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Game' in intent['slots']:
        game_type = intent['slots']['Game']['value']
        session_attributes = {"game_type": game_type}
        speech_output = "Okay, let's practice " + game_type + "! "
        (question, session_attributes) = get_question(session_attributes)
        speech_output += question
        reprompt_text = question        
    else:
        speech_output = "Sorry, I didn't get that. Please choose a game type again."
        reprompt_text = "Sorry, I didn't get that. Please choose a game type again."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_question(session_attributes):
    if session_attributes['game_type'] == 'hex to decimal':
        (question, session_attributes) = get_hex_question(session_attributes)
    elif session_attributes['game_type'] == 'decimal to hex':
        (question, session_attributes) = get_dec_question(session_attributes)
    else:
        if randint(0,1):
            (question, session_attributes) = get_hex_question(session_attributes)
        else:
            (question, session_attributes) = get_dec_question(session_attributes)
    return (question, session_attributes)

def get_hex_question(session_attributes):
    answer = randint(10,MAX_RANGE)
    session_attributes['answer'] = answer
    question = hex(answer)[2:]
    if len(question) > 1:
        # Make Alexa spell out the hex
        question = '.'.join(list(question)) + '.'
    question = "What is {} in decimal?".format(question)
    return (question, session_attributes)

def get_dec_question(session_attributes):
    answer = randint(10,MAX_RANGE)
    session_attributes['answer'] = answer
    question = "What is {} in hex?".format(answer) 
    return (question, session_attributes)

def get_answer(intent, session):
    session_attributes = session['attributes']
    """Get answer from user, check, then ask another question"""
    answer = session['attributes']['answer']
    if "DecimalAnswer" in intent['slots']:
        user_answer = int(intent['slots']['DecimalAnswer']['value'])
    elif "HexAnswerOne" in intent['slots']:
        user_answer = intent['slots']['HexAnswerOne']['value']
        if "HexAnswerTwo" in intent['slots']:
            user_answer += intent['slots']['HexAnswerTwo']['value']
        user_answer = int(user_answer, 16)
    else:
        speech_output = "Could you repeat your answer?"
        reprompt_text = "Could you repeat your answer?"
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            '', speech_output, reprompt_text, should_end_session))
    if user_answer == answer:
        response = ["Correct!", "Woot!", "Yup!", "Damn, son", "On fire!"]
        speech_output = response[randint(0, len(response))] + " "
    else:
        speech_output = "No, sorry the answer was {}. Let's keep trying! ".format(answer)
    (question, session_attributes) = get_question(session_attributes)
    speech_output += question
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        '', speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
