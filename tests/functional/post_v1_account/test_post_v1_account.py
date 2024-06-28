import datetime

import pytest
from hamcrest import assert_that, has_property, has_properties, starts_with, all_of, instance_of, equal_to
from checkers.http_checkers import check_status_code_http


def test_post_v1_account(account_helper, prepare_user):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    response = account_helper.user_login(login=login, password=password, validate_response=True)
    assert_that(
        response, all_of(
            has_property("resource", has_property("login", starts_with("alyona"))),
            has_property("resource", has_property("registration", instance_of(datetime.datetime))),
            has_property(
                "resource", has_properties({
                    "rating": has_properties({
                        "enabled": equal_to(True),
                        "quality": equal_to(0),
                        "quantity": equal_to(0)
                    })
                })
            )
        )
    )

    print(response)


@pytest.mark.parametrize(
    "creds",
    [
        ("nik999", "999", "nik999@mail.ru"),
        ("n", "nik9991", "nik9991@mail.ru"),
        ("nik99911", "nik99911", "nik99911mail.ru")
    ]
)
def test_post_v1_account_incorrect_data(account_helper, creds):
    login, password, email = creds
    with check_status_code_http(400, "Validation failed"):
        account_helper.register_new_user(login=login, password=password, email=email)
        account_helper.user_login(login=login, password=password, validate_response=True)
