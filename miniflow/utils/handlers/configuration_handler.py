from pathlib import Path
from configparser import ConfigParser

from miniflow.core.exceptions import ResourceNotFoundError, InternalError


class ConfigurationHandler:
    """Configuration dosyalrını yöneten sınıf (singleton pattern)"""
    _initialized = False
    _config_path = None
    _config_parser = None

    @classmethod
    def load_config(cls, environment_name: str = "dev") -> None:
        """.ini dosyasını yükler"""
        if cls._initialized:
            return
        
        if cls._config_parser is None:
            cls._config_parser = ConfigParser()
        
        config_file_name = f"{environment_name.lower()}.ini"

        project_root = Path(__file__).resolve().parents[3]
        cls._config_path = project_root / config_file_name
        
        if not cls._config_path.exists():
            raise ResourceNotFoundError(f".ini dosyası bulunamadı: {cls._config_path}")
        
        cls._config_parser.read(cls._config_path)
        cls._initialized = True

    @classmethod
    def test_config(cls, section: str = "TEST", test_key: str = "TEST_KEY", test_value: str = "ThisIsATestValue") -> bool:
        """.ini dosyasını test etmek için kullanılır"""
        if not cls._initialized:
            cls.load_config()
        
        if not cls._config_parser.has_section(section):
            return False
        
        value = cls._config_parser.get(section, test_key, fallback=None)
        return (value == test_value if value else False)

    @classmethod
    def initialize(cls, environment_name: str = "dev", section: str = "TEST", test_key: str = "TEST_KEY", test_value: str = "ThisIsATestValue") -> bool:
        """.ini dosyasını yükler ve doğrular"""
        cls.load_config(environment_name)
        test_result = cls.test_config(section, test_key, test_value)
        if not test_result:
            raise InternalError(
                component_name="configuration_handler",
                message="Configuration validation test failed. Configuration file may be corrupted or missing required variables.",
                error_details={
                    "test_key": test_key,
                    "expected_value": test_value,
                    "actual_value": cls._config_parser.get(section, test_key, fallback=None) if cls._config_parser.has_section(section) else None,
                    "config_file_path": str(cls._config_path)
                }
            )
        return test_result
        
    @classmethod
    def get_value_as_str(cls, section: str, key: str, default = None) -> str:
        """.ini dosyasından configuration variable'ı alır"""
        if not cls._initialized:
            cls.load_config()
        return cls._config_parser.get(section, key, fallback=default)
        
    @classmethod
    def get_value_as_int(cls, section: str, key: str, default = None) -> int:
        """.ini dosyasından configuration variable'ı alır"""
        if not cls._initialized:
            cls.load_config()
        return cls._config_parser.getint(section, key, fallback=default)
        
    @classmethod
    def get_value_as_float(cls, section: str, key: str, default = None) -> float:
        """.ini dosyasından configuration variable'ı alır"""
        if not cls._initialized:
            cls.load_config()
        return cls._config_parser.getfloat(section, key, fallback=default)
        
    @classmethod
    def get_value_as_bool(cls, section: str, key: str, default = None) -> bool:
        """.ini dosyasından configuration variable'ı alır"""
        if not cls._initialized:
            cls.load_config()
        return cls._config_parser.getboolean(section, key, fallback=default)
        
    @classmethod
    def get_value_as_list(cls, section: str, key: str, default = None, separator = ',') -> list: 
        """.ini dosyasından configuration variable'ı alır"""
        if not cls._initialized:
            cls.load_config()

        value = cls._config_parser.get(section, key, fallback=default)
        if value is None:
            return default if default is not None else []
        return [item.strip() for item in value.strip().split(separator) if item.strip()]