from stem.process import launch_tor_with_config
from stem import Signal
from stem.control import Controller
import time
import atexit
import argparse
import requests

def cleanup():
    # try to terminate tor
    try:
        tor.terminate()
    except:
        pass

    print('everything cleaned up!')

def sendMessage(username, msg, msgNumber, session):
    # make a GET request to the given url and check the status code
    r = session.get('https://{}.sarahah.com'.format(username))
    if r.status_code != 200:
        print('Error making GET request #{}. Server returned code: {}'.format(msgNumber, r.status_code))
    
    # split text and get the user ID
    tstr = r.content.decode().split('<input id="RecipientId" type="hidden" value="')[1]
    userId = tstr.split('"')[0]

    # split text and get the Request Verification Token
    tstr = r.content.decode().split('<input name="__RequestVerificationToken" type="hidden" value="')
    reqToken = tstr[1].split('"')[0]

    # prepare url and data to post
    url = 'https://{}.sarahah.com/Messages/SendMessage'.format(username)
    data = {
        '__RequestVerificationToken':reqToken,
        'userId':userId,
        'text':msg
    }

    # make POST request
    p = session.post(url, data=data)
    # if the status code is 400, the message was not sent
    print('Posted #{}. Server returned code {}'.format(msgNumber, p.status_code))

# create argument parser
ap = argparse.ArgumentParser('flood sarahah with messages')
ap.add_argument('-n', '--num_msgs', type=int, default=10,
                help='number of messages to send')
ap.add_argument('-u', '--username', type=str,
                help='username to send the message to')
ap.add_argument('-m', '--msg', type=str,
                help='message that would be sent')
# parse the arguments                
args = ap.parse_args()

# register a cleanup function that will be called when the program exits
atexit.register(cleanup)

# get the start time
start_time = time.clock()

# create session with tor proxy
session = requests.session()
session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9050'
session.proxies['https'] = 'socks5h://localhost:9050'

# get the values of the arguments
num_messages = args.num_msgs
userName = args.username
message = args.msg

# loop and send messages
for i in range(num_messages):

        # (re)start tor every 3 iterations
        if i % 3 == 0:
            tor = launch_tor_with_config(config = {'ControlPort': '9051', 
                                        'CookieAuthentication':'1',
                                        'HashedControlPassword':'16:207CFF8D059C562460B96D50FF4759A2214E1FF5259F3CAF8109C639C4'})
        
        # send the message
        sendMessage(userName, message, i, session)

        # uncomment the following line if the internet connection is slow
        # time.sleep(3)

        # kill the tor process every 3 iterations
        if (i + 1) % 3 == 0 or i == num_messages - 1:
            tor.terminate()

# print the execution time of the program
print('\nexecution time: {} seconds'.format(time.clock() - start_time))
