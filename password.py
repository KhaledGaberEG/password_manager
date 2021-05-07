# the database file is a simple CSV file that will be in following format
# usename(M), url, comment, password(M), OTHERS


import sys
import os
import database
import signal
from helper import print_colour

if __name__ == "__main__":
    PATH = "~/.pass_manager/database"
    MODE = 0o740
    first_time = True

    print_colour("GREEN", "------- Starting Inialization -----------")
    # First we need to check if this is the very first time the program is run
    # or there already exits a folder containng database. so we create a hidden folder in home
    # directory as ~/.pass_manager

    if os.path.isfile(os.path.expanduser(PATH)):
        print_colour("GREEN", "[+] Already configured database system")
        first_time = False

    else:
        # else make all directorys needed 
        try:
            os.makedirs(os.path.expanduser(os.path.dirname(PATH)))
        except:
            print_colour("YELLOW", "[+] Directory already present so creating database")
            f = open(os.path.expanduser(PATH), 'w')
            f.close()
        else:
            f = open(os.path.expanduser(PATH), 'w')
            f.close()
            print_colour("GREEN", "[+] Database created")

    
    # ***************************************
    
    # database is present and ready to be connected to it.
    # first open it then use it ta start program.
    data = database.Database(first_time=first_time)
    def handler(signum, e):
        print_colour("RED", "SAVING DATABASE")
        data.close()
    signal.signal(signal.SIGINT, handler)


    print_colour("GREEN", "[+] Starting the program to exit enter q or (Q)")
    print_colour("GREEN", "[+] to view a password record enter (v) or(V)")
    print_colour("GREEN", "[+] to insert a new password record enter (i) or(I)")
    print_colour("GREEN", "[+] This info banner will appear only once make sure you remember options")
    

    while True:
        print_colour("PROMPT", "[+] RESPONSE >> ", end="")
        response = input()
        if response in 'qQ':
            data.close()

        elif response in 'Vv':
            print("[+] Search using part of any record detail like URL, username or comment")
            
            while True:
                search = input("[+] Search term: ")
                if data.search(search):
                    break
                else:
                    print_colour("RED", "[+] Didnt find the record do you want to keep searching or exit")
                    print_colour("RED", "[+] Press q or Q to exit to main menu")
                    _ = input(">>")
                    if _ in 'qQ':
                        break
                    

        elif response in 'Ii':
            while True:
                if data.save_record():
                    break
                else:
                    print("[+] Make sure to enter a valid password or exit")

        else:
            print("[+] please select a valid choice or exit using ctrl-c")
