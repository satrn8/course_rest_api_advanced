import datetime

from hamcrest import assert_that, has_property, has_properties, starts_with, all_of, instance_of, equal_to, has_key


def test_get_v1_account_auth(auth_account_helper):
    response = auth_account_helper.dm_account_api.account_api.get_v1_account()
    assert_that(
        response, all_of(
            has_property("resource", has_property("login", starts_with("alyona"))),
            has_property("resource", has_property("registration", instance_of(datetime.datetime))),
            has_property("resource", has_property("online", instance_of(datetime.datetime))),
            has_property(
                "resource", has_properties({
                    "roles": [
                        "Guest",
                        "Player"
                    ]
                })
            )
        ))

    print(response)
