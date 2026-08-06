from .secrets import client_key 
from .config import config


def client(id, secret, delete, show_secret):

    if bool(id) != bool(secret):
        raise Exception("id and secret must be provided together or both omitted")

    if delete:
        config.remove("client").save()
        client_key.delete()
    elif secret:
        config.set("client", id).save()
        client_key.save(secret)
    else:
        out = f"client id: {config.get("client")}. "
        if show_secret:
            try:
                out += f"Client secret: {client_key.get()}"
            except:
                out += f"Client secret not present." 
            
        print(out)

