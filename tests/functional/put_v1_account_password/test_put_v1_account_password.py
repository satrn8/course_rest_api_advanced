def test_put_v1_account_password(prepare_user, account_helper):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    new_password = "ytrewq54321"
    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.user_login(login=login, password=password)
    account_helper.change_user_password(login=login, email=email, old_password=password, new_password=new_password)
    account_helper.user_login(login=login, password=new_password)
