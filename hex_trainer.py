"""
Ken Sanderson
1/23/2016

Hex Trainer Alexa Skill -- Game to improve ability to convert to and from hexadecimal

"""

from __future__ import print_function
from random import randint

MAX_RANGE = 32

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
    session_attributes = {}
    should_end_session = False

    if 'Game' in intent['slots']:
        game_type = intent['slots']['Game']['value']
        session_attributes = {"game_type": game_type}
        speech_output = "Okay, let's practice " + game_type + "! "
        session_attributes = get_question(session_attributes)
        speech_output += session_attributes['question']
        reprompt_text  = session_attributes['question']
    else:
        speech_output = "Sorry, I didn't get that. Please choose a game type again."
        reprompt_text = "Sorry, I didn't get that. Please choose a game type again."
    return build_response(session_attributes, build_speechlet_response_no_card(
        speech_output, reprompt_text, should_end_session))

def get_question(session_attributes):
    answer = randint(10,MAX_RANGE)
    if session_attributes.has_key('answer'):
        # Ensure we don't ask the same question back to back
        while answer == session_attributes['answer']:
            answer = randint(10,MAX_RANGE)
    session_attributes['answer'] = answer
    if session_attributes['game_type'] == 'hex to decimal':
        # Hex to Decimal
        question = hex_to_dec_question(answer)
        session_attributes['answer_is_hex'] = False
    elif session_attributes['game_type'] == 'decimal to hex':
        # Decimal to Hex
        question = dec_to_hex_question(answer)
        session_attributes['answer_is_hex'] = True
    else:
        # Both
        if randint(0,1):
            question = hex_to_dec_question(answer)
            session_attributes['answer_is_hex'] = False
        else:
            question = dec_to_hex_question(answer)
            session_attributes['answer_is_hex'] = True
    session_attributes['question'] = question
    return session_attributes

def hex_to_dec_question(answer):
    question = hex(answer)[2:]
    if len(question) > 1:
        # Make Alexa spell out the hex
        question = ' '.join(list(question))
    question = "What is {} in decimal.".format(question)
    return question

def dec_to_hex_question(answer):
    question = "What is {} in hex.".format(answer)
    return question

def get_answer(intent, session):
    """Get answer from user, check, then ask another question"""
    session_attributes = session.get('attributes', {})
    answer = session_attributes['answer']
    answer_is_hex = session_attributes['answer_is_hex']
    user_answer = None
    if answer_is_hex:
        # Answer should be in hex
        if 'value' in intent['slots']['HexAnswerOne']:
            user_answer = intent['slots']['HexAnswerOne']['value']
            if 'value' in intent['slots']['HexAnswerTwo']:
                user_answer += intent['slots']['HexAnswerTwo']['value']
            try:
                user_answer = int(user_answer, 16)
            except:
                # catch error
                user_answer = user_answer = None
        elif 'value' in intent['slots']['DecimalAnswer']:
            # Oops, hex answer was fielded as a decimal number. Treat as hex.
            try:
                user_answer = int(intent['slots']['DecimalAnswer']['value'], 16)
            except:
                # catch error
                user_answer = user_answer = None
    else:
        # Answer should be in decimal
        if 'value' in intent['slots']['DecimalAnswer']:
            try:
                user_answer = int(intent['slots']['DecimalAnswer']['value'])
            except:
                # catch error
                user_answer = user_answer = None
        elif 'value' in intent['slots']['HexAnswerOne']:
            # Oops, decimal answer was fielded as a hex number. Treat as decimal
            try:
                user_answer = int(intent['slots']['HexAnswerOne']['value'])
            except:
                # catch error
                user_answer = user_answer = None
        if 'value' in intent['slots']['HexAnswerTwo']:
            # This shouldn't happen, raise error
            user_answer = None
    if user_answer == None:
        speech_output = "Could you repeat your answer? " + session_attributes['question']
        reprompt_text = "Could you repeat your answer? " + session_attributes['question']
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response_no_card(
            speech_output, reprompt_text, should_end_session))
    elif user_answer == answer:
        # User was right
        response = ["Correct!", "Woot!", "Yes!", "Yep!", "You're on fire!", 
                    "Killin' it!", "You got it!", "Right!",]
        speech_output = response[randint(0, len(response)-1)] + " "
    else:
        # User was wrong
        # If answer is in hex, convert to inform user of correct answer
        if session_attributes['answer_is_hex']:
            answer = ' '.join(list(hex(answer)[2:]))
        speech_output = "No, sorry the answer was {}. Let's keep trying! ".format(answer)
    session_attributes = get_question(session_attributes)
    speech_output += session_attributes['question']
    reprompt_text  = session_attributes['question']
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response_no_card(
        speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response_no_card(output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

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
