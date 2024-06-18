import pprint
import random
import structlog

from json import loads

from helpers.account_helper import AccountHelper
from rest_client.configuration import Configuration as MailhogConfiguration
from rest_client.configuration import Configuration as DmApiConfiguration
from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(
            indent=4,
            ensure_ascii=True,
            # sort_keys=True
        )
    ]
)


def test_put_v1_account_email(account_helper, prepare_user):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email

    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.change_email(login=login, password=password, email=email)
    account_helper.user_login(login=login, password=password)
