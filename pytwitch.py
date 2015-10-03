import socket
from cfg import *

class twitch():
    def __init__(self, name='', token=''):
        self.name = name
        self.token = token

    def connect(self, channel=''):
        if len(channel) == 0:
            print('[-] No channel passed!')


def connect_to_twitch(channel=CHAN):
    irc = socket.socket()
    try:
        irc.connect((HOST, PORT))
        irc.send("PASS {}\r\n".format(PASS).encode("utf-8"))
        irc.send("NICK {}\r\n".format(NICK).encode("utf-8"))
        irc.send("JOIN {}\r\n".format(channel).encode("utf-8"))
        print('[+] Bot connected to twitch!')
        return irc
    except Exception as e:
        print(str(e))
        print('Bot did not manage to connect!')
        exit(0)


def twitch_ping_pong(irc, decoded_data):
    if decoded_data.find('PING') != -1:
        print('Bot responding to the irc ping with a pong!')
        pong_string = bytes(decoded_data.replace('PING', 'PONG'), 'utf-8')
        irc.send(pong_string)
        pause('Waiting for after the PONG', 5)


def post_to_twitch_chat(chat_string='', channel=CHAN):
    if len(chat_string) == 0:
        print('[-] No string passed to be posted to the chat!')
    print('[*] Attempting to post the string: {}'.format(chat_string))
    try:
        irc.send(bytes('PRIVMSG {} :{}\r\n'.format(channel, chat_string), 'utf-8'))
        print('[+] String posted successfully!')
        return True
    except Exception as e:
        print('[-] Exception occured: {}'.format(str(e)))
        print('[-] Closing the connection...')
        irc.close()
        pause('[+] Waiting for connection to close properly...', 5)
        return False