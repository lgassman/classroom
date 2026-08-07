from .secrets import login_key
import requests
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
        raise ValueError("Team name must be lowercase")

    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise ValueError(
            "Team name can only contain lowercase letters, numbers and hyphens"
        )

def create_github_team(orga, name, users):
    validate_team_name(name)
    response = requests.post(
        teams_endpoint(orga),
        json={
            "name": name,
        },
        headers=login_key.headers(),
    )

    if response.status_code != 201:
        raise RuntimeError(
            f"Could not create team '{name}': "
            f"{response.status_code} {response.text}"
        )

    team = response.json()
    team_slug = team["slug"]

    logging.debug(f"Created team: {name}")
    add_members_to_team(orga, name, users)

def add_members_to_team(orga, name, users):
    success = 0
    errors = []

    for username in users:
        if add_member_to_team(orga, name, username):
            success += 1
        else:
            errors.append(username)

    logging.info(f"Added members: {success}")

    if errors:
        logging.error(f"Failed to add {len(errors)} user{'s' if len(errors) != 1 else ''} to the team: {', '.join(errors)}")

    return success, errors


def remove_members_from_team(orga, name, users):
    success = 0
    errors = []

    for username in users:
        if remove_member_from_team(orga, name, username):
            success += 1
        else:
            errors.append(username)

    logging.info(f"Removed members: {success}")

    if errors:
        logging.error(f"Failed to remove {len(errors)} user{'s' if len(errors) != 1 else ''} from the team: {', '.join(errors)}")

    return success, errors
    
def add_member_to_team(orga, name, username):
    response = requests.put(
        membership_endpoint(orga, name, username),
        json={
            "role": "member",
        },
        headers=login_key.headers(),
    )

    if response.status_code not in (200, 201):
        logging.warning(f"Could not add user '{username}' to team '{name}'. {response.status_code} {response.text}")
        return False
    else:
        logging.info(f"Added user: {username}")
        return True
    
def remove_member_from_team(orga, name, username):
    response = requests.delete(
        membership_endpoint(orga, name, username),
        headers=login_key.headers(),
    )

    if response.status_code != 204:
        logging.warning(f"Could not remove user '{username}' from team '{name}'. {response.status_code} {response.text}")
        return False
    else:
        logging.info(f"Removed user: {username}")
        return True

def show_team(orga, name):
    try:
        users = find_team(orga, name)
        _size = 0
        for user in users:
            logging.info(f"{user['login']} {user.get('html_url')}")
            _size += 1
        logging.info(f"size {_size}")
    except HTTPError as e:
        if e.response.status_code == 404:
            logging.info(f"GitHub team '{name}' does not exist.")
        else:
            raise

def delete_team(orga, name):
    response = requests.delete(
        team_endpoint(orga, name),
        headers=login_key.headers(),
    )
    response.raise_for_status()

def find_team(orga, name, per_page=100):
    validate_team_name(name)

    page = 1

    while True:
        response = requests.get(
            f"{team_endpoint(orga, name)}/members",
            params={
                "page": page,
                "per_page": per_page,
            },
            headers=login_key.headers(),
        )

        response.raise_for_status()

        yield from response.json()

        if "next" not in response.links:
            break

        page += 1

import logging


def update_github_team(orga, name, final_members):
    current = {
        member["login"]
        for member in find_team(orga, name)
    }

    desired = set(final_members)

    to_add = desired - current
    to_remove = current - desired

    logging.info(f"Updating team '{name}': {len(to_add)} to add, {len(to_remove)} to remove, {len(current & desired)} unchanged")
    if to_add:
        add_members_to_team(orga, name, sorted(to_add))
    if to_remove:
        remove_members_from_team(orga, name, sorted(to_remove))

    