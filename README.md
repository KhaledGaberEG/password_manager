# Python password_manager
A python simple implementation of a password manager that use **pycryptodome** for file encryption and decryption. It stores the passwords it a simple csv file that gets encrypted using a user supplied password(master password) or he can allow the module to choose a randomly generated password.

## NOTES:

- **Closing program in the middle of program can cause data loss always make sure to close it properly either using ctrl-c or `q` in prompt
 which will make any changes to be commited to the csv file**
- When inserting a new record to the database Its not allowed to use your own password. We generate a random new password for you.
- All encryptions are done using AES mode with key being driven using the password and password salt being passed to **PBKDF** function.
- The csv file is being encrypted using AES_GCM mode with 128 bit key.

### How to run ?
run the program by running ```python3 password.py``` make sure all other files ```database.py``` and ```helper.py``` are in the same directory and that ```pycryptodome``` is installed.
