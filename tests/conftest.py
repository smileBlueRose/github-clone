from pathlib import Path
from uuid import uuid4

import pytest

from domain.entities.user import User


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_secrets_dir(project_root: Path) -> Path:
    return project_root / "tests" / "secrets"


@pytest.fixture(scope="session")
def private_key(test_secrets_dir: Path) -> str:
    private: str = (test_secrets_dir / "test-private.pem").read_text()
    return private


@pytest.fixture(scope="session")
def another_private_key(test_secrets_dir: Path) -> str:
    private: str = (test_secrets_dir / "another-private.pem").read_text()
    return private


@pytest.fixture(scope="session")
def public_key(test_secrets_dir: Path) -> str:
    public: str = (test_secrets_dir / "test-public.pem").read_text()
    return public


@pytest.fixture(scope="session")
def another_public_key(test_secrets_dir: Path) -> str:
    private: str = (test_secrets_dir / "another-public.pem").read_text()
    return private


@pytest.fixture
def user() -> User:
    return User(
        id=uuid4(),
        email="test@example.com",
        username="scarlet-scarf",
        hashed_password="$2b$12$6rEUV1t6EHbC.HnelrKE9OntR1MUITbOJqteguORQ0un0CIRu/EzS",  # Password1234!
    )
