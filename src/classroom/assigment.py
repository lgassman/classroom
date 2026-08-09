from .course import _specified_course, current
import logging
from .requests import request
from requests import HTTPError

from .models import RepoTemplate
from .secrets import login_key
from .teams import find_team



def _get_course(organization, year, semester, course):
    specified_course = _specified_course(organization, year, semester, course)
    if specified_course:
        return specified_course

    current_course = current.get()
    if current_course:
        return current_course

    raise ValueError(
        "A course must be specified or a current course must exist. "
        "Specify a course with --organization, --year, --semester and --course, "
        "or set a current course with 'classroom course --set-current'."
    )


def assignment(organization, year, semester, course, template, name, private, clone):
    specified_course = _get_course(organization, year, semester, course)

    if private and not template:
        raise ValueError("--private can only be used when creating an assignment")

    if clone and not name:
        raise ValueError("--clone requires an assignment name")

    if template:
        return _create_assignment(specified_course, template, name, private)

    if clone:
        return _clone_assignment(specified_course, name, clone)

    if name:
        return _show_assignment(specified_course, name)

    return _show_assignments(specified_course)


def _create_assignment(course, template, name, private):
    template = RepoTemplate.from_str(template, private=private)
    _find_default_branch(template)

    if not name:
        name = template.name

    errors = []
    success = 0

    for student in find_team(course.organization, course.name):
        try:
            logging.info(f"Working with {student['login']}")
            repository_name = f"{course.name}-{name}-{student['login']}"
            _create_assignment_repository(course.organization, repository_name, template, student["login"])
            success += 1
        except KeyError as e:
            if e.args[0] == "login":
                error = f"No login name for student {student}"
                logging.debug(error)
                errors.append(error)
            else:
                raise
        except HTTPError as e:
            error = f"{student['login']}: Error {e.response.status_code} creating assignment for {repository_name}: {e.response.text}"
            logging.debug(error)
            errors.append(error)
        finally:
            logging.info("---")


    logging.info(f"Successfully processed: {success}, errors: {len(errors)}")
    for error in errors:
        logging.error(error)


def _find_default_branch(template):
    response = request("GET",f"https://api.github.com/repos/{template.owner}/{template.name}")
    template.default_branch = response.json()["default_branch"]


def _create_assignment_repository(orga, name, template, student):
    _create_repository(orga, name, template)
    _add_repository_collaborator(orga, name, student)
    _create_feedback_branch(orga, name, template.default_branch)
    commit_sha = _create_feedback_commit(orga, name, template.default_branch)
    _update_default_branch(orga, name, template.default_branch, commit_sha)
    _create_feedback_pull_request(orga, name, template.default_branch)


def _create_repository(orga, name, template):
    response = request("POST", f"https://api.github.com/repos/{template.owner}/{template.name}/generate",
        json={"owner": orga, "name": name, "private": template.private, "include_all_branches": template.include_all_branches},
    )

    if response.status_code == 422:
        logging.info(f"Repository '{name}' probably already exists")
    else: 
        logging.warning(f"Created repository {name} OK: {response.status_code}")


def _add_repository_collaborator(orga, name, username):
    response = request("PUT",f"https://api.github.com/repos/{orga}/{name}/collaborators/{username}",json={"permission": "push"})

    if response.status_code == 422:
        logging.info(f"Collaborator '{username}' probably already has access to repository '{name}'")
    else:
        logging.info(f"Added collaborator '{username}' to repository '{name}': {response.status_code}")
    

def _create_feedback_branch(orga, name, default_branch):
    response = request("GET",f"https://api.github.com/repos/{orga}/{name}/commits/{default_branch}")

    sha = response.json()["sha"]

    response = request("POST",f"https://api.github.com/repos/{orga}/{name}/git/refs",json={"ref": "refs/heads/feedback", "sha": sha})

    if response.status_code == 422:
        logging.info(f"Branch 'feedback' in repository '{name}' probably already exists")
    else:
        logging.info(f"Created branch 'feedback' in repository '{name}': {response.status_code}")


FEEDBACK_COMMIT_MESSAGE = "Initial feedback commit"


def _create_feedback_commit(orga, name, default_branch):
    repo_url = f"https://api.github.com/repos/{orga}/{name}"
    commits = request("GET", f"{repo_url}/commits?sha={default_branch}&per_page=100").json()

    commit = next((commit for commit in commits if commit["commit"]["message"].splitlines()[0] == FEEDBACK_COMMIT_MESSAGE), None)

    if commit:
        logging.info(f"Feedback baseline already exists in repository '{name}'")
        return commit["sha"]
    
    main_sha = request("GET", f"{repo_url}/git/ref/heads/{default_branch}").json()["object"]["sha"]
    tree_sha = request("GET", f"{repo_url}/git/commits/{main_sha}").json()["tree"]["sha"]
    response = request("POST", f"{repo_url}/git/commits", json={"message": FEEDBACK_COMMIT_MESSAGE, "tree": tree_sha, "parents": [main_sha]})

    response.raise_for_status() #Por si vino un 422

    commit_sha = response.json()["sha"]
    logging.info(f"Created feedback baseline commit in repository '{name}'")
    return commit_sha


def _update_default_branch(orga, name, default_branch, commit_sha):
    repo_url = f"https://api.github.com/repos/{orga}/{name}"
    response = request("PATCH", f"{repo_url}/git/refs/heads/{default_branch}", json={"sha": commit_sha})

    response.raise_for_status() #Por si vino un 422

    logging.info(f"Updated default branch '{default_branch}' in repository '{name}'")

def _create_feedback_pull_request(orga, name, default_branch):
    response = request( "POST",f"https://api.github.com/repos/{orga}/{name}/pulls",json={"title": "feedback", "head": default_branch, "base": "feedback"})

    if response.status_code == 422:
        logging.info(f"Feedback pull request in repository '{name}' probably already exists")
    else:
        logging.info(f"Created feedback pull request in repository '{name}': {response.status_code}")
        
def _clone_assignment(course, name, path):
    pass


def _show_assignment(course, name):
    pass


def _show_assignments(course):
    pass