"""
Ken Sanderson
1/23/2016

Hexercise - Alexa Skill -- Game to improve ability to convert to and from hexadecimal

"""

from __future__ import print_function
from random import randint

MIN_RANGE = 10
MAX_RANGE = 32

homophones = {'zero':'0','one':'1','won':'1','two':'2','to':'2','too':'2','three':'3','four':'4','for':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','hey':'a','be':'b','bee':'b','see':'c','half':'f'}

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
    elif intent_name == "DifficultyIntent":
        return set_difficulty(intent, session)
    elif intent_name == "AnswerIntent":
        return get_answer(intent, session)
    elif intent_name == "ScoreIntent":
        return get_score(session)
    elif intent_name == "AMAZON.StopIntent":
        return get_score_then_quit(session)
    elif (intent_name == "PlayIntent") or (intent_name == "AMAZON.StartOverIntent"):
        return get_welcome_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_help(session)
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
    """At app opening or restart"""
    session_attributes = {}
    card_title = "Hexercise - by Ken"
    speech_output = "Welcome to Ken's Hexercise App. " \
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

def get_help(session):
    session_attributes = session.get('attributes', {})
    speech_output = "Here are some things you can try: " \
                    "start a mixed game, " \
                    "decimal to hex, " \
                    "start over, " \
                    "tell me the score, " \
                    "You can also say stop if you are done. " \
                    "So, how can I help?"
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response_no_card(
        speech_output, reprompt_text, should_end_session))


def set_game_type_in_session(intent, session):
    """ Sets the game type in the session. """
    session_attributes = {}
    session_attributes['score'] = 0
    should_end_session = False

    if 'Game' in intent['slots']:
        game_type = intent['slots']['Game']['value']
        session_attributes = {"game_type": game_type}
        speech_output = "Great, now set the difficulty level. " \
                        "Choose from: easy, medium, hard, or genius. "
        reprompt_text = "Please choose: easy, medium, hard, or genius. "
        should_end_session = False
    else:
        speech_output = "Sorry, I didn't get that. Please choose a game type again."
        reprompt_text = "Sorry, I didn't get that. Please choose a game type again."
    return build_response(session_attributes, build_speechlet_response_no_card(
        speech_output, reprompt_text, should_end_session))

def set_difficulty(intent, session):
    session_attributes = session.get('attributes', {})
    if not session_attributes.has_key('score'):
        session_attributes['score'] = 0
    if 'Difficulty' in intent['slots']:
        difficulty = intent['slots']['Difficulty']['value']
        if difficulty == 'easy':
            MIN_RANGE = 0
            MAX_RANGE = 32
        elif difficulty == 'medium':
            MIN_RANGE = 10
            MAX_RANGE = 48
        elif difficulty == 'hard':
            MIN_RANGE = 10
            MAX_RANGE = 128
        elif difficulty == 'genius':
            MIN_RANGE = 10
            MAX_RANGE = 255
        else:
            speech_output = "Sorry, I didn't get that. Please choose a difficulty level again."
            reprompt_text = "Sorry, I didn't get that. Please choose a difficulty level again."
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response_no_card(
                speech_output, reprompt_text, should_end_session))
        session_attributes['difficulty'] = difficulty
        speech_output = "Okay, let's practice {} at the {} level! ".format(session_attributes['game_type'], difficulty)
        if difficulty == 'genius':
            speech_output = 'Good luck brainiac!'
        session_attributes = get_question(session_attributes)
        speech_output += session_attributes['question']
        reprompt_text  = session_attributes['question']
    else:
        speech_output = "Sorry, I didn't get that. Please choose a difficulty level again."
        reprompt_text = "Sorry, I didn't get that. Please choose a difficulty level again."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response_no_card(
        speech_output, reprompt_text, should_end_session))

def get_question(session_attributes):
    answer = randint(MIN_RANGE, MAX_RANGE)
    if session_attributes.has_key('answer'):
        # Ensure we don't ask the same question back to back
        while answer == session_attributes['answer']:
            answer = randint(MIN_RANGE, MAX_RANGE)
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
    if not session_attributes.has_key('score'):
        session_attributes['score'] = 0

    # Error handling
    if not session_attributes.has_key('answer'):
        # Uhoh, something went wrong. Try to sort out the issue.
        if session_attributes.has_key('game_type'):
            if session_attributes.has_key('difficulty'):
                # Shouldn't happen. We are not in the right code flow. Raise error.
                speech_output = "I'm sorry, something went wrong. Please ask to start over."
                reprompt_text = "Sorry, something went wrong. Please ask to start over."
            else:
                # Haven't set difficulty
                speech_output = "Sorry, I didn't get that. Please choose a difficulty level."
                reprompt_text = "Please choose a difficulty level. Easy, medium, hard, or genius"
        else:
            # Haven't set game type
            speech_output = "Sorry, I didn't get that. Please choose a game type."
            reprompt_text = "Please choose decimal to hex, hex to decimal, or both. "
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response_no_card(
            speech_output, reprompt_text, should_end_session))

    answer = session_attributes['answer']
    answer_is_hex = session_attributes['answer_is_hex']
    user_answer = None
    if answer_is_hex:
        # Answer should be in hex
        if 'value' in intent['slots']['HexAnswerOne']:
            hex_one = intent['slots']['HexAnswerOne']['value']
            if hex_one in homophones.keys():
                hex_one = homophones[hex_one]
            user_answer = hex_one
            if 'value' in intent['slots']['HexAnswerTwo']:
                hex_two = intent['slots']['HexAnswerTwo']['value']
                if hex_two in homophones.keys():
                    hex_two = homophones[hex_two]
                user_answer += hex_two
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
            user_answer = None
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
        else:
            user_answer = None
        if 'value' in intent['slots']['HexAnswerTwo']:
            # This shouldn't happen, raise error
            user_answer = None
    if user_answer == None:
        speech_output = "Could you repeat your answer? " + session_attributes['question']
        reprompt_text = "Could you repeat your answer? " + session_attributes['question']
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            'error', speech_output, reprompt_text, should_end_session))
    elif user_answer == answer:
        # User was right
        response = ["Correct!", "Woot!", "Yes!", "Yep!", "You're on fire!", 
                    "Killing it!", "You got it!", "Right!",]
        speech_output = response[randint(0, len(response)-1)] + " "
        session_attributes['score'] += 1
        if (session_attributes['score'] % 10 == 0) and (session_attributes['score'] != 0):
            # update user on score
            speech_output += "{} points, keep going! ".format(session_attributes['score'])
    else:
        # User was wrong
        # If answer is in hex, convert to inform user of correct answer
        if session_attributes['answer_is_hex']:
            answer = ' '.join(list(hex(answer)[2:]))
        speech_output = "No, sorry the answer was {}. Let's keep trying! ".format(answer)
        session_attributes['score'] -= 2
        # Don't go negative, that's just mean
        if session_attributes['score'] < 0:
            session_attributes['score'] = 0
    session_attributes = get_question(session_attributes)
    speech_output += session_attributes['question']
    reprompt_text  = session_attributes['question']
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response_no_card(
        speech_output, reprompt_text, should_end_session))

def get_score(session):
    """Get user score"""
    session_attributes = session.get('attributes', {})
    if session_attributes.has_key('score'):
        score = session_attributes['score']
    else:
        score = 0
    if score == 1:
        speech_output = "You have {} point. ".format(score)
    else:
        speech_output = "You have {} points. ".format(score)

    # If game type not set yet, do it (shouldn't happen)
    if not session_attributes.has_key('game_type'):
        speech_output += "Which type of practice would you like? " \
                         "decimal to hex, " \
                         "hex to decimal, " \
                         "or both."
        reprompt_text = "Please choose decimal to hex, hex to decimal, or both. "
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response_no_card(
            speech_output, reprompt_text, should_end_session))
        
    # Now ask the previous question again (or ask a new one if can't access it)
    if not session_attributes.has_key('question'):
        session_attributes = get_question(session_attributes)
    speech_output += session_attributes['question']
    reprompt_text  = session_attributes['question']
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response_no_card(
        speech_output, reprompt_text, should_end_session))
   
def get_score_then_quit(session):
    """Get user score then quit"""
    session_attributes = session.get('attributes', {})
    if session_attributes.has_key('score'):
        score = session_attributes['score']
    else:
        score = 0
    if score > 1:
        speech_output = "You scored {} points. Thanks for playing! ".format(score)
    else:
        speech_output = "Thanks for playing! ".format(score)
    reprompt_text = ""
    should_end_session = True
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
