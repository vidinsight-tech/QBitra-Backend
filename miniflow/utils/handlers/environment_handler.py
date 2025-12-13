import os
from pathlib import Path
from dotenv import load_dotenv
from miniflow.core.exceptions import ResourceNotFoundError, InternalError


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
            raise ResourceNotFoundError(f".env dosyası bulunamadı: {cls._env_path}")
        
        load_dotenv(cls._env_path)
        cls._initialized = True

    @classmethod
    def test_env(cls, test_key: str = "TEST_KEY", test_value: str = "ThisIsATestValue") -> None:
        """.env dosyasını test etmek için kullanılır"""
        if not cls._initialized:
            cls.load_env()
        
        value = os.getenv(test_key)
        return (value == test_value if value else False)

    @classmethod
    def initilize(cls, test_key: str = "TEST_KEY", test_value: str = "ThisIsATestValue") -> bool:
        """.env dosyasının yolunu alır"""
        cls.load_env()
        test_result = cls.test_env(test_key, test_value)
        if not test_result:
            raise InternalError(
                component_name="environment_handler",
                message="Environment validation test failed. Environment file may be corrupted or missing required variables.",
                error_details={
                    "test_key": "TEST_KEY",
                    "expected_value": "ThisKeyIsForConfigTest",
                    "actual_value": test_value,
                    "env_file_path": str(cls._env_path)
                }
            )
        return test_result

    @classmethod
    def get_env(cls, key: str, default = None) -> str:
        """.env dosyasından environment variable'ı alır"""
        if not cls._initialized:
            cls.load_env()

        return os.getenv(key, default)