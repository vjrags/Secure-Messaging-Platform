#!/usr/bin/env python3
import Dictionary.User_dictionary as ut
import socket
import threading
import re
import os
import datetime

SERVER_PORT = 5002
users = ut.buildClass(ut.readAccounts())
activeUsers = []  # holds all the active users currently online

def setup(port):
    #### Sets up the server and returns the server socket ####
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(('', port))

    # no timeout set
    serverSocket.settimeout(None)
    return serverSocket


def interactWithClient(client, address):
    #### Initiates the interaction between server and client ####
    ret = loginAttempt(client)
    while ret [0]!= 1:
        print("Failed login")
        ret = loginAttempt(client)

    # send username over so client has access to it
    user = ret[1]
    username = user.username
    # find the User object related the username
    thisUser = None
    for user in users:
        if user.username == username:
            user.client = client
            activeUsers.append(user)
            thisUser = user
            
    print(username, "logged in")
    # sends a message containing the instructions how to use the client
    personalMessage(username, "\nWelcome to the chat room!\n")
    personalMessage(username, "Type a message to broadcast it to everyone on the server.\n")
    personalMessage(username, "Type @<username> <message> to send a PM to a user.\n")
    personalMessage(username, "Type !quit to log out.\n")

    # stores missed messages for the user to read when they login again
    if thisUser.missedMessages != []:
        personalMessage(username, "\nPMs you recieved while offline:\n")
        for missedMessage in thisUser.missedMessages:
            personalMessage(username, missedMessage + "\n")
        thisUser.missedMessages = []

    # shows who is online currently
    personalMessage(username, "\nOnline Users:\n")
    for activeUser in activeUsers:
        personalMessage(username, activeUser.username + "\n")
    personalMessage(username, "\n")

    # broadcast who has joined the chatroom
    broadcast(username + " has joined the chat room.", True, "")

    # start listening to the for the client's messages
    listenToClient(thisUser)


def loginAttempt(client):
    #### Manages login process and responds to errors ####
    global activeUsers
    global users

    # get the username from the client
    recvUsername = client.recv(1024).decode()

    # Check if user is in our user file
    usernameFeedback = ut.haveUser(users, recvUsername, activeUsers)
    client.send(str(usernameFeedback).encode())
    if usernameFeedback != 1:
        return usernameFeedback

        # get User object related to username
    for x in users:
        if x.username == recvUsername:
            currUser = x

    # get password from the client
    recvPassword = client.recv(1024).decode()
    # Check if password is correct
    passwordFeedback = ut.authenticate(recvUsername, recvPassword)

    # determine if the user is locked out and lock them out if they need to be
    if currUser.shouldLock():
        currUser.lockOut()
        print(currUser.username, "locked out, try again later")
        passwordFeedback = -2
    elif currUser.stillLocked():
        print(currUser.username, "locked out, try again later")
        passwordFeedback = -2

    # send the results of the password check
    client.send(str(passwordFeedback).encode())

    if passwordFeedback and currUser.lockOutTime is None:
        # nothing went wrong during attempt, log user in
        return 1, currUser
    else:
        currUser.badAttempt()
        return 0, currUser

def recordToFile(message):
    #### Records the messages being sent along with timestamps ####
    file = open('message_logs.txt', 'w')
    file.write(str(datetime.datetime.now())+": "+message+"\n")
    file.close()


def personalMessage(username, message):
    #### Send a personal message to another user ####
    recvUser = None
    for activeUser in activeUsers:
        if activeUser.username == username:
            recvUser = activeUser
    if recvUser != None:
        recvUser.client.send(str(message).encode())
    else:
        for user in users:
            if user.username == username:
                user.missedMessages.append(message)


def broadcast(message, fromServer, sender):
    #### Broadcast a message to all clients except for the one who sent it ####
    if fromServer:
        message = "Server Broadcast: " + message
    else:
        message = sender + ": " + message
   
    for user in activeUsers:
        if fromServer or sender != user.username:
            user.client.send(str(message).encode())
    recordToFile(message)


def listenToClient(user):
    #### Listens to client commands and carries out the command ####
    finishedListening = False

    while not finishedListening:
        incomingMessage = user.client.recv(1024).decode()

        if incomingMessage == "!quit":
            finishedListening = True
            activeUsers.remove(user)
            user.client = None
            broadcast(user.username + " has left the chat room.", True, "")
            print(user.username, "logged out")

        # @ signifies a personal message to a user
        # format this string and prep to send it out
        elif incomingMessage[0] == "@":
            targetUsername = re.split('@', re.split(' ', incomingMessage)[0])[1]
            message = "PM from " + user.username + ":"
            firstFragment = True
            for fragment in re.split(' ', incomingMessage):
                if firstFragment:
                    firstFragment = False
                else:
                    message = message + " " + fragment
            personalMessage(targetUsername, message)

        # otherwise, broadcast the message to everyone
        else:
            broadcast(incomingMessage, False, user.username)


def main():
    #### Entry to program. Starts setup and listens ####
    serverSocket = setup(5002)
    print("Python Secure Messaging Platform server has finished setup")

    serverSocket.listen(5)
    while True:

        # when a client is heard, accept and start a new thread
        # to log the user in and then listen for messages
        client, address = serverSocket.accept()
        client.settimeout(None)
        threading.Thread(target=interactWithClient, args=(client, address)).start()


if __name__ == '__main__':
    ut.cls()

    try:
        main()
    except Exception as ex:
        ut.cls()
        print(ex.message)
        exit(-1) # return -1 for error during execution
    except KeyboardInterrupt:
        # send a message to tell the clients to shutdown their connections
        broadcast("Closing Down Server", True, None)
        os._exit(0)
    finally:
        ut.cls()
        print('Python Secure Messaging Platform Server cleanup and exit...done!')
exit (0) # return 0 for successful completion

