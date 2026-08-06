from .commandBuilder import CommandBuilder, SubCommandBuilder
from .login import login
from.client import client
from .logout import logout
from .whoami import whoami
import textwrap



def main():
    builder = CommandBuilder()
    builder.addCommand(login, help="github login")
    builder.addCommand(logout, help="github logout")
    builder.addCommand(whoami, help="show data about current github user")
    builder.addCommand(client, help="Handle GitHub client id and secret (set/get/delete)", 
                       epilog=textwrap.dedent("""
                            Examples:

                            Save client secret:
                                classroom client my-id my-secret-value

                            Show current client id:
                                classroom client

                            Show current client id and secret:
                                classroom client --show-secret

                            Delete client id and secret:
                                classroom client --delete
                            """),
                       ) \
        .add_argument("id", nargs="?", help="The github client id") \
        .add_argument("secret", nargs="?", metavar="SECRET",help="The github client secret") \
        .add_argument("--delete",action="store_true",help="Delete the client secret from keyring")\
        .add_argument("--show-secret",action="store_true",help="show the secret")
    builder.run()


if __name__ == "__main__":
    raise SystemExit(main())