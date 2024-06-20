def test_put_v1_account_password(auth_account_helper, prepare_user, account_helper):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    new_password = "ytrewq54321"
    account_helper.change_user_password(login=login, email=email, password=password, new_password=new_password)
