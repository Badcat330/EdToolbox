import requests
import Model.EnvironmentVariables as Variables
import Model.Exceptions as Exceptions

import time


def get_token(user, pwd):
    url = f"https://login.microsoftonline.com/{Variables.TenantID}/oauth2/v2.0/token"

    payload = 'grant_type=password&' \
              f'client_id={Variables.ClientId}&' \
              f'client_secret={Variables.ClientSecret}&' \
              'scope=https%3A//graph.microsoft.com/.default+offline_access&' \
              f'username={user}&' \
              f'password={pwd}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'x-ms-gateway-slice=prod; stsservicecookie=ests; fpc=Au0l4KQG5plFurbvgO_W1cBKvchEAQAAALO2s9YOAAAA'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text.encode('utf8'))

    if response.status_code != 200:
        print('Token request fault')
        return None

    token = response.json()['access_token']
    refresh_token = response.json()['refresh_token']

    return token, refresh_token


def get_user(user_name):
    url = f"https://graph.microsoft.com/v1.0/users/{user_name}"

    headers = {
        'Authorization': Variables.user_token
    }

    response = requests.request("GET", url, headers=headers).json()

    if 'error' in response:
        if response['error']['code'] == 'InvalidAuthenticationToken':
            raise Exceptions.TokenException('You don\'t have permissions!')
        elif response['error']['code'] == 'Request_ResourceNotFound':
            raise Exceptions.StudentNotFoundException('Student not found!')
        # TODO find all possible exceptions

    # return information about user in json
    return response


def get_classes_in_organization():
    url = f"https://graph.microsoft.com/beta/education/classes"

    headers = {
        'Authorization': Variables.user_token
    }
    response = requests.request("GET", url, headers=headers).json()

    if 'error' in response:
        ...  # raise exception

    return response['value']


def get_class_members(class_id):
    url = f"https://graph.microsoft.com/beta/education/classes/{class_id}/members"

    headers = {
        'Authorization': Variables.user_token
    }
    response = requests.request("GET", url, headers=headers).json()

    if 'error' in response:
        if response['error']['code'] == 'Request_ResourceNotFound':
            time.sleep(2)
            return get_class_members(class_id)
        ...  # raise exception

    return response['value']


def get_class_teachers(class_id):
    url = f"https://graph.microsoft.com/beta/education/classes/{class_id}/teachers"

    headers = {
        'Authorization': Variables.user_token
    }
    response = requests.request("GET", url, headers=headers).json()

    if 'error' in response:
        ...  # raise exception

    return response['value']


def add_resource_to_assignment(class_id, assignment_id, task_link):
    url = f"https://graph.microsoft.com/beta/education/classes/{class_id}/assignments/{assignment_id}/resources"

    headers = {
        'Authorization': Variables.user_token,
        'Content-Type': 'application/json'
    }

    payload = "{\n" \
              f"\"distributeForStudentWork\": false, \n" \
              "\"resource\": { \n" \
              f"\"displayName\": \"TaskLink\", \n" \
              f"\"link\": \"{task_link}\", \n" \
              f"\"thumbnailPreviewUrl\": null, \n" \
              f"\"@odata.type\": \"#microsoft.graph.educationLinkResource\" \n" \
              "} \n" \
              "}"

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()
    print(response)


def publish_assignment(class_id, assignment_id):
    headers = {
        'Authorization': Variables.user_token,
        'Content-Type': 'application/json'
    }

    publish_url = f"https://graph.microsoft.com/beta/education/classes/" \
                  f"{class_id}/assignments/{assignment_id}/publish"
    response = requests.request("POST", publish_url, headers=headers).json()
    print('publish: ', response)
    if 'error' in response:
        if response['error']['innerError']['code'] == 'invalidAssignTo':
            time.sleep(1)
            return publish_assignment(class_id, assignment_id)

    return assignment_id


def create_assignment(class_id, due_date, name, student_id):
    create_url = f"https://graph.microsoft.com/beta/education/classes/{class_id}/assignments"

    headers = {
        'Authorization': Variables.user_token,
        'Content-Type': 'application/json'
    }

    payload = "{\n" \
              f"\"dueDateTime\": \"{due_date}\", \n" \
              f"\"displayName\": \"{name}\", \n" \
              "\"instructions\": { \n" \
              f"\"contentType\": \"text\", \n" \
              f"\"content\": \"Do the task on the link!\" \n" \
              "}, \n" \
              "\"grading\": { \n" \
              f"\"@odata.type\": \"#microsoft.graph.educationAssignmentPointsGradeType\", \n" \
              f"\"maxPoints\": 10 \n" \
              "}, \n" \
              "\"assignTo\": {\n" \
              f"\"@odata.type\": \"microsoft.graph.educationAssignmentIndividualRecipient\", \n" \
              f"\"recipients\": [\"{student_id}\"] \n" \
              "},\n" \
              f"\"status\": \"draft\", \n" \
              f"\"allowStudentsToAddResourcesToSubmission\": false\n" \
              "}"

    response = requests.request("POST", create_url, headers=headers, data=payload.encode('utf8')).json()
    if 'error' in response:
        if response['error']['innerError']['code'] == 'invalidAssignTo':
            time.sleep(1)
            return create_assignment(class_id, due_date, name, student_id)

    return publish_assignment(class_id, response['id'])


def get_tags_in_class(class_id):
    url = f"https://graph.microsoft.com/beta/teams/{class_id}/tags"

    headers = {
        'Authorization': Variables.user_token
    }
    response = requests.request("GET", url, headers=headers).json()

    return dict(map(lambda x: (x['displayName'], x['id']), response['value']))


def get_tag_members(class_id, tag_id):
    url = f"https://graph.microsoft.com/beta/teams/{class_id}/tags/{tag_id}/members"

    headers = {
        'Authorization': Variables.user_token
    }
    response = requests.request("GET", url, headers=headers).json()

    return list(map(lambda x: x['userId'], response['value']))


def create_tag(class_id, tag_name, members, has_id=False):
    url = f"https://graph.microsoft.com/beta/teams/{class_id}/tags"

    headers = {
        'Authorization': Variables.user_token,
        'Content-Type': 'application/json'
    }

    members_list = ""

    for i in members:
        if has_id:
            members_list += "{ \n" \
                            f"\"userId\": \"{i['id']}\" \n" \
                            "} \n"
        else:
            members_list += "{ \n" \
                            f"\"userId\": \"{get_user(i)['id']}\" \n" \
                            "} \n"
        if i != members[-1]:
            members_list += ',\n'

    payload = "{\n" \
              f"\"displayName\": \"{tag_name}\", \n" \
              f"\"members\": [ \n" \
              f"{members_list}" \
              f"] \n" \
              "}"

    tag_id = None
    if len(members) > 0:
        response = requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()
        tag_id = response['id']

    return tag_id


def create_class(class_name, owner):
    url = f"https://graph.microsoft.com/beta/teams"

    headers = {
        'Authorization': Variables.user_token,
        'Content-Type': 'application/json'
    }

    payload = "{\n" \
              f"\"template@odata.bind\": \"https://graph.microsoft.com/beta/teamsTemplates('educationClass')\", \n" \
              f"\"displayName\": \"{class_name}\", \n" \
              f"\"description\": \"\", \n" \
              f"\"members\": [ \n" \
              "{ \n" \
              f"\"@odata.type\": \"#microsoft.graph.aadUserConversationMember\", \n" \
              f"\"roles\": [\"owner\"], \n" \
              f"\"user@odata.bind\": \"https://graph.microsoft.com/beta/users('{owner}')\" \n" \
              "} \n" \
              "] \n" \
              "}"

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf8'))
    resp_headers = response.headers
    # value in header will be in format: "/teams('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')"
    return resp_headers['Content-Location'][8:44]


def add_member_to_class(class_id, student_email):
    url = f"https://graph.microsoft.com/beta/teams/{class_id}/members"

    headers = {
        'Authorization': Variables.user_token,
        'Content-Type': 'application/json'
    }

    payload = "{\n" \
              f"\"@odata.type\": \"#microsoft.graph.aadUserConversationMember\", \n" \
              f"\"roles\": [], \n" \
              f"\"user@odata.bind\": \"https://graph.microsoft.com/beta/users('{student_email}')\" \n" \
              "}"

    requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()


def add_member_to_tag(class_id, tag_id, student_email):
    url = f"https://graph.microsoft.com/beta/teams/{class_id}/tags/{tag_id}/members"

    headers = {
        'Authorization': Variables.user_token,
        'Content-Type': 'application/json'
    }

    payload = "{\n" \
              f"\"userId\": \"{get_user(student_email)['id']}\" \n" \
              "}"

    requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()

