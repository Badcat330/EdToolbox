import requests
import json

import Model.GraphAPI as API


def generate_assignment(member, assignment_id, task_type, task_format,
                        number_of_exercises, due_date, task_title, class_id):
    url = 'https://management-system-api.azurewebsites.net/createTask'
    student_info = API.get_user(member)
    student_email = student_info['userPrincipalName']
    student_name = student_info['givenName']
    student_surname = student_info['surname']

    headers = {
        'Content-Type': 'application/json'
    }

    payload = f'{{\"student_email\": \"{student_email}\", \n' \
              f'\"student_name\": \"{student_name}\", \n' \
              f'\"student_surname\": \"{student_surname}\", \n' \
              f'\"task_type\": \"{task_type}\", \n' \
              f'\"task_format\": \"{task_format}\", \n' \
              f'\"number_of_exercises\": {number_of_exercises}, \n' \
              f'\"assignment_end_time\": \"{due_date}\", \n' \
              f'\"task_title\": \"{task_title}\", \n' \
              f'\"assignment_link\": \"https://graph.microsoft.com/beta/education/classes/' \
              f'{class_id}/assignments/{assignment_id}\"}}'

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))
    json_resp = json.loads(response.json())
    task_url = json_resp['task_url']
    return f'{task_url}'


def create_assignments(class_id, task_type, task_format,
                       number_of_exercises,
                       due_date, name, student):
    assignments_id = API.create_assignment(class_id, due_date, name, student)
    if not assignments_id:
        return

    task_url = generate_assignment(student, assignments_id, task_type,
                                   task_format, number_of_exercises,
                                   due_date.replace('T', ' ').replace('Z', ''),
                                   name, class_id)

    API.add_resource_to_assignment(class_id, assignments_id, task_url)
