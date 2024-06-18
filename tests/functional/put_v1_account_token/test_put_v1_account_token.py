def test_put_v1_account_token(account_helper, prepare_user):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.account_token(login=login, password=password, email=email)
