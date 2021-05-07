# The python database class of encryption/decryption and database insertions and deletions
# It is used to manage all aspects of database. key file datastrucure is expected to be first 
# 16 bytes to be the IV. user must keep password salt safe as a security measure to make
# password more difficult to brute force.

import os, sys
import re
import secrets
from helper import print_colour, Error
import getpass


try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    from Crypto.Protocol.KDF import PBKDF2 
    from Crypto.Hash import SHA256
except ImportError as e:
    print("Error importing pycryptodome make sure its correctly installed")
    print("Install pycryptodome package then try again")
    print(e.args)
    sys.exit(1)


class Database():
    # The init code start connection to the database and return a cursor to it
    # after decrypting the database. Return True if initialization 
    # was successfull false otherwise.

    def __init__(self, first_time, database_path = "~/.pass_manager/database"):      

        self.encryption = "AES"
        self.database_path = database_path
        self.key_size = 16
        self.min_password_length = 8
        self.database = bytearray()
        

        # encryption related aspects 
        self.nonce_length = 16
        self.tag_length = 16
        self.enc_key = b""
        self.password_salt = b''
        self.tag = b""
        self.iv = b""

        # Start Initialziation
        if not first_time:
            self.__get_key_data()
            if self.__decrypt():     # Successfull decryption
                print_colour("GREEN", "[+] Database decrypted correctly ")
            else:               # wrong key
                raise Error("[+] Password is incorrect")
        else:
            self.__setup()
            t, array = self.__encrypt()
            # then write data to the file
            if t:
                with open(os.path.expanduser(self.database_path), "wb") as f:
                    f.write(array[0])
                    f.write(array[1])
                    f.write(array[2])
                print_colour("GREEN", "[+] Finished setup completely")
            else:
                raise Error("[+] Cant complete setup")
            

    def __randomly_generate_password(self):
        # generate a randomly generated password and return it 

        choice = "0123456789qazwsxedcrfvtgbyhnujmiklopQWERTYUIOPLKJHGFDSAZXCVBNM!@#$%^&*()?><"

        print("[+] what is the length of the password you want")
        length = int(input("[+] NOTE: Minumum length is {} characters: ".format(
            self.min_password_length)))

        while True:
            if length < self.min_password_length:
                length = int(input("[+] Enter a valid accepted minumum length: "))
                continue
            break

        password = "".join(secrets.choice(choice) for i in range(int(length)))
        return password        


    def __setup(self):
        print_colour("BLUE", "[+] ---setting up program---")
        print("\t[+] password must be minumum length of 8. Have numbers,")
        print("\t[+] upper, lower and symbols characters or we can choose for you a password")
        _ = input("\t[+] if you want us to Choose a password for you enter [c/C]")
        while True:            
            if _ in 'cC':
                print_colour("YELLOW", "[+] Generatig the master password make sure it gave suffient length")
                p1  = self.__randomly_generate_password()
                print("[+] Generated Password: ", end='')
                print_colour("GREEN", p1)
                print_colour("YELLOW", "[+] Please save this password in a safe place")
                print_colour("YELLOW", "[+] If you lose your password or salt your data will be lost")
                break

            else:
                p1 = getpass.getpass("[+] Enter Password to use: ")
                if not self.__check_password_strength(p1):
                    print_colour("RED", "[+] Password doesnt meet requirements try again with a valid password")
                    continue
                p2 = getpass.getpass("[+] Verify Password: ")
                if p1 == p2:
                    break
        
        print("[+] Now to prevent bruteforce attacks against password used")
        print("[+] We use a salt that make sure that bruteforce attacks more difficult")
        print("[+] also the salt act as a second authontication in case password is leaked")
        print_colour("YELLOW", "[+] ONLY IF: the salt is kept private and not shared")
        s1 = input("\n\t[+] Enter salt: ")
        s2 = input("\t[+] Verify salt: ")
        if s1 == s2:
            self.__get_key_data(cred=[p1, s1])
            return


    def __get_key_data(self, cred = []):
        # This function get key data from user then set self patameters accordingly to be used
        # by other functions such as __decrypt but this function doesnt check if entered 
        # keys are correct.
        
        if cred:
            entered_key = cred[0]
            entered_salt = cred[1]
        else:
            entered_key = getpass.getpass("[+] Enter password: ")
            entered_salt = input("[+] Enter salt: ")

        sha = SHA256.new()
        sha.update(bytes(entered_salt, encoding="ascii"))
        self.password_salt = sha.digest()[:16]

        self.enc_key = PBKDF2(bytes(entered_key, encoding="ascii"), self.password_salt, 
                    64, count=1000000, hmac_hash_module=SHA256)[:16]
        

    def __encrypt(self):
        # this function encrypt self.database using self.enc_key by using AES_GCM mode 
        # and return a list of nonce, ciphertext, tag. Return true if encryption was 
        # successful along with data and false with None otherwise.
        
        aes = AES.new(self.enc_key, AES.MODE_GCM)
        try:
            ciphertext, tag = aes.encrypt_and_digest(self.database)
        except Exception as e:
            return False, None
        else:
            nonce = aes.nonce
            return True, [nonce, ciphertext, tag]


    def __decrypt(self):

        # Now start decrypting database self.database_path        
        # return True if decryption successfull and save result to database false otherwise

        f = open(os.path.expanduser(self.database_path), "rb")
        encrypted_data = f.read()
        nonce = encrypted_data[0 : self.nonce_length]
        ciphertext = encrypted_data[self.nonce_length : -self.tag_length]
        tag = encrypted_data[-self.tag_length: ]
        
        try:
            aes = AES.new(self.enc_key, AES.MODE_GCM, nonce=nonce)
            plaintext = aes.decrypt_and_verify(ciphertext, tag)
        except (ValueError, KeyError):
            return False
        else:
            self.database = bytearray(plaintext)
            return True
        finally:
            f.close()


    def __check_password_strength(self, password: str):
        # return true if password is strong false if not
        _num = "0123456789"
        _upper = "QWERTYUIOPLKJHGFDSAZXCVBNM"
        _lower = "qwertyuioplkjhgfdsazxcvbnm"
        _symbols = "!@#$%^&*()?><"
        num = 0
        upper = 0
        lower = 0
        symbols = 0
        
        for char in password:
            if char in _num:    
                num += 1
                continue
            if char in _upper: 
                upper += 1
                continue
            if char in _lower:
                lower +=1
                continue
            if char in _symbols:
                symbols += 1
                continue
            return False

        if num == 0 or symbols == 0 or upper == 0 or lower == 0:
            return False
        else:
            return True


    def __insert(self, string: bytearray):
        # Insert a new record to self.database
        # First check if its valid (have a new line at end)
        self.database.extend(string)
        self.database.append(0x0A)
        return True


    def __retrive(self, search_term: bytearray):
        # retrive a record from self.database
        regex = bytearray(b"[A-Za-z0-9]*")
        regex.extend(search_term)
        regex.extend(b"[A-Za-z0-9]*")
        result = re.search(bytes(regex), bytes(self.database))
        return result
    

    def save_record(self):
        # This is user function used to enter a new record to the self.database data
        username = input("[+] Username(M): ")
        if username == None:
            print("[+] username is mandatory field")
            return 0
        url = input("[+] URL: ")
        comment = input("[+] Comment: ")
        password = self.__randomly_generate_password()

        record = ', '.join([username, url, comment, password])
        # Now insert record into the database
        self.__insert(bytearray(record, encoding="ascii"))
        print_colour("GREEN", "[+] inserted record successfully to the database")
        return True


    def search(self, search: str):
        result = self.__retrive(bytearray(search, encoding="ascii"))
        if result:
            start = result.span()[0]
            end = result.span()[1]
            for x in range(start, -1, -1):
                if self.database[x] == 0x0A:
                    start = x + 1
            for x in range(end, len(self.database)):
                if self.database[x] == 0x0A:
                    end = x 

            print_colour("GREEN", "[+] Found this record: {}".format(str(
                self.database[start:end], encoding="ascii")))
            return True
        else:
            print_colour("RED", "[+] Didnt find result please make sure to have some details")
            return False
    
    
    def close(self):
        # This function encrypt the database then save it correctly formated to the file
        t, array = self.__encrypt()
            # then write data to the file
        if t:
            with open(os.path.expanduser(self.database_path), "wb") as f:
                f.write(array[0])
                f.write(array[1])
                f.write(array[2])
            print_colour("GREEN", "[+] Closing program safely")
            sys.exit(0)
        else:
            raise Error("[+] CRITICAL: Coudnt close program sagely")
