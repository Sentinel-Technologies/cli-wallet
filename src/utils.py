from web3.auto import w3
import secrets

def get_new_address():
    """Returns new address and private key. NEVER SHARE YOUR PRIVATE KEY!"""
    privkey = "0x" + secrets.token_hex(32)
    return w3.eth.account.privateKeyToAccount(privkey).address, privkey

def get_from_privkey(privkey : str):
    """Returns the address belonging to a private key."""
    try:
        return w3.eth.account.privateKeyToAccount(privkey).address
    except:
        return False

def is_address(address):
    """Checks if the address is valid."""
    return w3.isAddress(address)
