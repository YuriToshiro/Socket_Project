import json
import os


def signup(username: str, password: str):
    path = os.path.join("Source", "UserAccount.json")
    if(not os.path.exists(path)):
        data = {}
        data['users'] = []
    else:
        data = json.load(open(path))

    for user in data['users']:
        if user['username'] == username:
            print("Username already exists")
            return

    data['users'].append({'username': username, 'password': password})
    with open(os.path.join('Source', 'UserAccount.json'), 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def login(username: str, password: str):
    path = os.path.join("Source", "UserAccount.json")
    if(not os.path.exists(path)):
        print("User not found")
        return
    else:
        data = json.load(open(path))

    for user in data['users']:
        if user['username'] == username:
            if user['password'] == password:
                print("Login successfully")
                return
            else:
                print("Wrong password")
                return

    print("Username not found")


signup('hoanggia', '2010')
login('admi', 'admin')
