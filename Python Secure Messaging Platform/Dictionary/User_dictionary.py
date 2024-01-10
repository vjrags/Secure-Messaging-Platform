import os
import getpass
import json
import hashlib
from datetime import datetime

DIRNAME = os.path.dirname(__file__)
USERFILE = os.path.join(DIRNAME, 'users.json')

class User:
    def __init__(self, username, password, attempts):
        #### Initialize a user from json data ####
        self.username = username
        self.password = password
        self.attempts = attempts
        self.client = None
        self.lockOutTime = None
        self.missedMessages = []


    def badAttempt(self):
        #### Increase number of attempts ####
        self.attempts += 1

    def shouldLock(self):
        #### See if the user should be locked out ####
        return self.attempts >= 3

    def lockOut(self):
        #### locks the user out from logging in ####
        self.lockOutTime = datetime.now()
        self.attempts = 0

    def stillLocked(self):
        #### Gets current time then sees if 5 minutes have passed ####
        currTime = datetime.now()
        if self.lockOutTime is None:
            return False

        # get difference between lockout time and the current time
        difference = currTime - self.lockOutTime

        if difference.total_seconds() >= 300:  # 5 minutes in seconds
            self.lockOutTime = None
            return False
        return True


    def closeDown(self):
        #### return contents of the user into a list to export ####
        return [self.password, self.attempts]


def cls():
    #### nt (windows) = cls | unix = clear ####
    os.system('cls' if os.name == 'nt' else 'clear')


def hashPassword(password):
    #### hashes the password given ####
    encrypt = hashlib.sha512()
    encrypt.update(password.encode('utf-8'))
    return encrypt.hexdigest()


def haveUser(users, username, activeUsers):
    #### username checks on login ####
    # see if user is already logged in somewhere else
    for x in activeUsers:
        if x.username == username:
            return -1
    # if we have the user, return the object, else return 0
    for userObj in users:
        if userObj.username == username:
            # return the user object that has this username
            return 1
    return 0


def authenticate(user, password):
    #### Authenticate users ####
    for x in buildClass(readAccounts()):
        if x.username == user:
            theUser = x
    if theUser.password == password:
        return 1
    return 0


def readAccounts():
    #### read in the accounts from json file ####
    try:
        with open(USERFILE, 'r') as usersFile:
            return json.load(usersFile)
    except FileNotFoundError:
        print("User file not found. Exiting.")
        exit(1)
    except json.JSONDecodeError:
        print("No entries in user account file."
              " Please add an account and try again.")
        exit(1)


def buildClass(userDict):
    #### From a dictionary, populate a list of User objects ####
    userList = set()

    for user in userDict.keys():
        userList.add(User(user, userDict[user][0], userDict[user][1]))
    return userList


def main():
    #### Create a user in the users/passwords file ####
    users = readAccounts()
    print("Create a user")

    # loop until the two passwords match
    while True:
        username = input("Enter a username: ")
        if users.keys().__contains__(username):
            if input("This user already exists. "
                     "Do you want to change the password? (y/n)") != 'y':
                continue
        pass1 = getpass.getpass("Enter your password: ")
        pass2 = getpass.getpass("Re-enter your password: ")

        # if they match, break out of the loop
        if pass1 == pass2:
            break
        cls()
        print("Passwords don't match. Please try again.\n")

    print("Passwords match.")

    # set username with the hashed password
    # and attempts made. Start with 0 failed attempts
    users[username] = [hashPassword(pass1), 0]

    # save the contents to the json file
    with open(USERFILE, 'w') as writing:
        json.dump(users, writing)

    print("Saved account for", username)


if __name__ == '__main__':
    main()
