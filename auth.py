import bcrypt

tuz = bcrypt.gensalt(12)
pw = bcrypt.hashpw('8727'.encode(), tuz)

def get_loged(password):
    password = password.encode()
    return bcrypt.checkpw(password, pw)