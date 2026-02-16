import pytest
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

CustomUser = get_user_model()
fake = Faker()

@pytest.mark.django_db
def test_profile_view_permission():
    # Tworzymy użytkownika
    user = CustomUser.objects.create(username="testuser", password="securepassword123", email=fake.email())

    # Tworzymy użytkownika innego niż zalogowany
    other_user = CustomUser.objects.create(username="otheruser", password="securepassword123", email=fake.email())

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')


    response = client.get(f'/profile/{user.id}/')
    assert response.status_code == status.HTTP_200_OK  # Powinno być OK dla własnego profilu

    # Próba edycji profilu innego użytkownika
    response = client.get(f'/profile/{other_user.id}/')


    assert response.status_code == status.HTTP_403_FORBIDDEN  # Brak uprawnień do edytowania profilu innego użytkownika


@pytest.mark.django_db
def test_admin_user_permission():
    # Tworzymy użytkownika admina
    admin_user = CustomUser.objects.create(username="admin", password="adminpassword", email=fake.email(), is_staff=True, is_superuser=True)

    # Tworzymy zwykłego użytkownika
    normal_user = CustomUser.objects.create(username="normaluser", password="normalpassword", email=fake.email())

    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get('/profile/')
    assert response.status_code == status.HTTP_200_OK  # Admin powinien mieć dostęp

    # Logowanie zwykłego użytkownika
    refresh = RefreshToken.for_user(normal_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get('/profile/')
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Zwykły użytkownik nie ma dostępu


@pytest.mark.django_db
def test_special_resource_permission():
    # Tworzymy użytkownika z rolą 'editor'
    editor_user = CustomUser.objects.create(username="editor", password="editorpassword", email=fake.email(), role="editor")

    # Tworzymy zwykłego użytkownika
    normal_user = CustomUser.objects.create(username="normaluser", password="normalpassword", email=fake.email(), role="user")


    # Logowanie użytkownika z rolą editor
    refresh = RefreshToken.for_user(editor_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get('/special-resource/')
    assert response.status_code == status.HTTP_200_OK  # Użytkownik z rolą 'editor' ma dostęp

    # Logowanie zwykłego użytkownika
    refresh = RefreshToken.for_user(normal_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get('/special-resource/')
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Zwykły użytkownik nie ma dostępu


@pytest.mark.django_db
def test_unauthenticated_user_access():
    # Tworzymy użytkownika
    user = CustomUser.objects.create(username="testuser", password="securepassword123", email=fake.email())

    client = APIClient()

    # Próba dostępu do endpointu, który wymaga logowania (np. /profile/)
    response = client.get(f'/profile/{user.id}/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Nieautoryzowany użytkownik nie ma dostępu

    # Logowanie użytkownika
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    response = client.get(f'/profile/{user.id}/')
    assert response.status_code == status.HTTP_200_OK  # Zalogowany użytkownik ma dostęp


@pytest.mark.django_db
def test_unauthorized_user_edit_other_profile():
    # Tworzymy dwóch użytkowników
    user = CustomUser.objects.create(username="testuser", password="securepassword123", email=fake.email())
    other_user = CustomUser.objects.create(username="otheruser", password="securepassword123", email=fake.email())



    # Logowanie użytkownika 'testuser'
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Próba edytowania profilu innego użytkownika
    response = client.put(f'/profile/{other_user.id}/', {'username': 'newusername'})
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Użytkownik nie ma prawa edytować obcego profilu


@pytest.mark.django_db
def test_admin_user_can_edit_users():
    # Tworzymy użytkownika admina i normalnego użytkownika
    admin_user = CustomUser.objects.create(username="admin", password="adminpassword", email=fake.email(), is_staff=True, is_superuser=True)
    normal_user = CustomUser.objects.create(username="normaluser", password="normalpassword", email=fake.email())


    # Logowanie admina
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Próba edytowania użytkownika przez admina
    response = client.patch(f'/profile/{normal_user.id}/', {'username': 'newusername'})
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.status_code == status.HTTP_200_OK  # Admin ma prawo edytować użytkowników


@pytest.mark.django_db
def test_editor_user_access_to_special_resource():
    # Tworzymy użytkownika z rolą 'editor'
    editor_user = CustomUser.objects.create(username="editor", password="editorpassword", email=fake.email(), role="editor")

    # Logowanie użytkownika z rolą editor
    refresh = RefreshToken.for_user(editor_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Dostęp do zasobu 'special-resource'
    response = client.get('/special-resource/')
    assert response.status_code == status.HTTP_200_OK  # Użytkownik z rolą 'editor' ma dostęp


@pytest.mark.django_db
def test_user_with_no_role_cannot_access_special_resource():
    # Tworzymy użytkownika bez roli 'editor'
    normal_user = CustomUser.objects.create(username="normaluser", password="normalpassword", email=fake.email(), role="user")


    # Logowanie użytkownika bez roli 'editor'
    refresh = RefreshToken.for_user(normal_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Próba dostępu do zasobu 'special-resource'
    response = client.get('/special-resource/')
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Użytkownik bez roli 'editor' nie ma dostępu


@pytest.mark.django_db
def test_admin_user_can_create_new_user():
    # Tworzymy użytkownika admina
    admin_user = CustomUser.objects.create(username="admin", password="adminpassword", email=fake.email(), is_staff=True, is_superuser=True)


    # Logowanie admina
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Próba utworzenia nowego użytkownika przez admina
    data = {'username': 'newuser', 'password': 'newpassword123', 'email': 'newuser@example.com'}
    response = client.post('/profile/', data)
    assert response.status_code == status.HTTP_201_CREATED  # Admin powinien móc tworzyć nowych użytkowników
