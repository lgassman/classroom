import logging
import time

import requests

from .secrets import login_key


_MAX_RETRIES = 3


def paginated_request(method, url, **kwargs):
    page = 1
    per_page=50
    params = kwargs.pop("params", {})
    while True:
        response = request(method, url,params={"page": page,"per_page": per_page,**params},**kwargs)

        yield from response.json()

        if "next" not in response.links:
            break
        page +=1

def request(method, url, retries=_MAX_RETRIES, **kwargs):
    method = method.upper()
    kwargs["headers"] = {**login_key.headers(), **kwargs.get("headers", {}) }


    for attempt in range(retries + 1):
        response = requests.request(method, url, **kwargs)

        if response.status_code == 401:
            raise RuntimeError("Your GitHub login has expired or is no longer valid. Run the 'login' command again.")

        wait = _retry_wait(response, attempt, retries)

        if wait is not None:
            logging.warning(f"GitHub returned {response.status_code}, retrying in {wait}s")
            time.sleep(wait)
            continue

        if response.status_code == 422 and method in ("POST", "PUT", "PATCH", "DELETE"):
            logging.warning(f"GitHub returned 422: {_describe_422(response)}")
            return response

        if response.status_code >= 400:
            raise requests.HTTPError(f"GitHub request failed: {response.status_code} {response.text}", response=response)

        return response

    raise requests.HTTPError(f"GitHub request failed after {retries} retries: {response.status_code} {response.text}", response=response)


def _retry_wait(response, attempt, retries):
    if attempt >= retries:
        return None

    if response.status_code == 429: #To many request
        return _retry_after(response)

    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0": #a rate problem
        return _rate_limit_wait(response)

    if response.status_code == 409: #the server is probably still working
        return 2 ** attempt

    return None


def _retry_after(response):
    return _get_int(response, "Retry-After")

def _rate_limit_wait(response):
    rate_limit_reset = _get_int(response, "X-RateLimit-Reset")
    return None if rate_limit_reset is not None else max(0, rate_limit_reset - int(time.time()))

def _get_int(response, header_key):
    try:
        return max(0, int(response.headers.get("Retry-After")))
    except (TypeError, ValueError):
        return None
 

def _describe_422(response):
    try:
        data = response.json()
    except ValueError:
        return response.text

    message = data.get("message")
    errors = data.get("errors")

    if errors:
        details = []

        for error in errors:
            if isinstance(error, dict):
                details.append(":".join(str(value) for value in (error.get("resource"), error.get("field"), error.get("code")) if value is not None))
            else:
                details.append(str(error))

        if details:
            return f"{message or 'Validation failed'} ({', '.join(details)})"

    return message or response.text