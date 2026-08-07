import keyring

SERVICE_NAME = "uqbar-classroom" #TODO, esto quizas deba calcularse a partir del proyecto o parametrizarse o algo

class Key:
    def __init__(self, name, not_found_error):
        self.name = name
        self.not_found_error = not_found_error

    def save(self, value):
        keyring.set_password(SERVICE_NAME,self.name,value)

    def delete(self):
        keyring.delete_password(SERVICE_NAME,self.name)

    def get(self):
        secret =  keyring.get_password(SERVICE_NAME,self.name)
        if not secret:
            raise RuntimeError(self.not_found_error)
        return secret

class AuthKey(Key):
    def headers(self):
        return {
            "Authorization": f"Bearer {self.get()}",
            "Accept": "application/vnd.github+json",
        }


client_key = Key("client_secret", "The client secret is not configured. please run `client <client_key> <client_secret>` command")
login_key = AuthKey("login","Login token not found. Please run `login` command")
    



