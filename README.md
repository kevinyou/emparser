# EMParser

Retrieves, parses, and then formats the JSON game data files from epicmafia.com.

# Usage

Currently, it is a Python 3.4.0+ script usable in any command line interface.

Input supports local or online games. Game files can be downloaded by the user manually and, if placed in the same directory as the working directory, loaded automatically. Otherwise, the script can request data files from https://s3.amazonaws.com/em-records/xxx or https://s3.amazonaws.com/em-records-forever/xxx. Data files will be saved locally.

Output is currently only plaintext.
