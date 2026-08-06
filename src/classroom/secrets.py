import keyring

SERVICE_NAME = "uqbar-classroom" #TODO, esto quizas deba calcularse a partir del proyecto o parametrizarse o algo

class Key:
    def __init__(self, name):
        self.name = name

    def save(self, value):
        keyring.set_password(SERVICE_NAME,self.name,value)

    def delete(self):
        keyring.delete_password(SERVICE_NAME,self.name)

    def get(self):
        secret =  keyring.get_password(SERVICE_NAME,self.name)
        if not secret:
            raise RuntimeError(f"{SERVICE_NAME}.{self.name} not present in keyring")
        return secret

client_key = Key("client_secret")
login_key = Key("login")
    



