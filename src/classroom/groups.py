from .course import  specified_course_or_current
from .teams import update_github_team, create_github_team, delete_team, find_teams, find_team_members
import logging
from collections.abc import Iterator

def groups(organization, year, semester, course, grouping, delete, roster):
    if roster and delete:
        raise ValueError("--delete cannot be used together with a roster")

    _course = specified_course_or_current(organization, year, semester, course)

    if roster:
        return _create_or_update_groups(_course, grouping, roster)

    if delete:
        return _delete_groups(_course, grouping)

    return _show_groups(_course, grouping)

def group_name(course, grouping, number):
    return f"{course.name}-{grouping}-{number}"

def _create_or_update_groups(course, grouping, roster):
    existing = dict(_find_groups(course, grouping))
    desired = {group_name(course,grouping,number): set(line.split())for number, line in enumerate(roster, start=1)}

    for name in sorted(existing.keys() - desired.keys()):
        logging.info(f"Deleting obsolete group '{name}'")
        delete_team(course.organization, name)

    for name, users in desired.items():
        if name in existing:
            update_github_team(course.organization, name, users)
        else:
            logging.info(f"Creating group '{name}'")
            create_github_team(course.organization, name, sorted(users))


def _find_groups(course, grouping)-> Iterator[tuple[str, dict]]:
    prefix = f"{course.name}-{grouping}-"
    yield from ((team["slug"], team) for team in find_teams(course.organization, prefix))


def _delete_groups(course, grouping):
    for name in _find_groups(course, grouping):
        logging.info(f"Deleting group '{name}'")
        delete_team(course.organization, name)


# def _show_groups(course, grouping):
#     for name, _ in _find_groups(course, grouping):
#         logging.info(f"Group '{name}':")

#         for member in find_team_members(course.organization, name):
#             logging.info(f"  - {member['login']}")

def _show_groups(course, grouping):
    for name, _ in _find_groups(course, grouping):
        logging.info(f"Team: {name}")

        for member in find_team_members(course.organization, name):
            logging.info(f"    {member['login']}")