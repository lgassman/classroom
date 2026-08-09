from .commandBuilder import CommandBuilder, line_file
from .login import login
from.client import client
from .logout import logout
from .whoami import whoami
from .course import course
from .config import config
import logging
from .assigment import assignment

import textwrap



def main():
    configure_logging()
    builder = CommandBuilder()
    (builder.addCommand(client, help="Handle GitHub client id and secret (set/get/delete)", epilog=_client_epilog())
        .add_argument("id", nargs="?", help="The github client id") \
        .add_argument("secret", nargs="?", metavar="SECRET",help="The github client secret") 
        .add_argument("--delete",action="store_true",help="Delete the client secret from keyring")
        .add_argument("--show-secret",action="store_true",help="show the secret"))
    builder.addCommand(login, help="github login")
    builder.addCommand(logout, help="github logout")
    builder.addCommand(whoami, help="show data about current github user")
    (builder.addCommand(course, help="Handle a course", epilog=_course_epilog())
        .add_argument("--organization", "-o", help="GitHub organization name")
        .add_argument("--year", "-y",  help="Academic year")
        .add_argument("--semester","-s",  help="Academic semester")
        .add_argument("--course","-c", help="Course section number")
        .add_argument("--update","-u",  action="store_true", help="Update an existing course")
        .add_argument("--delete", action="store_true", help="Delete the course")
        .add_argument("--set-current", action="store_true", help="Set this course as the current course")
        .add_argument("--unset", action="store_true", help="Clear the current course")
        .add_argument("--untrack", action="store_true", help="Remove the course from the local configuration")
        .add_argument("roster", nargs="?", type=line_file, help="Path to a file containing GitHub student accounts, one account per line"))
    (builder.addCommand(assignment, help="Handle an assignment", epilog=_assignment_epilog())
        .add_argument("--organization", "-o", help="GitHub organization name")
        .add_argument("--year", "-y", help="Academic year")
        .add_argument("--semester", "-s", help="Academic semester")
        .add_argument("--course", "-c", help="Course section number")
        .add_argument("--template", "-t", help="GitHub template repository URL")
        .add_argument("--name", "-n", help="Assignment name")
        .add_argument("--private", action="store_true", help="Create private repositories")
        .add_argument("--clone", metavar="PATH", help="Clone assignment repositories to PATH")
        .add_argument("--user", "-u", nargs="+", help="GitHub usernames to process instead of the course students. Useful for teachers"))
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

def _assignment_epilog():
    return textwrap.dedent("""
        A current course is used when no course is specified.

        Examples:

            Create an assignment in the current course:
                classroom assignment -t https://github.com/obj1unq/pepitaEnunciado

            Create an assignment specifying the course:
                classroom assignment -o obj1unq -y 2026 -s 2 -c 2 -t https://github.com/obj1unq/pepitaEnunciado

            Create an assignment with a custom name:
                classroom assignment -t https://github.com/obj1unq/pepitaEnunciado -n tp1

            Create private repositories:
                classroom assignment -t https://github.com/obj1unq/pepitaEnunciado --private

            Create an assignment for specific users instead of the course students:
                classroom assignment -t https://github.com/obj1unq/pepitaEnunciado -u lgassman otro_usuario

            List assignments in the current course:
                classroom assignment

            List assignments in a specific course:
                classroom assignment -o obj1unq -y 2026 -s 2 -c 2

            List repositories for an assignment:
                classroom assignment -n tp1

            Clone an assignment:
                classroom assignment -n tp1 --clone ~/assignments

            Clone repositories for specific users instead of the course students:
                classroom assignment -n tp1 --clone ~/assignments -u lgassman otro_usuario

        The --user option processes the specified GitHub users instead of the
        students in the course. This can be useful for teachers who need to
        create or clone their own assignment repositories.

        Without --template, the command only queries existing assignments
        and repositories. The --name option selects a specific assignment.

        When --clone is specified, repositories are cloned under:
            <path>/<course>/<assignment>/<student>

        Existing repositories are updated with git pull.
        """)

def configure_logging():
    #TODO algun dia voy a hacer el comando para configurar el log
    level_name = config.get("log_level", "INFO")
    log_format = config.get("log_format", "%(levelname)s: %(message)s")

    level = getattr(logging, level_name.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format=log_format,
    )

if __name__ == "__main__":
    raise SystemExit(main())