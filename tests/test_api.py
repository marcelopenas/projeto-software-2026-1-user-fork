OK = 200
CREATED = 201
DELETED = 204
NOT_FOUND = 404


def test_get_user_404(client) -> None:

    # Teste de Recuperação
    get_response = client.get("/users/1")
    assert get_response.status_code == NOT_FOUND  # noqa: S101


def test_create_and_get_user_and_delete_user(client) -> None:
    new_client = {"name": "client", "email": "client@example.test"}
    post_response = client.post("/users", json=new_client)
    assert post_response.status_code == CREATED  # noqa: S101
    client_id = post_response.get_json()["id"]

    get_response = client.get(f"/users/{client_id}")
    assert get_response.status_code == OK  # noqa: S101

    delete_response = client.delete(f"/users/{client_id}")
    assert delete_response.status_code == DELETED  # noqa: S101


def test_create_and_delete_user(client) -> None:
    new_client = {"name": "client", "email": "client@example.test"}
    post_response = client.post("/users", json=new_client)
    assert post_response.status_code == CREATED  # noqa: S101
    client_id = post_response.get_json()["id"]

    delete_response = client.delete(f"/users/{client_id}")
    assert delete_response.status_code == DELETED  # noqa: S101


def test_create_two_users_and_list_and_delete_both_users(
    client,
) -> None:
    new_client_1 = {"name": "client_1", "email": "client_1@example.test"}
    post_response = client.post("/users", json=new_client_1)
    assert post_response.status_code == CREATED  # noqa: S101
    client_1_id = post_response.get_json()["id"]

    new_client_2 = {"name": "client_2", "email": "client_2@example.test"}
    post_response = client.post("/users", json=new_client_2)
    assert post_response.status_code == CREATED  # noqa: S101
    client_2_id = post_response.get_json()["id"]

    get_response = client.get("/users")
    assert get_response.status_code == OK  # noqa: S101
    assert isinstance(get_response.json, list)  # noqa: S101
    assert len(get_response.json) == 2  # noqa: PLR2004, S101

    delete_response = client.delete(f"/users/{client_1_id}")
    assert delete_response.status_code == DELETED  # noqa: S101
    delete_response = client.delete(f"/users/{client_2_id}")
    assert delete_response.status_code == DELETED  # noqa: S101
