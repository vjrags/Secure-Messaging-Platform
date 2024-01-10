# Secure-Messaging-Platform
Group chat with encrypted messaging and authentication

Server program runs on port 5002

Server IP address: set to the desired IP address


#### To run the server
via terminal:
$ python3 server.py

#### To terminate the server program
via terminal:
use control + z

#### To run the client(s) 
via terminal:
$ python3 client.py


Source: Google Images


## Server Specifications
  - Maintains a list of usernames and passwords
    - Usernames and passwords read in from json file when starting up
    - Passwords are encrypted prior to transmission or saving
    - New users can be added using a supporting program to encrypt passwords if desired
  - Authenticates users through client requests
    - 4 failed authentications locks a user out for 5 minutes
  - Once a user has been authenticated the server does the following
    - Sends a list of online users to the newly authenticated users
    - Sends a broadcast message to all others that the user is now online
  - Relays all broadcast messages to all other online users
  - Delivers private messages directly to specified user
    - Private messages for offline users are stored and delivered when that user comes back online
  - Only Broadcast messages are stored in a message_logs text file on the server.py location. (Make sure to have write access in this directory)
  - Control + C (Shift +F5 in VS Code) terminates the server program
  - Go to Dictionary folder and run User_dictionary.py to make a new user

## Client Specifications
- Prompts a username and a password from users
- Authenticate with the server
- Repeats if needed and provide feedback to user
- Displays list of other online users when provided by server
- Displays any server provided messages
- Provides method for sending broadcast messages
- Provides method for sending private messages
- Provides method for going offline and reporting this to the server

--------------------Terminal--------------------------------
Type a message to broadcast it to everyone on the server.
Type @<username> <message> to send a PM to a user.
Type !quit to log out.
--------------------------------------------------------------
