import os
from telethon import TelegramClient
from flask import Flask, request
import telebot

TOKEN = '838906822:AAFoj1ZFfRD2JFvK591Nd-DCXKsFA7n74vE'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Needed Variable
user = ''
passcode = '2020'

target = ''
group = ''
target_admins = []
phone_numbers = []

api_id = '1024191'
api_hash = '12f029b11e81a9c19a5ac34a0670a385'

@bot.message_handler(commands=['start'])
def start(msg):
    """
    Initialize The Bot
    """

    bot.reply_to(msg, 'Hello, ' + msg.from_user.first_name)

    # Request for passcode
    question = bot.send_message(msg.from_user.id, "What is your access password? ")
    bot.register_next_step_handler(question, verify_user)


def verify_user(msg):
    """
    Verify User To Use Bot
    """

    global user
    if msg.text == passcode:

        user = msg.from_user
        bot.reply_to(msg, "You are a verified user. Welcome!")

        # Request target group
        question = bot.send_message(user.id, "Where Do You Want Members From Today (Please make sure this is a valid group) e.g 't.me/group' >> ")
        bot.register_next_step_handler(question, target_group)

    else:
        bot.reply_to(msg, "Sorry, you are not authorized to use this bot. Contact @codefred to get verified.")
        bot.reply_to(msg, "Thank you")


def target_group(msg):
    """
    Specify where you want users from
    """
    global target
    target = msg.text

    # Fuction to Test Group ####
    try:
        # Extracting Admin Information For the target group
        [target_admins.append(admin.user.id) for admin in bot.get_chat_administrators(target)]
    except:
        bot.send_message(user.id, "Wrong Input, Try Again")
        bot.register_next_step_handler(question, target_group)
    else:
        bot.send_message(user.id, "Target Group To Scrape, Set Successfully!!")

    # Request the group to add members
    question = bot.send_message(user.id, "Input The Link To Your Group Here >> ")
    bot.register_next_step_handler(question, user_group)


def user_group(msg):
    """
    Specify where you want to add users to
    """
    global group
    group = msg.text

    # Fuction to Test Group ####
    try:
        # Extracting Admin Information For the target group
        bot.get_chat_administrators(group)
    except:
        bot.send_message(user.id, "Wrong Input, Try Again")
        bot.register_next_step_handler(question, user_group)
    else:
        bot.send_message(user.id, "Your Group Set Successfully!!")

    # Request number to log in
    question = bot.send_message(user.id, "Input the phone number you will be using to add today here -- ")
    bot.register_next_step_handler(question, request_code)


def request_code(msg):
    """
    Sign in with the phone number received
    """

    global phone_numbers

    number = msg.text
    phone_numbers.append(number)

    # Starting the session
    client = TelegramClient(number, api_id, api_hash)

    client.start()
    if not client.is_user_authorized():
        client.send_code_request(number)

        # Request code sent
        question = bot.send_message(user.id, "Input the code you just received -- ")
        bot.register_next_step_handler(question, validate_code)
    else:
        bot.send_message(user.id, "Something went wrong bro")

def validate_code(msg):
    """
    Validating code just received
    """

    code = int(msg.text)

    client.sign_in(phone_numbers[-1], code)

    client.loop.run_until_complete(addUsers())



async def addUsers(self):
    """
    Initiating A Single Session Instance
    """

    bot.send_message(user.id, "Adding Started")

    # Collect members of target group
    groupEntity = await client.get_entity(target)
    members = await client.get_participants(groupEntity)

    channel = await client.get_entity(group)
    
    bot.send_message(user.id, '{channel.title} Adding New Users')

    added = 1
    private = 0
    stopped = 0
    n = added + private + stopped

    users = [] # Accumulated list of users to be added on one attempt
    
    for user in members:   
        if user.bot == False and user.id not in target_admins:
            users.append(user)
            if len(users) == 5:
                try:

                    # users_to_add = await client.get_entity(str(user.username))
                    # await self.client.send_message("Hutagg", "Maximum Limit For One Day Reached!!")
                    await self.client(InviteToChannelRequest(
                        channel,
                        users
                    ))
                    stopped = 0
                    added += 1

                    bot.send_message(user.id, f"Added {[i.username for i in users]}")
                    time.sleep(20)                

                except UserPrivacyRestrictedError:
                
                    private += 1
                    
                    time.sleep(1)

                except UserNotMutualContactError:

                    time.sleep(1)

                except UserChannelsTooMuchError:
                    time.sleep(1)
                    # print("There is an error to handle!")

                except PeerFloodError:

                    print("Peer Flood Error!!")
                    
                    stopped += 1
                
                    time.sleep(30)
                    
                    if stopped == 5:
                        await client.send_message(
                            user.id, 
                            f"""
                            Final report:
                            {added - 1} New Members added to {channel.title}
                            {private} Members with their privacy on!  

                            Target Group --> {groupEntity.title}
                            Stopped at {members.index(user)}

                        """)
                        break


                except Exception as e:
                    bot.send_message(user.id, '{e} Error!')
                    stopped += 1
                    time.sleep(1)

                    if stopped == 5:
                        break
        else:
            pass   

    await client.disconnect()


@bot.message_handler(func=lambda msg: True, content_types=['text'])
def echo_message(msg):
    bot.reply_to(msg, msg.text)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telegram-tool.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="127.0.0.1", port=int(os.environ.get('PORT', 5000)))