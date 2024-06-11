import pprint
import random
from json import loads

from dm_api_account.apis.account_api import AccountApi
from dm_api_account.apis.login_api import LoginApi
from api_mailhog.apis.mailhog_api import MailhogApi


def test_put_v1_account_email():
    # Регистрация пользователя
    account_api = AccountApi(host="http://5.63.153.31:5051")
    login_api = LoginApi(host="http://5.63.153.31:5051")
    mailhog_api = MailhogApi(host="http://5.63.153.31:5025")

    login = f"alyona{random.randint(100, 500)}"
    password = "qwerty12345"
    email = f'{login}@mail.ru'

    json_data = {
        'login': login,
        'email': email,
        'password': password
    }
    response = account_api.post_v1_account(json_data=json_data)
    assert response.status_code == 201, f"Пользователь не был создан {response.json()}"

    # Получить письма из почтового сервера
    response = mailhog_api.get_api_v2_messages()
    assert response.status_code == 200, f"Письма не были получены"

    # Получить активационный токен
    token = get_activation_token_by_login(login, response)
    assert token is not None, f"Токен для пользователя {login}, не был получен"

    # Активация пользователя
    response = account_api.put_v1_account_token(token=token)
    assert response.status_code == 200, f"Пользователь не был активирован"

    # Авторизоваться
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True
    }
    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 200, f"Пользователь не смог авторизоваться"

    # Смена email
    new_email = f"{login}{random.randint(500, 1000)}@mail.ru"
    json_data = {
        'login': login,
        'password': password,
        'email': new_email
    }
    response = account_api.put_v1_account_email(json_data=json_data)
    assert response.status_code == 200, f"Пользователь не смог изменить почту"

    # Авторизация после смены email
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True
    }
    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 403, f"Пользователь смог авторизоваться"

    # Активация токена
    response = account_api.put_v1_account_token(token=token)
    assert response.status_code == 200, f"Пользователь не был активирован"

    # Авторизация после активации токена
    json_data = {
        'login': login,
        'password': password,
        'rememberMe': True
    }
    response = login_api.post_v1_account_login(json_data=json_data)
    assert response.status_code == 200, f"Пользователь не смог авторизоваться"


def get_activation_token_by_login(login, response):
    token = None
    for item in response.json()["items"]:
        user_data = loads(item["Content"]["Body"])
        user_login = user_data["Login"]
        if user_login == login:
            token = user_data["ConfirmationLinkUrl"].split("/")[-1]
    return token
