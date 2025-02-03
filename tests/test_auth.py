import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_register_user():
    client = APIClient()
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123"
    }
    response = client.post('/auth/register/', data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
def test_login_user():
    # Tworzymy użytkownika
    user = User.objects.create_user(username="testuser", password="securepassword123")

    client = APIClient()
    data = {
        "username": "testuser",
        "password": "securepassword123"
    }

    response = client.post('/auth/login/', data)
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_register_user_invalid_data():
    client = APIClient()

    # Brakujące pole "username"
    data = {
        "email": "testuser@example.com",
        "password": "securepassword123"
    }
    response = client.post('/auth/register/', data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data

    # Brakujące pole "password"
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
    }
    response = client.post('/auth/register/', data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.data

    # Złe dane w polu email
    data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "securepassword123"
    }
    response = client.post('/auth/register/', data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_login_user_invalid_password():
    # Tworzymy użytkownika
    User.objects.create_user(username="testuser", password="securepassword123")

    client = APIClient()
    data = {
        "username": "testuser",
        "password": "wrongpassword123"  # Niepoprawne hasło
    }
    response = client.post('/auth/login/', data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert response.data["detail"] == "No active account found with the given credentials"

@pytest.mark.django_db
def test_login_user_not_found():
    client = APIClient()
    data = {
        "username": "nonexistentuser",
        "password": "somepassword"
    }
    response = client.post('/auth/login/', data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert response.data["detail"] == "No active account found with the given credentials"


@pytest.mark.django_db
def test_change_password():
    # Tworzymy użytkownika
    user = User.objects.create_user(username="testuser", password="oldpassword123")

    client = APIClient()
    client.login(username='testuser', password='oldpassword123')

    # Nowe hasło
    data = {
        "old_password": "oldpassword123",
        "new_password": "newpassword123"
    }

    response = client.post('/auth/change-password/', data)
    assert response.status_code == status.HTTP_200_OK
    assert 'message' in response.data
    assert response.data["message"] == "Password successfully changed"

    # Próba logowania po zmianie hasła
    client.logout()
    login_data = {
        "username": "testuser",
        "password": "newpassword123"
    }
    login_response = client.post('/auth/login/', login_data)
    assert login_response.status_code == status.HTTP_200_OK
    assert "access" in login_response.data
    assert "refresh" in login_response.data


@pytest.mark.django_db
def test_login_inactive_user():
    # Tworzymy nieaktywnego użytkownika
    user = User.objects.create_user(username="testuser", password="securepassword123", is_active=False)

    client = APIClient()
    data = {
        "username": "testuser",
        "password": "securepassword123"
    }
    response = client.post('/auth/login/', data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert response.data["detail"] == "No active account found with the given credentials"
