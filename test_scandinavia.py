import requests
import allure
import pytest

BASE_URL = "https://jsonplaceholder.typicode.com/posts"

@allure.feature("CRUD операции с /posts")
class TestPostsAPI:
    @allure.story("Создание нового поста")
    def test_create_post(self):
        payload = {"title": "foo", "body": "bar", "userId": 1}
        response = requests.post(BASE_URL, json=payload)
        assert response.status_code == 201, "Ошибка: неверный статус-код"
        assert "id" in response.json(), "Ошибка: нет ID в ответе"

    @allure.story("Получение списка постов")
    def test_get_all_posts(self):
        response = requests.get(BASE_URL)
        assert response.status_code == 200, "Ошибка: неверный статус-код"
        assert isinstance(response.json(), list), "Ошибка: ответ не является списком"

    @allure.story("Получение поста по ID")
    @pytest.mark.parametrize("post_id", [1, 50, 100])
    def test_get_post_by_id(self, post_id):
        response = requests.get(f"{BASE_URL}/{post_id}")
        assert response.status_code == 200, "Ошибка: неверный статус-код"
        assert response.json()["id"] == post_id, "Ошибка: ID не совпадает"

    @allure.story("Обновление поста (PUT)")
    def test_update_post_put(self):
        """API принимает PUT-запрос, но фактически не изменяет данные"""
        payload = {"title": "updated", "body": "new content", "userId": 1}
        response = requests.put(f"{BASE_URL}/1", json=payload)
        assert response.status_code == 200, "Ошибка: неверный статус-код"
        assert response.json()["title"] == "updated", "Ошибка: заголовок не изменился"

    @allure.story("Частичное обновление поста (PATCH)")
    def test_update_post_patch(self):
        """API принимает PATCH-запрос, но фактически не изменяет данные"""
        payload = {"title": "patched"}
        response = requests.patch(f"{BASE_URL}/1", json=payload)
        assert response.status_code == 200, "Ошибка: неверный статус-код"
        assert response.json()["title"] == "patched", "Ошибка: заголовок не изменился"

    @allure.story("Удаление поста")
    def test_delete_post(self):
        """API принимает DELETE-запрос, но данные не удаляются"""
        response = requests.delete(f"{BASE_URL}/1")
        assert response.status_code == 200, "Ошибка: неверный статус-код"

    @allure.story("Негативный тест: получение несуществующего поста")
    @pytest.mark.parametrize("post_id", [0, 101, 9999])
    def test_get_nonexistent_post(self, post_id):
        response = requests.get(f"{BASE_URL}/{post_id}")
        assert response.status_code == 404, "Ошибка: ожидался статус 404"

    @allure.story("Негативный тест: передача некорректного JSON")
    def test_create_post_with_invalid_json(self):
        headers = {"Content-Type": "application/json"}
        payload = '{"title": 123, "body": False, "userId": "abc"}'  # Некорректный JSON
        response = requests.post(BASE_URL, data=payload, headers=headers)
        assert response.status_code in [400, 500], "Ошибка: ожидался статус 400 или 500 при некорректном JSON"

        # При ручной проверке через Postman запроса с телом: {"title": 123, "body": False, "userId": "abc"} поймал статус 500, 
        # а через скрипт 201, это обусловлено тем, что Python requests автоматически сериализует False в false 
        # при использовании json=payload, и выполняет обратный процесс - десериализует JSON обратно в Python-объект, 
        # когда мы вызываем response.json().    
        # Конкретно наш API это не сломало, и он допускает булев тип данных, что мы увидим в следующем тесте.
          
        # Однако, я захотел воспроизвести сценарий из Postman. 
        # Изначально мой тест-кейс предполагал, что возможно API ломается на булевом значении (False),
        # но на самом деле он сломался из-за невалидного JSON-синтаксиса (False вместо false). 
        # Чтобы это воспроизвести, я создал "плохой" JSON вручную в виде строки, 
        # без автоматической конвертации и принудительно указал headers.

    @allure.story("Негативный тест: создание поста с невалидными данными")
    @pytest.mark.parametrize("payload, expected_response", [
        ({"title": 123, "body": False, "userId": "abc"}, {"title": 123, "body": False, "userId": "abc", "id": 101}), # Неверные типы
        ({"random_field": "unexpected"}, {"random_field": "unexpected", "id": 101}), # Поля, которых нет в API
        ({}, {"id": 101}), # Пустые данные
        (None, {"id": 101}) # Вообще без JSON
    ])
    def test_create_post_with_invalid_payload(self, payload, expected_response):  
        response = requests.post(BASE_URL, json=payload)
        assert response.status_code == 201, "Ошибка: ожидался статус 201"
        assert response.json() == expected_response, f"Ошибка: API вернул неожиданный ответ {response.json()}"

        # Данный тест(test_create_post_with_invalid_data) выстроен так, чтобы он проходил как PASSED, 
        # и чтобы подсветить ”особенности” работы конкретного API, а именно то, что пост создается почти всегда, 
        # даже с пустым или отсутствующим JSON, с полями, которых нет в API и с неверными типами данных. 
        # Во всех этих случаях мы получаем статус код 201, что вряд-ли можно считать нормальным поведением API.

if __name__ == "__main__":
    pytest.main(["-v", "--alluredir=./allure-results"])
