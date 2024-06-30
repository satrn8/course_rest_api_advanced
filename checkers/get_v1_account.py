from datetime import datetime
from hamcrest import assert_that, has_property, has_properties, starts_with, all_of, instance_of, equal_to


class GetV1Account:
    @classmethod
    def check_response_values(cls, response):
        assert_that(
            response, all_of(
                has_property("resource", has_property("login", starts_with("alyona"))),
                has_property("resource", has_property("registration", instance_of(datetime))),
                has_property("resource", has_property("online", instance_of(datetime))),
                has_property(
                    "resource", has_properties({
                        "roles": [
                            "Guest",
                            "Player"
                        ]
                    })
                )
            ))
