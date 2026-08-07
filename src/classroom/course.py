from .models import Course, ModelSerializer
from .teams import create_github_team, show_team, delete_team, update_github_team
from .config import ListConfig, Config
import logging 


courseSerializer = ModelSerializer(cls=Course)
tracked = ListConfig("tracked", serializer=courseSerializer)
current = Config("current", serializer=courseSerializer)


def _specified_course(organization, year, semester, course):
    course_parameters = [organization, year, semester, course]
    course_specified = all(course_parameters)
    if not course_specified and any(course_parameters) :
        raise ValueError("Organization, year, semester and course must be specified together")
    return Course(organization, year, semester, course) if course_specified else None

def _validate_just_one_action(update, delete, set_current, unset, untrack):
    if sum([update, delete, set_current, unset, untrack]) > 1:
        raise ValueError("Course actions are mutually exclusive")




def course(organization, year, semester, course, update, delete, set_current, unset, untrack, roster):
    _validate_just_one_action(update, delete, set_current, unset, untrack)
    specified_course = _specified_course(organization, year, semester, course)

    if roster:
        if any([delete, set_current, unset, untrack]):
            raise ValueError("Roster can only be used to create or update a course")
        if not specified_course:
            raise ValueError("A course must be specified when using a roster")

        if update:
            return _update_course(specified_course, roster)
        else:
            return _create_course(specified_course, roster)
        
    if (delete or set_current or untrack) and not specified_course:
            raise ValueError("A course must be specified for this operation")

    if delete:
        return _delete_course(specified_course)

    if set_current:
        return _set_current_course(specified_course)

    if unset:
        if specified_course:
            raise ValueError("--unset does not accept a course")
        return _unset_current_course()

    if untrack:
        return _untrack_course(specified_course)

    if specified_course:
        return _show_course(specified_course)

    return _show_current_and_tracked_courses()


def _create_course(course, roster):
    logging.info(f"Creating coourse {course}")
    create_github_team(course.organization, course.name, roster)
    tracked.add_if_missing(course)

def _update_course(course, roster):
    logging.info(f"Updating course {course}")
    update_github_team(course.organization, course.name, roster)

    

def _delete_course(course):
    logging.info(f"Deleting course {course}")
    delete_team(course.organization, course.name)


def _show_course(course):
    logging.info(f"Showing course {course}")
    show_team(course.organization, course.name)


def _set_current_course(course):
    logging.info(f"Setting course {course} as current")
    current.save(course)
    tracked.add_if_missing(course)

def _unset_current_course():
    logging.info(f"Unsetting course {course}")
    current.delete()

def _untrack_course(course):
    logging.info(f"Untrucking course {course}")
    tracked.remove(course)
 
def _show_current_and_tracked_courses():
    current_course = current.get()
    if current_course:
        _show_course(current_course)
    logging.info("Tracked courses:")
    for course in tracked.get():
        logging.info(f"- {course.name}")





