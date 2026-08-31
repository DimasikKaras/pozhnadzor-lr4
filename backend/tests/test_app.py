from app.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    password = "SuperPassword2026!"
    hashed = hash_password(password)
    assert password != hashed
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_generation():
    user_id = 42
    token = create_access_token(str(user_id))
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload.get("sub") == "42"
    assert payload.get("type") == "access"
