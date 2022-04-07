from functools import partial
from collections import defaultdict
from multiprocessing.dummy import Pool as ThreadPool

import Model.GraphAPI as API

# table: (Email, Program, TeamsGroup, Status)
table_r = [("a", "a", "PsyManagement-Team", 1),]
           # ("b", "b", "a", 1),
           # ("c", "c", "a", 1),
           # ("a", "a", "b", 1),
           # ("b", "b", "b", 1),
           # ("c", "c", "b", 1),
           # ('d', 'd', 'b', 1)]
classes_in_organization = {}


def add_member_to_class(member_data, class_id):
    email, tag = member_data

    API.add_member_to_class(class_id, email)
    # TODO: add to tag group


def sync_class(class_element):
    global classes_in_organization

    class_name, table_members = class_element
    table_members_emails = set(table_members.keys())
    table_members_tags = set(table_members.values())

    if class_name not in classes_in_organization:
        classes_in_organization[class_name] = API.create_class(class_name)

    tags = API.get_tags_in_class(classes_in_organization[class_name])
    # Updating tags in class
    for tag_name in table_members_tags.difference(set(tags.keys())):
        tags[tag_name] = API.create_tag(
            classes_in_organization[class_name], tag_name)

    class_members = API.get_class_members(classes_in_organization[class_name])
    class_members_emails = set(class_members.keys())

    only_table = table_members_emails.difference(class_members_emails)
    only_class = class_members_emails.difference(table_members_emails)

    map(partial(add_member_to_class, team_id=classes_in_organization[class_name]), only_table)
    print(f"this command has {len(class_element[1])} elements")


def sync_classes_with_table(table_rows):
    # table_rows.sort(key=itemgetter(teams_name_index))
    global classes_in_organization
    classes_in_organization = API.get_classes_in_organization()

    teams_map = defaultdict(dict)
    for Email, Program, TeamsGroup, Status in [i for i in table_rows if i[3]]:
        teams_map[TeamsGroup][Email] = Program

    pool = ThreadPool()
    res = pool.map(sync_class, teams_map.items())

    pool.close()
    pool.join()



def sync_table_with_classes():
    ...
