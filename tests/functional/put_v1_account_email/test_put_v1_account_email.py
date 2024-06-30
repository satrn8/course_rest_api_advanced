import random


def test_put_v1_account_email(account_helper, prepare_user):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    new_email = f"thisisanewmail{random.randint(1, 1000)}@mail.ru"
    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.change_email(login=login, password=password, email=new_email)
    account_helper.user_login(login=login, password=password)
