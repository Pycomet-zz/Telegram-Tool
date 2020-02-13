# This code is written by CodeFredy on Fiverr

# Import necessary modules
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.functions.channels import InviteToChannelRequest
import sys
from telethon.errors.rpcerrorlist import UserPrivacyRestrictedError, PeerFloodError, UserNotMutualContactError, UserChannelsTooMuchError
import time
import random
import os
import glob

class TG_tool(object):

    def __init__(self, targetGroup, group, start):
        self.sessions = glob.glob("sessions/*.session")
        self.targetGroup = targetGroup
        self.id = '1024191'
        self.hash = '12f029b11e81a9c19a5ac34a0670a385'
        self.group = group
        self.start = start
        self.session = ''

    def create(self):
        """Initiating A Single Session Instance"""

        try:
            lastSession = self.sessions[-1].split('.')[0]
            a = lastSession.split("\\")[1]

            b = a.split("session")[1]

            b = int(b) + 1
            newSession = "session" + str(b) # Giving  this session an index preceeding the existing one

            # Starting New Session
            self.client = TelegramClient(f"sessions/{newSession}", self.id, self.hash)
            self.client.start()

            self.client.loop.run_until_complete(self.addUsers())

            self.quit()

        except IndexError as e:

            self.client = TelegramClient("sessions/session1", self.id, self.hash).start()

            self.client.loop.run_until_complete(self.addUsers())

            self.quit()

    def run(self):
        """Monitoring all sessions in a loop"""

        print("Starting Telegram Software")
        for each in self.sessions:
            self.session = str(each)
            self.client = TelegramClient(each, self.id, self.hash).start()

            self.client.loop.run_until_complete(self.addUsers())

        self.quit()


    async def addUsers(self):
        """Initiating A Single Session Instance"""

        groupEntity = await self.client.get_entity(self.targetGroup)
        members = await self.client.get_participants(groupEntity)
        channel = await self.client.get_entity(self.group)
        
        print(f'{channel.title} Adding New Users')

        added = 1
        private = 0
        stopped = 0
        n = added + private + stopped

        users = [] # Accumulated list of users to be added on one attempt
        
        for user in members[self.start::5]:
        # if added % 50 == 0:
        #     await client.send_message("Hutagg", "Maximum Limit For One Day Reached!!")
        #     added += 1
        #     time.sleep(1000)
     
            if user.bot == False:
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

                        # print(f"Added {user.username} -- {members.index(user)}")
                        time.sleep(40)                

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
                #             await self.client.send_message(
                #     "Hutagg", 
                #     f"""
                #     Final report:
                # {added - 1} New Members added to {channel.title}
                # {private} Members with their privacy on!  
                
                # Target Group --> {group.title}
                # Stopped at {members.index(user)}

                #     """)
                            self.start += n
                            break


                    except Exception as e:
                        print(f'{e} Error!')
                        stopped += 1
                        time.sleep(1)

                        if stopped == 5:
                            self.start += n

                            break
            else:
                pass   

        print("DONE... Started Adding For The Next User")


    def quit(self):
        """Ending One Session"""
        self.client.disconnect()







while True:
    target = input("Where Do You Want Members From Today (Please make sure this is a valid group) >> ")
    group = input("Input The Link To Your Group Here >> ")
    start = int(input("Where do you wish to start from?"))

    while target:

        bot = TG_tool(target, group, start)

        print("Press '1' To Create A New User Instance And '2' To Run The Software >> ")
        var = str(input("-->  "))

        if var == '1':

            bot.create()

        elif var == '2':

            bot.run()

        else:

            print("Wrong Input!! Try again.")

