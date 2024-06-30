import pytest

from checkers.http_checkers import check_status_code_http
from checkers.post_v1_account import PostV1Account


def test_post_v1_account(account_helper, prepare_user):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    response = account_helper.user_login(login=login, password=password, validate_response=True)
    PostV1Account.check_response_values(response)


@pytest.mark.parametrize(
    "creds",
    [
        ("nik998", "999", "nik999@mail.ru"),
        ("n", "nik9999", "nik9991@mail.ru"),
        ("nik99991", "nik99991", "nik99911mail.ru")
    ]
)
def test_post_v1_account_incorrect_data(account_helper, creds):
    login, password, email = creds
    with check_status_code_http(400, "Validation failed"):
        account_helper.register_new_user(login=login, password=password, email=email)
        account_helper.user_login(login=login, password=password, validate_response=True)
