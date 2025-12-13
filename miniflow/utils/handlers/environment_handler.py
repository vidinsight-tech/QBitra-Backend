import os
from pathlib import Path
from dotenv import load_dotenv
from miniflow.core.exceptions import (
    ResourceNotFoundError,
    InternalServiceValidationError
)


class EnvironmentHandler:
    """.env dosyasını yöneten sınıf (singleton pattern)"""
    _initialized = False
    _env_path = None

    @classmethod
    def load_env(cls, env_file_name: str = '.env') -> None:
        """.env dosyasını yükler"""
        if cls._initialized:
            return
        
        project_root = Path(__file__).resolve().parents[3]
        cls._env_path = project_root / env_file_name

        if not cls._env_path.exists():
            raise ResourceNotFoundError(
                resource_type="environment_file",
                resource_path=str(cls._env_path),
                service_name="environment_handler"
            )
        
        load_dotenv(cls._env_path)
        cls._initialized = True

    @classmethod
    def test_env(cls, test_key: str = "TEST_KEY", test_value: str = "ThisIsATestValue") -> bool:
        """.env dosyasını test etmek için kullanılır"""
        if not cls._initialized:
            cls.load_env()
        
        value = os.getenv(test_key)
        return (value == test_value if value else False)

    @classmethod
    def initialize(cls, test_key: str = "TEST_KEY", test_value: str = "ThisIsATestValue") -> bool:
        """.env dosyasını yükler ve doğrular"""
        cls.load_env()
        test_result = cls.test_env(test_key, test_value)
        if not test_result:
            actual_value = os.getenv(test_key)
            raise InternalServiceValidationError(
                service_name="environment_handler",
                validation_field=test_key,
                expected_value=test_value,
                actual_value=actual_value,
                message=f"Environment validation test failed for '{test_key}'. Environment file may be corrupted or missing required variables."
            )
        return test_result

    @classmethod
    def get_env(cls, key: str, default = None) -> str:
        """.env dosyasından environment variable'ı alır"""
        if not cls._initialized:
            cls.load_env()

        return os.getenv(key, default)