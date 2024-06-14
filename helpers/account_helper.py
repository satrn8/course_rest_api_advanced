import random

from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi
from json import loads


class AccountHelper:
    def __init__(self, dm_account_api: DMApiAccount, mailhog: MailHogApi):
        self.dm_account_api = dm_account_api
        self.mailhog = mailhog

    def register_new_user(self, login: str, password: str, email: str):
        json_data = {
            'login': login,
            'email': email,
            'password': password
        }

        response = self.dm_account_api.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан {response.json()}"

        response = self.mailhog.mailhog_api.get_api_v2_messages()
        assert response.status_code == 200, f"Письма не были получены"

        token = self.get_activation_token_by_login(login=login, response=response)
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

        response = self.mailhog.mailhog_api.get_api_v2_messages()
        assert response.status_code == 200, f"Письма не были получены"

        token = self.activation_new_token(login, response, new_email)
        assert token is not None, f"Токен для пользователя {login}, не был получен"

        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, f"Пользователь не был активирован"

        return response

    def account_token(self, login: str, password: str, email: str):
        json_data = {
            'login': login,
            'email': email,
            'password': password
        }

        response = self.dm_account_api.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан {response.json()}"

        # Получить письма из почтового сервера
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        assert response.status_code == 200, f"Письма не были получены"

        # Получить активационный токен
        token = self.get_activation_token_by_login(login=login, response=response)
        assert token is not None, f"Токен для пользователя {login}, не был получен"

    @staticmethod
    def get_activation_token_by_login(login, response):
        token = None
        for item in response.json()["items"]:
            user_data = loads(item["Content"]["Body"])
            user_login = user_data["Login"]
            if user_login == login:
                token = user_data["ConfirmationLinkUrl"].split("/")[-1]
                print(f"старый токен {token}")
        return token

    @staticmethod
    def activation_new_token(login, response, email):
        new_token = None
        for item in response.json()["items"]:
            user_data = loads(item["Content"]["Body"])
            new_email = item["Content"]["Headers"]["To"][0]
            if new_email == email:
                new_token = user_data["ConfirmationLinkUrl"].split("/")[-1]
                print(f"новый токен {new_token}")
        return new_token
