import random
import time

from dm_api_account.models.change_user_email import ChangeEmail
from dm_api_account.models.change_user_password import ChangeUserPassword
from dm_api_account.models.login_credentials import LoginCredentials
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_user_password import ResetUserPassword
from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi
from json import loads
from retrying import retry


def retry_if_result_none(result):
    """Return True if we should retry (in this case when result is None), False otherwise"""
    return result is None


def retrier(function):
    def wrapper(*args, **kwargs):
        token = None
        count = 0
        while token is None:
            print(f"Попытка получения токена номер {count}")
            token = function(*args, **kwargs)
            count += 1
            if count == 5:
                raise AssertionError("Превышено количество попыток получения активационного токена!")
            if token:
                return token
            time.sleep(1)

    return wrapper


class AccountHelper:
    def __init__(self, dm_account_api: DMApiAccount, mailhog: MailHogApi):
        self.dm_account_api = dm_account_api
        self.mailhog = mailhog

    def auth_client(self, login: str, password: str, remember_me: bool = True, validate_response=False):
        login_credentials = LoginCredentials(
            login=login,
            password=password,
            remember_me=remember_me
        )
        response = self.dm_account_api.login_api.post_v1_account_login(login_credentials=login_credentials,
                                                                       validate_response=validate_response)
        token = {
            "x-dm-auth-token": response.headers["x-dm-auth-token"]
        }
        self.dm_account_api.account_api.set_headers(token)
        self.dm_account_api.login_api.set_headers(token)

    def register_new_user(self, login: str, password: str, email: str):
        registration = Registration(
            login=login,
            email=email,
            password=password
        )

        self.dm_account_api.account_api.post_v1_account(registration=registration)
        token = self.get_activation_token_by_login(login=login)
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        return response

    def user_login(self, login: str, password: str, remember_me: bool = True, validate_response=False):
        login_credentials = LoginCredentials(
            login=login,
            password=password,
            remember_me=remember_me
        )
        response = self.dm_account_api.login_api.post_v1_account_login(login_credentials=login_credentials,
                                                                       validate_response=validate_response)
        return response

    def change_email(self, login: str, email: str, password: str):
        change_email = ChangeEmail(
            login=login,
            email=email,
            password=password
        )
        self.dm_account_api.account_api.put_v1_account_email(change_email=change_email)
        token = self.get_activation_new_token_by_login(login, email)
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        return response

    def get_account_token(self, login: str):
        token = self.get_activation_token_by_login(login=login)
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)

    def change_user_password(self, login: str, email: str, old_password: str, new_password: str):
        token = self.user_login(login=login, password=old_password)
        self.dm_account_api.account_api.post_v1_account_password(
            reset_password=ResetUserPassword(
                login=login,
                email=email
            ),
            headers={
                "x-dm-auth-token": token.headers["x-dm-auth-token"]
            },
        )
        token = self.get_token(login=login, token_type="reset")
        self.dm_account_api.account_api.put_v1_account_password(
            change_password=ChangeUserPassword(
                login=login,
                oldPassword=old_password,
                newPassword=new_password,
                token=token
            )
        )

    def delete_account_login(self, **kwargs):
        self.dm_account_api.login_api.delete_v1_account_login(**kwargs)

    def delete_account_login_all(self, **kwargs):
        self.dm_account_api.login_api.delete_v1_account_login_all(**kwargs)

    @retry(stop_max_attempt_number=5, retry_on_result=retry_if_result_none)
    def get_activation_token_by_login(self, login):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()["items"]:
            user_data = loads(item["Content"]["Body"])
            user_login = user_data["Login"]
            if user_login == login:
                token = user_data["ConfirmationLinkUrl"].split("/")[-1]
        return token

    @retry(stop_max_attempt_number=5, retry_on_result=retry_if_result_none)
    def get_activation_new_token_by_login(self, login, email):
        new_token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()["items"]:
            user_data = loads(item["Content"]["Body"])
            new_email = item["Content"]["Headers"]["To"][0]
            if new_email == email:
                new_token = user_data["ConfirmationLinkUrl"].split("/")[-1]
        return new_token

    @retry(stop_max_attempt_number=5, retry_on_result=retry_if_result_none, wait_fixed=1000)
    def get_token(self, login, token_type="activation"):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()["items"]:
            user_data = loads(item["Content"]["Body"])
            user_login = user_data["Login"]
            activation_token = user_data.get("ConfirmationLinkUrl")
            reset_token = user_data.get("ConfirmationLinkUri")
            if user_login == login and activation_token and token_type == "activation":
                token = activation_token.split("/")[-1]
            elif user_login == login and reset_token and token_type == "reset":
                token = reset_token.split("/")[-1]
        return token
