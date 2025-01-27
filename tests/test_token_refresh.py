import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_refresh_token():
    client = APIClient()
    # Tworzymy użytkownika
    user = User.objects.create_user(username="testuser", password="securepassword123")

    # Logowanie
    login_data = {
        "username": "testuser",
        "password": "securepassword123"
    }
    login_response = client.post('/auth/login/', login_data)
    assert login_response.status_code == status.HTTP_200_OK
    refresh_token = login_response.data["refresh"]

    # Próba odświeżenia tokenu
    refresh_data = {"refresh": refresh_token}
    refresh_response = client.post('/auth/refresh/', refresh_data)
    assert refresh_response.status_code == status.HTTP_200_OK
    assert "access" in refresh_response.data

@pytest.mark.django_db
def test_refresh_token_invalid():
    client = APIClient()
    data = {
        "refresh": "invalidtoken123"  # Niepoprawny token
    }
    response = client.post('/auth/refresh/', data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert response.data["detail"] == "Token is invalid or expired"
