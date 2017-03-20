import os
import time
from slackclient import SlackClient
from urllib.request import urlopen
import json
from pprint import pprint


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
PRECIO = "btc"
STATS = "stats"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Usar las opciones validas *" + PRECIO + " o " + STATS + "* para obtener valores del mercado"
    if command.startswith(PRECIO):
        u = urlopen('https://www.surbtc.com/api/v1/markets/btc-clp/indicators')
        resp = json.loads(u.read().decode('utf-8'))
        response = resp["indicators"][0]["value"] /100
    elif command.startswith(STATS):
        u = urlopen('https://www.surbtc.com/api/v1/markets/btc-clp/indicators')
        resp = json.loads(u.read().decode('utf-8'))
        r = resp["indicators"][3]["value"] * 100
        s = resp["indicators"][4]["value"] * 100
        stat_24 = round(r,2)
        stat_7 = round(s,2)
        response = "Variacion en 7d" + str(stat_7) + "%"  + " ---- " + "Variacion en 24hs" + str(stat_24) + "%"
        

    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


#    if command.startswith(STATS):
 #       u = urlopen('https://www.surbtc.com/api/v1/markets/btc-clp/indicators')
 #       resp = json.loads(u.read().decode('utf-8'))
 #       stat = resp["indicators"][3]["value"] * 100	
  #      response = "Sure...write some more code then I can do that!"
   #     slack_client.api_call("chat.postMessage", channel=channel, text=stat , as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
