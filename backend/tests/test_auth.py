from app.security import hash_password, verify_password

def test_password_hashing():
    password = "SuperSecurePassword2026!"
    hashed = hash_password(password)
    assert password != hashed
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False
