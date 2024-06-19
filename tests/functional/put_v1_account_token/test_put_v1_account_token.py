def test_put_v1_account_token(account_helper, prepare_user, auth_account_helper):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.get_account_token(login=login)
