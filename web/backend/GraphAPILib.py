import requests

import variables as Variables


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


def get_submissions(assignment_link):
    url = f"{assignment_link}/submissions"

    headers = {
        'Authorization': Variables.user_token,
    }

    response = requests.request("GET", url, headers=headers).json()
    print(response)
    submission_id = response['value'][0]['id']

    return submission_id


def submit_task(submission_link):
    url = f"{submission_link}/submit"

    headers = {
        'Authorization': Variables.user_token,
    }

    response = requests.request("POST", url, headers=headers).json()
    print(response)


def return_submission(submission_link):
    url = f"{submission_link}/return"

    headers = {
        'Authorization': Variables.user_token,
    }

    response = requests.request("POST", url, headers=headers).json()
    print(response)


def patch_outcome(submission_link, outcome, grade, comment):
    headers = {
        'Authorization': Variables.user_token,
        'Content-Type': 'application/json'
    }

    outcome_id = None
    payload = None

    if outcome['@odata.type'] == '#microsoft.graph.educationPointsOutcome':
        outcome_id = outcome['id']
        payload = '{\n' \
                  f'\"@odata.type\": \"#microsoft.graph.educationPointsOutcome\",\n' \
                  '\"points\": {\n' \
                  '\"@odata.type\": \"microsoft.graph.educationAssignmentPointsGrade\",\n' \
                  f'\"points\": {grade}\n' \
                  '}\n' \
                  '}'
    elif outcome['@odata.type'] == '#microsoft.graph.educationFeedbackOutcome' and comment:
        outcome_id = outcome['id']
        payload = '{\n' \
                  f'\"@odata.type\": \"#microsoft.graph.educationFeedbackOutcome\",\n' \
                  '\"feedback\": {\n' \
                  '\"text\": {\n' \
                  f'\"content\": \"{comment}\",\n' \
                  f'\"contentType\": \"text\"\n' \
                  '}\n' \
                  '}\n' \
                  '}'

    if outcome_id and payload:
        url = f"{submission_link}/outcomes/{outcome_id}"
        response = requests.request("PATCH", url, headers=headers,
                                    data=payload.encode('utf8')).json()
        print(response)


def grade_task(submission_link, grade, comment):
    url = f"{submission_link}/outcomes"

    headers = {
        'Authorization': Variables.user_token,
    }

    response = requests.request("GET", url, headers=headers).json()
    print(response)

    for outcome in response['value']:
        patch_outcome(submission_link, outcome, grade, comment)

    return_submission(submission_link)
