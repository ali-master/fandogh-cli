import requests
import os

fandogh_host = os.getenv('FANDOGH_HOST', 'http://fandogh.cloud:8080')
base_url = '%s/api/' % fandogh_host
base_webapp_url = '%swebapp/' % base_url


class FandoghAPIError(Exception):
    message = "Server Error"

    def __init__(self, response):
        self.response = response


class AuthenticationError(Exception):
    message = "Please login first. You can do it by running 'fandogh login' command"

    def __init__(self, response):
        self.response = response


class ResourceNotFoundError(FandoghAPIError):
    message = "Resource Not found"

    def __init__(self, response):
        self.response = response


def get_exception(response):
    return {
        404: ResourceNotFoundError(response),
        401: AuthenticationError(response)
    }.get(response.status_code, FandoghAPIError(response))


def create_image(app_name, token):
    response = requests.post(base_webapp_url + 'apps',
                             json={'name': app_name},
                             headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.text


def get_images(token):
    response = requests.get(base_webapp_url + 'apps',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def get_image_build(app, version, token):
    response = requests.get(base_webapp_url + 'apps/' + app + '/versions/' + version + '/builds',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def create_version(image_name, version, workspace_path):
    with open(workspace_path, 'rb') as file:
        files = {'source': file}
        response = requests.post(base_webapp_url + 'apps/' + image_name + '/versions',
                                 files=files,
                                 data={'version': version})
        if response.status_code != 200:
            raise get_exception(response)
        else:
            return response.text


def list_versions(image_name):
    response = requests.get(base_webapp_url + 'apps/' + image_name + '/versions')
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def _parse_env_variables(envs):
    env_variables = {}
    for env in envs:
        (k, v) = env.split('=')
        env_variables[k] = v
    return env_variables


def deploy_service(image_name, version, service_name, envs, token):
    env_variables = _parse_env_variables(envs)
    response = requests.post(base_webapp_url + 'services',
                             json={'app_name': image_name,
                                   'img_version': version,
                                   'service_name': service_name,
                                   'environment_variables': env_variables},
                             headers={'Authorization': 'JWT ' + token}
                             )
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def list_services(token, show_all):
    response = requests.get(base_webapp_url + 'services',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        json_result = response.json()
        if show_all:
            return json_result
        return [item for item in json_result if item.get('state', None) == 'RUNNING']


def destroy_service(service_name, token):
    response = requests.delete(base_webapp_url + 'services/' + service_name,
                               headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def get_token(username, password):
    response = requests.post(base_url + 'tokens', json={'username': username, 'password': password})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def get_logs(service_name, token):
    response = requests.get(base_webapp_url + "services/%s/logs" % service_name,
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code == 200:
        return response.json()
    else:
        raise get_exception(response)
