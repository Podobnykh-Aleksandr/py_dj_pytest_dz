import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from model_bakery import baker
from django_testing.django_testing.wsgi import *
from students.models import Student, Course

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_get_first_course(client, course_factory, student_factory):
    course = course_factory(_quantity=1)
    course_id = str(course[0].id)
    print(course_id)

    url = reverse('courses-detail', args=(course_id,))
    response = client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert data['name'] == course[0].name


@pytest.mark.django_db
def test_create_list_courses(client, course_factory, student_factory):
    students = student_factory(_quantity=10)
    courses = course_factory(_quantity=20)

    url = reverse('courses-list')
    response = client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == len(courses)


@pytest.mark.django_db
def test_filter_id_courses(client, course_factory, student_factory):
    # Создаем курсы через фабрику, передать ID одного курса в фильтр, проверить результат запроса с фильтром;
    courses = course_factory(_quantity=10)
    course = courses[0]
    response = client.get('/api/v1/courses/', data={'course_id': course.id})

    assert response.status_code == 200
    data = response.json()
    assert data[0]['id'] == course.id

@pytest.mark.django_db
def test_filter_name_courses(client, course_factory, student_factory):
    students = student_factory(_quantity=10)
    courses = course_factory(_quantity=5)
    url = reverse('courses-list')
    response = client.get(url, {'name': courses[2].name})


    assert response.status_code == 200
    data = response.json()
    assert data[0]['name'] == courses[2].name


@pytest.mark.django_db
def test_create_course(client):
    count = Course.objects.count()

    url = reverse('courses-list')
    response = client.post(url, data={'name': 'Python'})

    assert response.status_code == 201
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_patch_course(client, course_factory, student_factory):

    students = student_factory(_quantity=30)
    courses = course_factory(_quantity=20)
    course_id = str(courses[5].id)

    url = reverse('courses-detail', args=(course_id,))
    response = client.patch(url, data={'name': 'Python'})
    data = response.json()

    assert response.status_code == 200
    assert data['name'] == 'Python'


@pytest.mark.django_db
def test_delete_course(client, course_factory, student_factory):
    students = student_factory(_quantity=30)
    courses = course_factory(_quantity=20)
    course_id = str(courses[7].id)
    count = Course.objects.count()

    url = reverse('courses-detail', args=(course_id,))
    response = client.delete(url)

    assert response.status_code == 204
    assert Course.objects.count() == count - 1