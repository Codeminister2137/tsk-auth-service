import pytest
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker()

@pytest.mark.django_db
def test_profile_view_permission():
    # Tworzymy użytkownika
    user = User.objects.create_user(username="testuser", password="securepassword123", email=fake.email())

    # Tworzymy użytkownika innego niż zalogowany
    other_user = User.objects.create_user(username="otheruser", password="securepassword123", email=fake.email())

    client = APIClient()

    # Zalogowanie zwykłego użytkownika
    client.login(username="testuser", password="securepassword123")
    response = client.get('/profile/')
    assert response.status_code == status.HTTP_200_OK  # Powinno być OK dla własnego profilu

    # Próba edycji profilu innego użytkownika
    response = client.get(f'/profile/{other_user.id}/')
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Brak uprawnień do edytowania profilu innego użytkownika


@pytest.mark.django_db
def test_admin_user_permission():
    # Tworzymy użytkownika admina
    admin_user = User.objects.create_user(username="admin", password="adminpassword", email=fake.email(), is_staff=True)

    # Tworzymy zwykłego użytkownika
    normal_user = User.objects.create_user(username="normaluser", password="normalpassword", email=fake.email())

    client = APIClient()

    # Logowanie admina
    client.login(username="admin", password="adminpassword")
    response = client.get('/admin/users/')
    assert response.status_code == status.HTTP_200_OK  # Admin powinien mieć dostęp

    # Logowanie zwykłego użytkownika
    client.login(username="normaluser", password="normalpassword")
    response = client.get('/admin/users/')
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Zwykły użytkownik nie ma dostępu


@pytest.mark.django_db
def test_special_resource_permission():
    # Tworzymy użytkownika z rolą 'editor'
    editor_user = User.objects.create_user(username="editor", password="editorpassword", email=fake.email(), role="editor")

    # Tworzymy zwykłego użytkownika
    normal_user = User.objects.create_user(username="normaluser", password="normalpassword", email=fake.email(), role="user")

    client = APIClient()

    # Logowanie użytkownika z rolą editor
    client.login(username="editor", password="editorpassword")
    response = client.get('/special-resource/')
    assert response.status_code == status.HTTP_200_OK  # Użytkownik z rolą 'editor' ma dostęp

    # Logowanie zwykłego użytkownika
    client.login(username="normaluser", password="normalpassword")
    response = client.get('/special-resource/')
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Zwykły użytkownik nie ma dostępu


@pytest.mark.django_db
def test_unauthenticated_user_access():
    # Tworzymy użytkownika
    user = User.objects.create_user(username="testuser", password="securepassword123", email=fake.email())

    client = APIClient()

    # Próba dostępu do endpointu, który wymaga logowania (np. /profile/)
    response = client.get('/profile/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Nieautoryzowany użytkownik nie ma dostępu

    # Logowanie użytkownika
    client.login(username="testuser", password="securepassword123")
    response = client.get('/profile/')
    assert response.status_code == status.HTTP_200_OK  # Zalogowany użytkownik ma dostęp


@pytest.mark.django_db
def test_unauthorized_user_edit_other_profile():
    # Tworzymy dwóch użytkowników
    user = User.objects.create_user(username="testuser", password="securepassword123", email=fake.email())
    other_user = User.objects.create_user(username="otheruser", password="securepassword123", email=fake.email())

    client = APIClient()

    # Logowanie użytkownika 'testuser'
    client.login(username="testuser", password="securepassword123")

    # Próba edytowania profilu innego użytkownika
    response = client.put(f'/profile/{other_user.id}/', {'username': 'newusername'})
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Użytkownik nie ma prawa edytować obcego profilu


@pytest.mark.django_db
def test_admin_user_can_edit_users():
    # Tworzymy użytkownika admina i normalnego użytkownika
    admin_user = User.objects.create_user(username="admin", password="adminpassword", email=fake.email(), is_staff=True)
    normal_user = User.objects.create_user(username="normaluser", password="normalpassword", email=fake.email())

    client = APIClient()

    # Logowanie admina
    client.login(username="admin", password="adminpassword")

    # Próba edytowania użytkownika przez admina
    response = client.put(f'/admin/users/{normal_user.id}/', {'username': 'newusername'})
    assert response.status_code == status.HTTP_200_OK  # Admin ma prawo edytować użytkowników


@pytest.mark.django_db
def test_editor_user_access_to_special_resource():
    # Tworzymy użytkownika z rolą 'editor'
    editor_user = User.objects.create_user(username="editor", password="editorpassword", email=fake.email(), role="editor")
    client = APIClient()

    # Logowanie użytkownika z rolą editor
    client.login(username="editor", password="editorpassword")

    # Dostęp do zasobu 'special-resource'
    response = client.get('/special-resource/')
    assert response.status_code == status.HTTP_200_OK  # Użytkownik z rolą 'editor' ma dostęp


@pytest.mark.django_db
def test_user_with_no_role_cannot_access_special_resource():
    # Tworzymy użytkownika bez roli 'editor'
    normal_user = User.objects.create_user(username="normaluser", password="normalpassword", email=fake.email(), role="user")
    client = APIClient()

    # Logowanie użytkownika bez roli 'editor'
    client.login(username="normaluser", password="normalpassword")

    # Próba dostępu do zasobu 'special-resource'
    response = client.get('/special-resource/')
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Użytkownik bez roli 'editor' nie ma dostępu


@pytest.mark.django_db
def test_admin_user_can_create_new_user():
    # Tworzymy użytkownika admina
    admin_user = User.objects.create_user(username="admin", password="adminpassword", email=fake.email(), is_staff=True)

    client = APIClient()

    # Logowanie admina
    client.login(username="admin", password="adminpassword")

    # Próba utworzenia nowego użytkownika przez admina
    data = {'username': 'newuser', 'password': 'newpassword123', 'email': 'newuser@example.com'}
    response = client.post('/admin/users/', data)
    assert response.status_code == status.HTTP_201_CREATED  # Admin powinien móc tworzyć nowych użytkowników
