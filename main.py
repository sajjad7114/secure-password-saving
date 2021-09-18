from AES import AES
import hashlib
import json
import random
import string

KEY1 = "VERYIMPORTANTKEY"
KEY2 = "KEYFOR@MASTERKEY"
LENGTH = 160
aes = AES()


def to_secret(plain_text, key):
    plain_text = add_padding(plain_text, 0)
    for i in range(16 - len(plain_text) % 16):
        plain_text.join(str(i%10))
    salt = aes.encrypt(plain_text, key)
    hashed_text = hashlib.sha512(plain_text.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    return hashed_text


def generate_master(username, password):
    user_master_key = aes.vec2word(aes.hex2vec(to_secret(username+password, KEY2)))[:16]
    return user_master_key


def sign():
    sign_mode = input("SignIn[i] / SignUp[u]: ")
    username = input("Enter username: ")
    secret_username = to_secret(username, KEY1)
    password = input("Enter password: ")
    secret_password = to_secret(password, KEY1)

    if sign_mode == 'u':
        with open('db.json', 'r+') as db:
            data = json.load(db)
            users = data["users"]
            try:
                password = users[secret_username]
                print("username exists! enter another username...")
                db.close()
                return False, False
            except:
                data["users"][secret_username] = secret_password
                data[username] = {}
                db.seek(0)
                json.dump(data, db, indent=4)
                db.close()
                return username, password
    else:
        with open('db.json') as db:
            data = json.load(db)
            users = data["users"]
            try:
                s_password = users[secret_username]
                if s_password == secret_password:
                    db.close()
                    return username, password
                print("password incorrect")
                db.close()
                return False, False
            except:
                print("username not found!")
                db.close()
                return False, False


def remove_padding(padded):
    raw = ''
    mode = 'read'
    for char in padded:
        if char == 'E' and mode == 'read':
            mode = 'escape'
        elif char == 'F' and mode == 'read':
            break
        else:
            raw += char
            mode = 'read'
    return raw


def add_padding(raw, min_len):
    padded = ''
    for char in raw:
        if char == 'F' or char == 'E':
            padded += 'E'
        padded += char
    padded += 'F'

    if min_len > 0:
        letters = string.ascii_letters + string.digits + string.punctuation
        if len(padded) < min_len:
            length = min_len - len(padded)
        else:
            length = 16 - len(padded) % 16
        random_part = ''.join(random.choice(letters) for i in range(length))
        padded += random_part

    return padded


def add_web_password(username, password):
    website = input("Enter Website: ")
    secret_website = to_secret(website+username, KEY1)
    with open('db.json', 'r+') as db:
        data = json.load(db)
        try:
            old_password = data[username][secret_website]
            print("website exists!")
            db.close()
            return False
        except:
            user_master_key = generate_master(username, password)
            web_password = input("Enter password: ")
            data[username][secret_website] = aes.encrypt(add_padding(web_password, LENGTH), user_master_key)
            db.seek(0)
            json.dump(data, db, indent=4)
            db.close()
            return True


def get_password(username, password):
    website = input("Enter Website: ")

    with open('db.json') as db:
        data = json.load(db)
        try:
            web_password = data[username][to_secret(website+username, KEY1)]
            user_master_key = generate_master(username, password)
            db.close()
            return remove_padding(aes.decrypt(web_password, user_master_key))
        except:
            print("website did not found")
            db.close()
            return False


def change_web_password(username, password):
    website = input("Enter Website: ")
    secret_website = to_secret(website+username, KEY1)

    with open('db.json', 'r+') as db:
        data = json.load(db)
        try:
            web_password = data[username][secret_website]
            new_web_password = input("Enter Password: ")
            user_master_key = generate_master(username, password)
            data[username][secret_website] = aes.encrypt(add_padding(new_web_password, LENGTH),
                                                         user_master_key)
            db.seek(0)
            json.dump(data, db, indent=4)
            db.close()
            return True
        except:
            print("website did not found")
            db.close()
            return False


def change_password(username, password):
    new_password = input("Enter new password: ")
    secret_username = to_secret(username, KEY1)
    secret_password = to_secret(new_password, KEY1)
    with open('db.json', 'r+') as users_file:
        data = json.load(users_file)
        data["users"][secret_username] = secret_password

        web_passwords = data[username]
        user_master_key = generate_master(username, password)
        new_user_master_key = generate_master(username, new_password)
        for key in web_passwords:
            value = data[username][key]
            web_password = remove_padding(aes.decrypt(value, user_master_key))
            data[username][key] = aes.encrypt(add_padding(web_password, LENGTH), new_user_master_key)
        users_file.seek(0)
        json.dump(data, users_file, indent=4)
        users_file.close()

    return new_password


def user_pad(username, password):
    print("1) Change password")
    print("2) Add website password")
    print("3) Get a website password")
    print("4) Change a website password")
    print("5) Exit")
    choice = input("Enter a choice: ")

    if choice == '1':
        password = change_password(username, password)
        return password
    if choice == '2':
        print(add_web_password(username, password))
        return password
    if choice == '3':
        web_password = get_password(username, password)
        if web_password:
            print(web_password)
        return password
    if choice == '4':
        print(change_web_password(username, password))
        return password
    if choice == '5':
        return False


if __name__ == '__main__':
    usrname, pssword = sign()
    if usrname:
        pssword = user_pad(usrname, pssword)
        while pssword:
            pssword = user_pad(usrname, pssword)
