from .secrets import client_key 
from .config import client_config


def client(id, secret, delete, show_secret):

    if bool(id) != bool(secret):
        raise Exception("id and secret must be provided together or both omitted")

    if delete:
        client_config.delete()
        client_key.delete()
    elif secret:
        client_config.save(id)
        client_key.save(secret)
    else:
        out = f"client id: {client_config.get()}. "
        if show_secret:
            try:
                out += f"Client secret: {client_key.get()}"
            except:
                out += f"Client secret not present." 
            
        print(out)

