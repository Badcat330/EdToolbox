import requests
import Model.EnvironmentVariables as Variables
import Model.Exceptions as Exceptions


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
        # TODO handle exception
        return None

    token = response.json()['access_token']
    refresh_token = response.json()['refresh_token']

    return token, refresh_token


def get_classes_in_organization():
    url = f"https://graph.microsoft.com/beta/education/classes"

    headers = {
        'Authorization': Variables.user_token
    }
    response = requests.request("GET", url, headers=headers).json()

    if 'error' in response:
        ...  # raise exception

    return dict(map(lambda x: (x['displayName'], x['id']), response['value']))


def get_class_members(class_id):
    url = f"https://graph.microsoft.com/beta/education/classes/{class_id}/members"

    headers = {
        'Authorization': Variables.user_token
    }
    response = requests.request("GET", url, headers=headers).json()

    if 'error' in response:
        ...  # raise exception

    return dict(map(lambda x: (x['userPrincipalName'], x['id']), response['value']))


def add_members_to_class(class_id, members):
    ...


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


def create_assignment(class_id, due_date, name, student_id, task_link):
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
    print(response)
    assignment_id = response['id']
    add_resource_to_assignment(class_id, assignment_id, task_link)

    publish_url = f"https://graph.microsoft.com/beta/education/classes/" \
                  f"{class_id}/assignments/{assignment_id}/publish"
    response = requests.request("POST", publish_url, headers=headers).json()
    print(response)


def get_user(token, user_name):
    url = f"https://graph.microsoft.com/v1.0/users/{user_name}" \
          f"?$select=id,displayName,mail,givenName,surname,userPrincipalName&$expand=extensions"

    headers = {
        'Authorization': token
    }

    response = requests.request("GET", url, headers=headers)
    parsed_response = response.json()

    if 'error' in parsed_response:
        if parsed_response['error']['code'] == 'InvalidAuthenticationToken':
            raise Exceptions.TokenException('You don\'t have permissions!')
        elif parsed_response['error']['code'] == 'Request_ResourceNotFound':
            raise Exceptions.StudentNotFoundException('Student not found!')
        # TODO find all possible exceptions

    # return information about user in json
    return parsed_response


def get_uc_payload(display_name, given_name, surname, mail_nickname, user_principal_name, password):
    # displayName: users name and surname
    # givenName: users name
    # surname: users surname
    # mailNickname: users e-mail in system without damien, example aglushko
    # userPrincipalName: e-mail in system, example aglushko@ithse.ru
    # password: disposable password
    return "{\n  " \
           "\"accountEnabled\": true,\n  " \
           f"\"displayName\": \"{display_name}\",\n  " \
           f"\"givenName\": \"{given_name}\",\n  " \
           f"\"surname\": \"{surname}\",\n  " \
           f"\"mailNickname\" : \"{mail_nickname}\",\n  " \
           f"\"userPrincipalName\": \"{user_principal_name}\",\n  " \
           f"\"usageLocation\": \"US\",\n " \
           "\"passwordProfile\" : {\n    " \
           "\"forceChangePasswordNextSignIn\": true,\n    " \
           f"\"password\": \"{password}\"\n  " \
           "}\n" \
           "}"


def get_user_extension_payload(personal_mail):
    return "{\n" \
           "\"@odata.type\":\"microsoft.graph.openTypeExtension\",\n    " \
           f"\"extensionName\":\"com.CoDiM.managmentTool\",\n    " \
           f"\"personalMail\":\"{personal_mail}\"\n" \
           "}\n"


def get_user_licence_payload():
    return "{\n  \"addLicenses\": " \
           "[\n    " \
           "{\n      " \
           "\"disabledPlans\": [],\n      " \
           "\"skuId\": \"314c4481-f395-4525-be8b-2ec4bb1e9d91\"\n    " \
           "}\n  ],\n  " \
           "\"removeLicenses\": [ ]" \
           "\n}"


def post_multiple_users(token, users, passwords):
    url = "https://graph.microsoft.com/v1.0/$batch"
    if len(users) == 0:
        return [], []

    payload = "{\n  " \
              "\"requests\": [\n  "
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    curr_id = 1

    for i in range(len(users)):
        uc_payload = get_uc_payload(users[i][4], users[i][1],
                                    users[i][0], users[i][5],
                                    users[i][6], passwords[i])
        payload += "{\n" \
                   f"\"id\": \"{curr_id}\", \n" \
                   f"\"url\": \"/users\", \n" \
                   f"\"method\": \"POST\", \n" \
                   "\"headers\": {\n" \
                   f"\"Authorization\": \"{token}\", \n" \
                   f"\"Content-Type\": \"application/json\" \n" \
                   "},\n" \
                   f"\"body\": " \
                   f"{uc_payload}\n" \
                   "}"

        if i != len(users) - 1:
            payload += ", \n"
        else:
            payload += "\n"

        curr_id += 1

    payload += "]\n" \
               "}"

    print(payload)
    responses = requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()
    good_response_indexes = []
    error_response_indexes = []
    print(responses)
    for i in range(len(responses['responses'])):
        if 'error' in responses['responses'][i] or 'error' in responses['responses'][i]['body']:
            error_response_indexes.append(i)
        else:
            good_response_indexes.append(i)

    return good_response_indexes, error_response_indexes


def get_users_of_groups(token, ids):
    url = "https://graph.microsoft.com/v1.0/$batch"

    payload = "{\n  " \
              "\"requests\": [\n  "
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    curr_id = 1

    for group_id in ids:
        payload += "{\n" \
                   f"\"id\": \"{curr_id}\", \n" \
                   f"\"url\": \"/groups/{group_id}/members/microsoft.graph.user?$select=userPrincipalName\", \n" \
                   f"\"method\": \"GET\", \n" \
                   "\"headers\": {\n" \
                   f"\"Authorization\": \"{token}\" \n" \
                   "}\n" \
                   "}\n"

        if group_id != ids[-1]:
            payload += ", \n"
        else:
            payload += "\n"

        curr_id += 1

    payload += "]\n" \
               "}"

    parsed_responses = requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()
    mails = set()
    print(parsed_responses)

    for response in parsed_responses['responses']:
        for mail in response['body']['value']:
            mails.add(mail['userPrincipalName'])

    return mails


def create_group(token, group_name, members):
    url = "https://graph.microsoft.com/v1.0/groups"

    bindStart = "https://graph.microsoft.com/v1.0/users/"
    members = map(lambda x: '\"' + bindStart + x + '\"', members)
    members_str = '[' + ',\n'.join(members) + ']'

    payload = "{\n  " \
              f"\"displayName\": \"{group_name}\",\n  " \
              "\"groupTypes\": [\n    \"Unified\"\n  ],\n  " \
              "\"mailEnabled\": true,\n  " \
              f"\"mailNickname\": \"{group_name}\",\n  " \
              "\"securityEnabled\": true,\n  " \
              "\"owners@odata.bind\": [\n      " \
              f"\"https://graph.microsoft.com/v1.0/users/{Variables.user_name}\"\n      " \
              "],\n  " \
              "\"visibility\": \"Public\",\n" \
              "\"members@odata.bind\": " + members_str + " \n}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()
    print(response)
    return response['id']


def get_group_members(token, group_id):
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members?$select=userPrincipalName"

    headers = {
        'Authorization': token
    }

    response = requests.request("GET", url, headers=headers)
    members = []

    if response.json()['value']:
        for i in response.json()['value']:
            members.append(i['userPrincipalName'])

    return members


def get_groups(token):
    url = f"https://graph.microsoft.com/v1.0/groups?$select=id,displayName"

    headers = {
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers).json()
    value = response['value']

    while '@odata.nextLink' in response:
        response = requests.request("GET", response['@odata.nextLink'], headers=headers).json()
        value.extend(response['value'])

    return value


def create_team(token, group_id):
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/team"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': token
    }

    payload = "{\n  " \
              "\"memberSettings\": {\n" \
              "\"allowCreatePrivateChannels\": true,\n" \
              "\"allowCreateUpdateChannels\": true\n" \
              "},\n" \
              "\"messagingSettings\": {\n" \
              "\"allowUserEditMessages\": true,\n" \
              "\"allowUserDeleteMessages\": true\n" \
              "},\n" \
              "\"funSettings\": {\n" \
              "\"allowGiphy\": true,\n" \
              "\"giphyContentRating\": \"strict\"\n" \
              "}\n" \
              "}"

    response = requests.request("PUT", url, headers=headers, data=payload).json()
    print(response)
    return 'error' in response


def get_primary_channels(token, teams_ids):
    url = "https://graph.microsoft.com/v1.0/$batch"

    payload = "{\n  " \
              "\"requests\": [\n  "
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    curr_id = 1

    for team_id in teams_ids:
        payload += "{\n" \
                   f"\"id\": \"{curr_id}\", \n" \
                   f"\"url\": \"/teams/{team_id}/primaryChannel?$select=id\", \n" \
                   f"\"method\": \"GET\", \n" \
                   "\"headers\": {\n" \
                   f"\"Authorization\": \"{token}\" \n" \
                   "}\n" \
                   "}\n"

        if team_id != teams_ids[-1]:
            payload += ", \n"
        else:
            payload += "\n"

        curr_id += 1

    payload += "]\n" \
               "}"

    parsed_responses = requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()

    primary_ids = []
    print(parsed_responses)
    for response in parsed_responses['responses']:
        primary_ids.append(response['body']['id'])

    return primary_ids


def send_message_to_teams(token, teams_ids, message):
    primary_channels = get_primary_channels(token, teams_ids)
    url = "https://graph.microsoft.com/v1.0/$batch"

    payload = "{\n  " \
              "\"requests\": [\n  "
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    curr_id = 1

    for team_id, channel_id in zip(teams_ids, primary_channels):
        payload += "{\n" \
                   f"\"id\": \"{curr_id}\", \n" \
                   f"\"url\": \"/teams/{team_id}/channels/{channel_id}/messages\", \n" \
                   f"\"method\": \"POST\", \n" \
                   "\"headers\": {\n" \
                   f"\"Authorization\": \"{token}\", \n" \
                   f"\"Content-Type\": \"application/json\" \n" \
                   "},\n" \
                   "\"body\": {\n" \
                   "\"body\": {\n" \
                   f"\"content\": \"{message}\"\n" \
                   "}\n" \
                   "}\n" \
                   "}"

        if team_id != teams_ids[-1]:
            payload += ", \n"
        else:
            payload += "\n"

    payload += "]\n" \
               "}"

    parsed_responses = requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()
    print(parsed_responses)
