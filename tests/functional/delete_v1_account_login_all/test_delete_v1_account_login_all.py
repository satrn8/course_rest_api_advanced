def test_delete_v1_account_login_all(auth_account_helper):
    auth_account_helper.dm_account_api.account_api.get_v1_account()
    auth_account_helper.dm_account_api.login_api.delete_v1_account_login_all()

