import madzpy, json, os, time
from cryptography.fernet import Fernet
from termcolor import colored
from utils import get_new_address, get_from_privkey

madz = madzpy.madz("http://shard-node.duckdns.org:6969")

class Wallet(object):
    def __init__(self):
        self.clear()
        self.key = Fernet.generate_key()
        self.f = Fernet(self.key)
        if os.path.exists("config.json"):
            self.AccountImport()
        else:
            self.AccountCreate()

    def AccountCreate(self):
        print(colored("No config.json found please create(1) or import(2) a private key!", "red", "on_grey",["underline"]))
        try:
            user_option = int(input("(1/2) >>> "))
        except:
            print(colored("Dont put a string here!", "white", "on_red", ["underline"]))
            exit(0)

        if user_option == 1:
            print(colored("Creating a new address", "blue", "on_grey", ["bold" ,"underline"]))
            new_wallet = get_new_address()
            print(colored("Public Key: ", "blue"), end="")
            print(new_wallet[0])
            hidden = new_wallet[1]

            for i in range(62):
                str_hidden = hidden[:-i] + "*"*i

            print(colored("Private Key: ", "blue"), end="")
            print(str_hidden)

            print(colored("Generating encryption key!", "blue"))
            print(colored("DO NOT FORGET THIS AS IF YOU DO YOUR FUNDS WILL BE LOST FOREVER (a very long time)\nWe recommend that you store this in multiple places\n", "red", "on_grey", ["bold", "underline"]))
            print("KEY: "+self.key.decode())

            EncryptedPriv = self.f.encrypt(new_wallet[1].encode("utf-8"))

            # Data to be written
            data = {
                "PublicAddr": new_wallet[0],
                "PrivKey": EncryptedPriv.decode()
            }
            # Saving JSON
            json.dump(data, open("config.json", "w"), indent=4)
            print(colored("Restart to use wallet", "blue", attrs=["bold"]))

        elif user_option == 2 :
            a = True
            print(colored("Enter your private key!", "blue", attrs=["underline"]))
            while a:
                PrivKey = input(">>> ")
                PubKey = get_from_privkey(PrivKey)
                if not (PubKey):
                    print(colored("Invaild Private Key!", "red", attrs=["bold"]))
                else:
                    print(colored(f"Importing address: {PubKey}\n", "blue"))
                    a = False

            EncryptedPriv = self.f.encrypt(PrivKey.encode("utf-8"))

            # Data to be written
            data = {
                "PublicAddr": PubKey,
                "PrivKey": EncryptedPriv.decode()
            }
            # Saving JSON
            json.dump(data, open("config.json", "w"), indent=4)
            print(colored("Generating encryption key!", "blue"))
            print(colored("DO NOT FORGET THIS AS IF YOU DO YOUR FUNDS WILL BE LOST FOREVER (a very long time)\nWe recommend that you store this in multiple places\n", "red", "on_grey", ["bold", "underline"]))
            print("KEY: "+self.key.decode())
            print(colored("Restart to use wallet", "blue", attrs=["bold"]))

        else:
            print(colored("INVAILD OPTION", "RED", attrs=["bold"]))
            exit(0)


    def AccountImport(self):
        a = True
        print(colored("Config.json found!", "blue", "on_grey", ["bold" ,"underline"]))
        print(colored("Enter your encryption key!", "blue"))
        while a:
            EncKey = input(">>> ")
            try:
                f = Fernet(EncKey.encode("utf-8"))
                a = False
            except:
                print(colored("KEY INVALID", "red", attrs=["bold", "underline"]))

        data = json.load(open("config.json", "r"))
        try:
            decry = f.decrypt(data["PrivKey"])
        except:
            print(colored("KEY INVALID", "red", attrs=["bold", "underline"]))
            exit(0)

        print(decry.decode())
        PubKey = get_from_privkey(decry.decode())
        if not(PubKey):
            print(colored("Encryption Key is invalid", "red"))
            exit(0)
        else:
            if PubKey == data["PublicAddr"]:
                print(colored(f"Successfully connected to {PubKey}", "blue"))
            else:
                print(colored("Unsuccessful try again!"))
                exit(0)

    def clear(self):
        time.sleep(0.25)
        if os.name == 'nt':
            _ = os.system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = os.system('clear')
        time.sleep(0.25)


if __name__ == "__main__":
    app = Wallet()
