#!/usr/bin/env python3
import Dictionary.User_dictionary as ut
import getpass
import threading
from socket import *
import os

def setup():
    #### Sets up the client's socket and returns the socket ####
    serverName = 'localhost'  # placeholder, should run on a server
    serverPort = 5002
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.settimeout(None)
    return clientSocket


def loginAttempt(clientSocket):
    #### Prompts user for username and password and then talks to client ####

    username = input("Enter a username: ")
    password = ut.hashPassword(getpass.getpass("Enter a password: "))

    # send username
    clientSocket.send(username.encode())

    # get the feedback from the server about username
    usernameFeedback = int(clientSocket.recv(1024).decode())

    # tell user about issues with username
    if usernameFeedback == 0:
        print("Invalid login: the given username does not exist")
        return 0
    elif usernameFeedback == -1:
        print("Invalid login: user is already logged in on another device")
        return 0

    # send password to server
    clientSocket.send(password.encode())

    # get server feedback about the password
    passwordFeedback = int(clientSocket.recv(1024).decode())

    # report to the user about issues with password
    if passwordFeedback == 0:
        print("Invalid login: the given password is incorrect")
        return 0
    elif passwordFeedback == -2:
        print("Invalid login: user is locked out")
        return 0

    return username


def login(clientSocket):
    ### Carry out login operations and let the user start sending messages ####
    username = loginAttempt(clientSocket)
    while username == 0:
        username = loginAttempt(clientSocket)
    readyForUse(clientSocket, username)


def readyForUse(clientSocket, username):
    #### Send start a thread that listens to server and listen for user input ####

    # start thread to listen to server messages
    threading.Thread(target=listenToServer, args=(clientSocket,)).start()
    message = None

    # wait for user input
    while message != "!quit":
        message = input("")
        clientSocket.send(message.encode())
    os._exit(0)


def listenToServer(clientSocket):
    #### Listen to messages from the server ####
    while True:
        message = clientSocket.recv(1024).decode()
        print(message)

        # if we receive this message, shut down the client TCP connection
        # and exit the program
        if message == "Server Broadcast: Closing Down Server":
            print("Exiting")
            clientSocket.shutdown(SHUT_RDWR)
            os._exit(0)


def main():
    #### Entry to program ####
    clientSocket = setup()
    login(clientSocket)

if __name__ == '__main__':
    main()
