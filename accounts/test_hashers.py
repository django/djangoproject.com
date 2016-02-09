from django.test import SimpleTestCase

from .hashers import PBKDF2WrappedSHA1PasswordHasher


class TestHasher(SimpleTestCase):
    def test(self):
        iterations = 10  # low value for testing
        password = 'a'
        sha1_encoded = 'sha1$YoBzLZeL3w2R$757b56ad30c5fac1b552f58ad3acfddb07b674e2'
        expected_pbkdf2_encoded = 'pbkdf2_wrapped_sha1$10$YoBzLZeL3w2R$djfB2Y51/PwFdzcMoIlwUXglb2wMBz2L+LZ8Hjs2wnk='
        _, salt, sha1_hash = sha1_encoded.split('$', 3)
        hasher = PBKDF2WrappedSHA1PasswordHasher()
        pbkdf2_hash = hasher.encode_sha1_hash(sha1_hash, salt, iterations)
        self.assertEqual(pbkdf2_hash, expected_pbkdf2_encoded)
        self.assertEqual(hasher.encode(password, salt, iterations), expected_pbkdf2_encoded)
