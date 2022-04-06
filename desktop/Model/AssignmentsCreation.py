from functools import partial
import requests
import json

import Model.GraphAPI as API


def generate_assignment(member, assignment_id, task_type,
                        task_format, number_of_exercises, class_id):
    url = 'http://localhost:5000/createTask'

    headers = {
        'Content-Type': 'application/json'
    }

    payload = f'{{\"mail\": \"{member}\", ' \
              f'\"task_type\": \"{task_type}\", ' \
              f'\"task_format\": \"{task_format}\", ' \
              f'\"number_of_exercises\": {number_of_exercises},' \
              f'\"assignment_link\": \"https://graph.microsoft.com/beta/education/classes/' \
              f'{class_id}/assignments/{assignment_id}\"}}'

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf8')).json()
    task_url = json.loads(response)['task_url']
    return f'{task_url}/{member}'


def create_assignments(members, class_id,
                       task_type, task_format, number_of_exercises,
                       due_date, name):
    assignments_ids = list(map(partial(API.create_assignment,
                                       class_id,
                                       due_date,
                                       name), members))

    urls = list(map(partial(generate_assignment,
                            task_type=task_type,
                            task_format=task_format,
                            number_of_exercises=number_of_exercises,
                            class_id=class_id),
                    members, assignments_ids))

    list(map(partial(API.add_resource_to_assignment,
                     class_id), assignments_ids, urls))
