"""Tests for hashing and JWT tokens"""

from app.core.security import Argon2PasswordHasher, JWTAuthToken

# test key for jwt session
TEST_KEY = "g0G.n838(Y.4PJeZDf'ZOW%wV%B9FxlC"

# secret word assign to all passwords before hashing
TEST_PEPPER = "7;SF`CFCFC^j/{sxW5PL$w8;"


# Argon2PasswordHasher

def test_argon2_hash_and_verify():
    """A correct password verifies; a wrong one doesn't."""
    h = Argon2PasswordHasher(pepper=TEST_PEPPER)
    hashed = h.hash("qwerty")
    assert h.verify("qwerty", hashed) is True
    assert h.verify("QWERTY", hashed) is False


def test_argon2_different_hashes():
    """Check if same password have different hashes as 'salt' must be different"""
    h = Argon2PasswordHasher(pepper=TEST_PEPPER)
    assert h.hash("qwerty") != h.hash("qwerty")


# JWTAuthToken

def test_jwt_create_and_decode():
    """User id must much the token"""
    t = JWTAuthToken(secret_key=TEST_KEY)
    token = t.create_token(user_id=42)
    assert t.decode_token(token) == 42


def test_jwt_rejects_wrong_secret():
    """A token signed with one key cannot be decoded with a different key"""
    issuer = JWTAuthToken(secret_key=TEST_KEY)
    another_key = JWTAuthToken(secret_key="y" * 32)
    token = issuer.create_token(user_id=42)
    assert another_key.decode_token(token) is None