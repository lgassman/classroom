from .commandBuilder import CommandBuilder, SubCommandBuilder
from .login import login
from.client import client
from .logout import logout
from .whoami import whoami
from .course import course

import textwrap



def main():
    builder = CommandBuilder()
    builder.addCommand(client, help="Handle GitHub client id and secret (set/get/delete)", epilog=_client_epilog())\
        .add_argument("id", nargs="?", help="The github client id") \
        .add_argument("secret", nargs="?", metavar="SECRET",help="The github client secret") \
        .add_argument("--delete",action="store_true",help="Delete the client secret from keyring")\
        .add_argument("--show-secret",action="store_true",help="show the secret")
    builder.addCommand(login, help="github login")
    builder.addCommand(logout, help="github logout")
    builder.addCommand(whoami, help="show data about current github user")
    # builder.addCommand(course, help="Handle a
    builder.addCommand(whoami, help="show data about current github user")
    builder.addCommand(course, help="Handle a course", epilog=_course_epilog())\
        .add_argument("-o", "--organization", help="Organizaction of github")\
        .add_argument("-y", "--year", help="Organizaction of github")\
        .add_argument("-s", "--semester", help="semester")\
        .add_argument("-c", "--course", help="course")\
        .add_argument("-u", "--update", action="store_true", help="Expects the course to exist and updates it")\
        .add_argument("--delete", action="store_true", help="Expects the course to exist and updates it")\
        .add_argument("--set", action="store_true", help="Set the current course")\
        .add_argument("--unset", action="store_true", help="Unset the current course")\
        .add_argument("--untrack", action="store_true", help="Unset the current course")\
        .add_argument("roster", nargs="?", help="Path to a file with GitHub student accounts, one account per line.") \

    builder.run()

def _client_epilog():
    return textwrap.dedent("""
        Examples:
            Save client secret:
                classroom client my-id my-secret-value

            Show current client id:
                classroom client

            Show current client id and secret:
                classroom client --show-secret

            Delete client id and secret:
                classroom client --delete
    """)

def _course_epilog():
    return textwrap.dedent("""
        A current course can be configured to avoid specifying the course
        in every command. This is convenient if you usually work with a
        single course. If you prefer to be explicit, you can specify the
        course in each command instead.

        To help prevent accidental changes, course modification commands
        always require the course to be specified explicitly. The current
        course is only used by commands that operate on a course, not by
        commands that modify its definition.

        Examples:

            Create a course:
                classroom course -o obj1unq -y 2026 -s 1 -c 1 roster.txt

            Update an existing course:
                classroom course -o obj1unq -y 2026 -s 1 -c 1 --update roster.txt

            Delete a course:
                classroom course -o obj1unq -y 2026 -s 1 -c 1 --delete

            Show information about a course:
                classroom course -o obj1unq -y 2026 -s 1 -c 1

            Set the current course:
                classroom course -o obj1unq -y 2026 -s 1 -c 1 --set

            Unset the current course:
                classroom course --unset

            Show the current course and the list of tracked courses:
                classroom course

            Untrack a course:
                classroom course -o obj1unq -y 2026 -s 1 -c 1 --untrack
        """)

if __name__ == "__main__":
    raise SystemExit(main())