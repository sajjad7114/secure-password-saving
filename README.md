# secure-password-saving
In this project people can register, their username and password will be saved securely. We attach a salt to these username and passwod that is related to their encrypted words and their hash will be saved.
The users can input a website and the password for them. The websites' name will attached to the username and follows the main username and password way.
The website's password will be attached a long random salt with a flag to help reclaim that. then it will be encrypted and saved.
The encryption key is user's main key that is can be found with user's username and password. The large salt is there to avoid the attacker find password's length.
All encryptions are done with AES algorithm that is developed in AES.py file.
