def test_put_v1_account_password(auth_account_helper, prepare_user, account_helper):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    new_password = "ytrewq54321"
    token = account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.reset_user_password(login=login, email=email, headers=token)
    new_token = account_helper.change_token(login=login)
    account_helper.change_user_password(login=login, token=new_token, oldPassword=password, newPassword=new_password,
                                        headers=new_token)
    account_helper.user_login(login=login, password=new_password, remember_me=True)
