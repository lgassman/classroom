from .secrets import login_key
from .requests import request, paginated_request
import logging
from requests.exceptions import HTTPError 

import re

def membership_endpoint(orga, name, username):
    return f"https://api.github.com/orgs/{orga}/teams/{name}/memberships/{username}"

def teams_endpoint(orga):
    return f"https://api.github.com/orgs/{orga}/teams"

def team_endpoint(orga, name):
    return f"{teams_endpoint(orga)}/{name}"

def validate_team_name(name):
    if name != name.lower():
        raise ValueError(f"Team name must be lowercase: team: {name}")

    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise ValueError(f"Team name can only contain lowercase letters, numbers and hyphens. team:{name}")

def create_github_team(orga, name, users):
    validate_team_name(name)
    response = request("POST",teams_endpoint(orga),json={"name": name},headers=login_key.headers())

    if response.status_code == 422:
        logging.info(f"Team '{name}' probably already exists")
    else:
        logging.info(f"Team '{name}' created successfully")

    add_members_to_team(orga, name, users)

def add_members_to_team(orga, name, users):
    success = 0
    errors = []

    for username in users:
        try:
            add_member_to_team(orga, name, username.lower())
            success += 1
        except HTTPError as e:
          errors.append(f"{username} {e.response.status_code} {e.response.text}")

    logging.info(f"Added members: {success}")

    if errors:
        logging.error(f"Failed to add {len(errors)} user{'s' if len(errors) != 1 else ''} to the team: {', '.join(errors)}")



def remove_members_from_team(orga, name, users):
    success = 0
    errors = []

    for username in users:
        try:
            remove_member_from_team(orga, name, username)
            success += 1
        except HTTPError as e:
          errors.append(f"{username} {e.response.status_code} {e.response.text}")

    logging.info(f"Removed members: {success}")

    if errors:
        logging.error(f"Failed to remove {len(errors)} user{'s' if len(errors) != 1 else ''} from the team: {', '.join(errors)}")

    
def add_member_to_team(orga, name, username):
    response = request("PUT", membership_endpoint(orga, name, username), json={"role": "member"}, headers=login_key.headers())

    if response.status_code == 422:
        logging.warning(f"User '{username}' probably already belongs to team '{name}'")
    else:
        logging.info(f"Added user '{username}' to team '{name}'")

def remove_member_from_team(orga, name, username):
    response = request("DELETE", membership_endpoint(orga, name, username), headers=login_key.headers())

    if response.status_code == 422:
        logging.warning(f"User '{username}' probably does not belong to team '{name}'")
    else:
        logging.info(f"Removed user '{username}' from team '{name}'")


def _show_team_members(orga, name):
    try:
        logging.info(f"Members of {orga}-{name}")
        _size = 0
        for _size, user in enumerate(find_team_members(orga, name), 1):
            logging.info(f"{user['login']} {user.get('html_url')}")
        logging.info(f"size {_size}")
    except HTTPError as e:
        if e.response.status_code == 404:
            logging.info(f"GitHub team '{name}' does not exist.")
        else:
            raise

def show_pending_members(orga, name):  
    try:
        logging.info(f"Pending members of {orga}-{name}")
        _size = 0
        for _size, user in enumerate(find_team_pending_members(orga, name), 1):
            logging.info(f"{user.get('login') or user.get('email')} (pending)")
        logging.info(f"size {_size}")
    except HTTPError as e:
        if e.response.status_code == 404:
            logging.info(f"GitHub team '{name}' does not exist.")
        else:
            raise

def find_team_pending_members(orga, name):
    validate_team_name(name)
    yield from paginated_request("GET", f"{team_endpoint(orga, name)}/invitations")    


def show_team(orga, name):
    _show_team_members(orga, name)
    _show_pending_members(orga, name)

def delete_team(orga, name):
    response = request("DELETE",team_endpoint(orga, name),headers=login_key.headers())
    response.raise_for_status()

def find_team_members(orga, name):
    validate_team_name(name)
    yield from paginated_request("GET", f"{team_endpoint(orga, name)}/members")

def update_github_team(orga, name, final_members):
    current = {member["login"].lower() for member in find_team_members(orga, name)}

    desired = {member.lower() for member in final_members}

    to_add = desired - current
    to_remove = current - desired

    logging.info(f"Updating team '{name}': {len(to_add)} to add, {len(to_remove)} to remove, {len(current & desired)} unchanged")
    if to_add:
        add_members_to_team(orga, name, sorted(to_add))
    if to_remove:
        remove_members_from_team(orga, name, sorted(to_remove))

def find_teams(orga, prefix):
    teams = paginated_request("GET", teams_endpoint(orga))
    yield from (team for team in teams if team["slug"].startswith(prefix))

