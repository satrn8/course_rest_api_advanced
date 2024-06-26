import requests

from dm_api_account.models.change_user_email import ChangeEmail
from dm_api_account.models.change_user_password import ChangeUserPassword
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_user_password import ResetUserPassword
from dm_api_account.models.user_details_envelope import UserDetailsEnvelope
from dm_api_account.models.user_envelope import UserEnvelope
from rest_client.client import RestClient


class AccountApi(RestClient):
    def post_v1_account(self, registration: Registration):
        """
        Register new user
        :return:
        """
        response = self.post(
            path=f'/v1/account',
            json=registration.model_dump(exclude_none=True, by_alias=True)
        )
        return response

    def get_v1_account(self, validate_response=True, **kwargs):
        """
        Get current user
        :return:
        """
        response = self.get(
            path=f'/v1/account',
            **kwargs
        )
        if validate_response:
            return UserDetailsEnvelope(**response.json())
        return response

    def put_v1_account_token(self, token, validate_response=True):
        """
        Activate registered user
        :param token:
        :return:
        """
        headers = {
            'accept': 'text/plain'
        }
        response = self.put(
            path=f'/v1/account/{token}',
            headers=headers
        )
        if validate_response:
            return UserEnvelope(**response.json())
        return response

    def put_v1_account_email(self, change_email: ChangeEmail, validate_response=True):
        """
        Change registered user email
        :param token:
        :return:
        """
        headers = {
            'accept': 'text/plain'
        }
        response = self.put(
            path=f'/v1/account/email',
            headers=headers,
            json=change_email.model_dump(exclude_none=True, by_alias=True)
        )
        if validate_response:
            return UserEnvelope(**response.json())
        return response

    def post_v1_account_password(self, reset_password: ResetUserPassword, **kwargs):
        """
        Reset registered user password
        :param json_data:
        :param kwargs:
        :return:
        """
        response = self.post(
            path=f'/v1/account/password',
            json=reset_password.model_dump(exclude_none=True, by_alias=True),
            **kwargs
        )
        return response

    def put_v1_account_password(self, change_password: ChangeUserPassword, validate_response=True):
        response = self.put(
            path=f"/v1/account/password",
            json=change_password.model_dump(exclude_none=True, by_alias=True),
        )
        if validate_response:
            return UserEnvelope(**response.json())
        return response
