import random
import time

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

    def auth_client(self, login: str, password: str):
        json_data = {
            "login": login,
            "password": password
        }
        response = self.dm_account_api.login_api.post_v1_account_login(json_data=json_data)
        token = {
            "x-dm-auth-token": response.headers["x-dm-auth-token"]
        }
        self.dm_account_api.account_api.set_headers(token)
        self.dm_account_api.login_api.set_headers(token)
        return response

    def register_new_user(self, login: str, password: str, email: str):
        json_data = {
            'login': login,
            'email': email,
            'password': password
        }

        response = self.dm_account_api.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан {response.json()}"

        token = self.get_activation_token_by_login(login=login)
        assert token is not None, f"Токен для пользователя {login}, не был получен"

        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, f"Пользователь не был активирован"
        return response

    def user_login(self, login: str, password: str, remember_me: bool = True):
        json_data = {
            'login': login,
            'password': password,
            'rememberMe': remember_me
        }
        response = self.dm_account_api.login_api.post_v1_account_login(json_data=json_data)
        assert response.status_code == 200, f"Пользователь не смог авторизоваться"
        return response

    def change_email(self, login: str, password: str, email: str):
        new_email = f"{login}{random.randint(500, 1000)}@mail.ru"
        json_data = {
            'login': login,
            'password': password,
            'email': new_email
        }

        response = self.dm_account_api.account_api.put_v1_account_email(json_data=json_data)
        assert response.status_code == 200, f"Пользователь не смог изменить почту"

        token = self.get_activation_new_token_by_login(login, new_email)
        assert token is not None, f"Токен для пользователя {login}, не был получен"

        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, f"Пользователь не был активирован"

        return response

    def get_account_token(self, login: str):
        # Получить активационный токен
        token = self.get_activation_token_by_login(login=login)
        assert token is not None, f"Токен для пользователя {login}, не был получен"

        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, f"Пользователь не был активирован"

    def reset_user_password(self, login: str, email: str, **kwargs):
        json_data = {
            'login': login,
            'email': email
        }
        response = self.dm_account_api.account_api.post_v1_account_password(json_data=json_data)
        return response

    def change_user_password(self, login: str, token: str, oldPassword: str, newPassword: str, **kwargs):
        token = self.get_reset_token_by_login(login=login)
        json_data = {
            'login': login,
            'token': token,
            'oldPassword': oldPassword,
            'newPassword': newPassword
        }
        response = self.dm_account_api.account_api.put_v1_account_password(json_data=json_data)
        return response

    def delete_account_login(self, **kwargs):
        response = self.dm_account_api.login_api.delete_v1_account_login(**kwargs)
        return response == 204, "Пользователь не разлогинен"

    def delete_account_login_all(self, **kwargs):
        response = self.dm_account_api.login_api.delete_v1_account_login_all(**kwargs)
        assert response == 204, "Пользователь не разлогинен на всех устройствах"

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

    @retry(stop_max_attempt_number=5, retry_on_result=retry_if_result_none)
    def get_reset_token_by_login(self, login):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()["items"]:
            user_data = loads(item["Content"]["Body"])
            user_login = user_data["Login"]
            if user_login == login:
                user_data_dict = dict(user_data)
                if user_data_dict.get("ConfirmationLinkUri"):
                    token = str(user_data_dict.get("ConfirmationLinkUri")).split("/")[-1]
        return token
