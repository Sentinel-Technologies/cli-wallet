import madzpy, json, os, time
from cryptography.fernet import Fernet
from termcolor import colored
from utils import get_new_address, get_from_privkey, is_address
import maskpass
import progress
from signal import signal, SIGINT

class NetFuncs(object):

    def __init__(self, Address : str, PrivateKey : str):
        self.madz = madzpy.madz("http://shard-node.duckdns.org:6969")
        self.Address = Address
        # Try to connect to Node
        try:
            self.madz.balance(self.Address)
        except:
            print(colored("Unable to connect to node!", "red"))
            exit(0)

    def GetBalance(self):
        return self.madz.balance(self.Address)

    def IsAddr(self, Address):
        if self.madz.is_address(Address):
            return True
        else:
            return False

    def Send(self, Privkey, From, To, Amount):
        return self.madz.transaction(Privkey, From, To, Amount)

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
            print(colored("Creating a new address", "blue", attrs=["bold" ,"underline"]))
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
            print(colored("Enter your private key!", "green", attrs=["underline"]))
            while a:
                PrivKey = maskpass.askpass(prompt=">>> " ,mask="*")
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
        print(colored("Enter your encryption key!", "green"))
        while a:
            EncKey = PrivKey = maskpass.askpass(prompt=">>> " ,mask="*")
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

        PubKey = get_from_privkey(decry.decode())
        if not(PubKey):
            print(colored("Encryption Key is invalid", "red"))
            exit(0)
        else:
            if PubKey == data["PublicAddr"]:
                print(colored(f"Successfully authenticated to {PubKey}", "blue"))
                time.sleep(0.75)
                self.clear()
                time.sleep(0.1)
                self.dashboard(PubKey, decry.decode())
            else:
                print(colored("Unsuccessful try again!"))
                exit(0)


    def dashboard(self, PubAddr, Privkey):
        self.Net_Funcs = NetFuncs(PubAddr, Privkey)
        # pretty sick ascii art by https://fsymbols.com/text-art/
        print(colored("""

░██████╗██╗░░██╗░█████╗░██████╗░██████╗░
██╔════╝██║░░██║██╔══██╗██╔══██╗██╔══██╗
╚█████╗░███████║███████║██████╔╝██║░░██║
░╚═══██╗██╔══██║██╔══██║██╔══██╗██║░░██║
██████╔╝██║░░██║██║░░██║██║░░██║██████╔╝
╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░ CLI Wallet V0.1.0
              """, "blue", attrs=["bold"]), end="\n\n\n")
        print(colored(f"Welcome, ", "green"), end="")
        print(colored(PubAddr, "green", attrs=["bold"]))
        print(colored("Balance: ", "green") , end="")
        print(colored(str(self.Net_Funcs.GetBalance()), "green", attrs=["bold", "underline"]), end=" ")
        print(colored("SHRD", "green"))

        print(colored("""
________________________________________________________\n
Send SHRD (1)
DEBUG_MODE (2)
                      """, "blue", attrs=["bold"]))
        Userinp = int(input(">>> "))
        if Userinp == 1:
            time.sleep(0.2)
            self.clear()
            time.sleep(0.2)
            self.send(PubAddr, Privkey)
        elif Userinp == 2:
            print(colored("Work in progress", "magenta"))
            time.sleep(0.5)
            self.clear()
            time.sleep(0.1)
            self.dashboard(PubAddr, Privkey)

        else:
            print(colored("Invalid Input", "red"))
            time.sleep(0.5)
            self.clear()
            time.sleep(0.1)
            self.dashboard(PubAddr, Privkey)

        return

    def send(self, PubAddr, Privkey):
        print(colored("Sending SHRD ---->\n", "blue", attrs=["bold"]))
        print(colored("Enter an address to send to!", "green"))
        AddressToSend = input(">>> ")
        print(colored("Enter amount to send!", "green"))
        try:
            Amount = int(input(">>> "))
            if Amount > self.Net_Funcs.GetBalance():
                print(colored("You do not have enough Shard to complete transaction!", "red"))
                time.sleep(0.5)
                self.clear()
                time.sleep(0.1)
                self.dashboard(PubAddr, Privkey)
            else:
                pass
        except:
            print(colored("DO NOT PUT A STRING HERE", "red"))
            time.sleep(0.5)
            self.clear()
            time.sleep(0.1)
            self.dashboard(PubAddr, Privkey)

        print(colored(f"Confirm Transaction of {Amount} SHARD to {AddressToSend}?", "green"))
        Confirm = input("(Y/N)>>> ").upper()
        a = True
        while a:
            if Confirm == "Y":
                break
            elif Confirm == "N":
                time.sleep(0.1)
                self.clear()
                time.sleep(0.1)
                self.dashboard(PubAddr, Privkey)
                a = False
            else:
                print(colored("INVALID INPUT", "red", attrs=["bold"]))
                time.sleep(2)
                self.clear()
                time.sleep(0.1)
                self.dashboard(PubAddr, Privkey)

        if is_address(AddressToSend) == True and AddressToSend != PubAddr:
            print(colored("\nSent with TXID: "+str(self.Net_Funcs.Send(Privkey, PubAddr, AddressToSend, Amount)), "blue"))
            input("Press Enter to continue...")
            time.sleep(0.1)
            self.clear()
            time.sleep(0.1)
            self.dashboard(PubAddr, Privkey)
        else:
            print(colored("INVALID ADDRESS/you cant send Shard to yourself!", "red", attrs=["bold"]))
            time.sleep(2)
            self.clear()
            time.sleep(0.1)
            self.dashboard(PubAddr, Privkey)

        return

    def clear(self):
        time.sleep(0.25)
        if os.name == 'nt':
            _ = os.system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = os.system('clear')
        time.sleep(0.25)


def handler(signal_received, frame):
    # Handle any cleanup here
    print(colored("\nSIGINT or CTRL-C detected. Exiting gracefully :)", "green"))
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, handler)
    app = Wallet()
