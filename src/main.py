import os
import re
import requests
from flask import Flask, request
from slack_sdk import WebClient
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler


app = Flask(__name__)

client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
bolt_app = App(token=os.environ.get('SLACK_BOT_TOKEN'),
               signing_secret=os.environ.get('SLACK_SIGNING_SECRET'))


@bolt_app.message(re.compile('(hi|hello|hey) pokebot'))
def greeting(payload: dict, say: Say):
    user = payload.get('user') 

    response = client.chat_postMessage(
            channel=payload.get('channel'),
            thread_ts=payload.get('ts'),
            text=f'Hi <@{user}>, How can I help you?')
    
    return response

@bolt_app.command('/help')
def show_help(say, ack):
    ack()
    text = {
        "text": "This is the help menu",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Help!:confused::information_source:",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "I support the following commands!",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "/help \t-\t Show this help menu"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "/all \t-\t Show all known pokemons"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "/name \t-\t Find pokemon by name"
                }
            },

        ]
    }

    say(text=text)

@bolt_app.command('/all')
def show_all(say, ack):
    ack()

    pokemon_list = requests.get('http://localhost/api/v1/pokemon').json()

    pokemon_info = ''
    for pokemon in pokemon_list['data']:
        for p in pokemon:
            pokemon_info += f'{p.capitalize()}: {pokemon[p]}\n'

        pokemon_info += "\n\n"

    text = {
        "text": "Pokemons list",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "List of current pokemons:dart::nerd_face:",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": pokemon_info,
                }
            }
        ]
    }

    say(text=text) 

@bolt_app.command('/info')
def show_pokemon(payload, say, ack):
    ack()

    pokemon_id = payload.get('text')
    pokemon = requests.get(f'http://localhost/api/v1/pokemon/{pokemon_id}').json()

    pokemon_info = ''

    for i in pokemon['data']:
        pokemon_info += f'{i.capitalize()}: {pokemon["data"][i]}\n'

    text = {
        "text": "Pokemons list",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Pokemon Information!:dart:",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": pokemon_info,
                }
            },
        ]
    }
    
    say(text=text)


handler = SlackRequestHandler(bolt_app)

@app.route('/pokebot/events', methods=['POST'])
def slack_events():
    return handler.handle(request)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
