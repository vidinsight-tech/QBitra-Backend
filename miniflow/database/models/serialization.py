"""
Model Serializasyon Yardımcıları

Bu modül, SQLAlchemy modellerini dictionary ve JSON string'lerine
dönüştürmek için yardımcı fonksiyonlar sağlar. API yanıtları ve
veri serializasyonu için kullanışlıdır.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from enum import Enum
import json


def _serialize_value(value: Any) -> Any:
    """Tek bir değeri JSON-serializable formata dönüştürür.
    
    Args:
        value: Serialize edilecek değer
    
    Returns:
        JSON-serializable değer
    """
    if value is None:
        return None
    
    # Primitif tipler - en sık karşılaşılan
    if isinstance(value, (str, int, float, bool)):
        return value
    
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    
    if isinstance(value, Decimal):
        return float(value)
    
    if isinstance(value, UUID):
        return str(value)
    
    if isinstance(value, Enum):
        return value.value
    
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    
    if isinstance(value, (list, dict)):
        return value
    
    if isinstance(value, (set, frozenset)):
        return list(value)
    
    if hasattr(value, '__dict__'):
        return str(value)
    
    return value


def _json_serializer(obj: Any) -> Any:
    """json.dumps default parametresi için özel JSON serializer.
    
    Args:
        obj: Serialize edilecek nesne
    
    Returns:
        JSON-serializable değer
    
    Raises:
        TypeError: Nesne serialize edilemezse
    """
    result = _serialize_value(obj)
    
    if result is obj and not isinstance(obj, (str, int, float, bool, list, dict, type(None))):
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    return result


def model_to_dict(
    instance: Any,
    exclude: Optional[List[str]] = None,
    include_relationships: bool = False,
    max_depth: int = 1,
    _exclude_set: Optional[set] = None,
    _visited: Optional[set] = None
) -> Dict[str, Any]:
    """SQLAlchemy model instance'ını dictionary'ye dönüştürür.
    
    SQLAlchemy model instance'ını Python dictionary'sine dönüştürür.
    datetime, date, Decimal, UUID, Enum ve relationship'ler gibi
    yaygın veri tiplerini işler.
    
    Args:
        instance: SQLAlchemy model instance'ı
        exclude: Çıktıdan hariç tutulacak alan adları listesi
        include_relationships: True ise, relationship verilerini dahil et (varsayılan: False)
        max_depth: Relationship serializasyonu için maksimum derinlik (varsayılan: 1)
        _exclude_set: Optimizasyon için internal parametre (doğrudan kullanmayın)
        _visited: Circular reference koruması için internal parametre (doğrudan kullanmayın)
    
    Returns:
        Dict[str, Any]: Model'in dictionary temsili
    
    Raises:
        ValueError: Instance None ise
    
    Örnekler:
        >>> from miniflow.database.models.serialization import model_to_dict
        >>> 
        >>> user = User(id=1, email="test@example.com", name="Test User")
        >>> user_dict = model_to_dict(user)
        >>> # {'id': 1, 'email': 'test@example.com', 'name': 'Test User'}
        
        >>> # Hassas alanları hariç tut
        >>> user_dict = model_to_dict(user, exclude=['password', 'api_key'])
        
        >>> # Relationship'leri dahil et
        >>> user_dict = model_to_dict(user, include_relationships=True)
        >>> # 'posts', 'comments' vb. relationship'ler varsa dahil edilir
    
    Not:
        - datetime, date, Decimal, UUID, Enum ve diğer yaygın tipleri işler
        - Relationship'ler include_relationships=True ise dictionary olarak serialize edilir
        - Circular reference'lar max_depth ve _visited set ile önlenir
        - SQLAlchemy internal attribute'larını (_ ile başlayan) hariç tutar
        - Time Complexity: O(C + R*L*D) - C=kolon sayısı, R=relationship sayısı, L=relationship item sayısı (ortalama), D=max_depth
        - Space Complexity: O(C + R*L*D) - recursive call stack ve result dictionary
    """
    if instance is None:
        raise ValueError("Instance cannot be None")
    
    # Circular reference koruması
    if _visited is None:
        _visited = set()
    
    # Instance ID'si ile circular reference kontrolü
    instance_id = id(instance)
    if instance_id in _visited:
        # Circular reference tespit edildi, None döndür
        return None
    
    _visited.add(instance_id)
    
    try:
        # exclude_set optimizasyonu - sadece bir kez oluştur
        if _exclude_set is None:
            _exclude_set = set(exclude or [])
            _exclude_set.add('_sa_instance_state')
        
        result = {}
        
        table = getattr(instance, '__table__', None)
        if table is not None:
            for column in table.columns:
                column_name = column.name
                
                if column_name in _exclude_set or column_name.startswith('_'):
                    continue
                
                value = getattr(instance, column_name, None)
                result[column_name] = _serialize_value(value)
        
        if include_relationships:
            mapper = getattr(instance, '__mapper__', None)
            if mapper is not None:
                for relationship in mapper.relationships:
                    rel_name = relationship.key
                    
                    if rel_name in _exclude_set:
                        continue
                    
                    rel_value = getattr(instance, rel_name, None)
                    
                    if rel_value is None:
                        result[rel_name] = None
                    elif isinstance(rel_value, list):
                        if max_depth > 0:
                            result[rel_name] = [
                                model_to_dict(
                                    item,
                                    include_relationships=False,
                                    max_depth=max_depth - 1,
                                    _exclude_set=_exclude_set,
                                    _visited=_visited
                                )
                                for item in rel_value
                            ]
                        else:
                            result[rel_name] = []
                    else:
                        if max_depth > 0:
                            result[rel_name] = model_to_dict(
                                rel_value,
                                include_relationships=False,
                                max_depth=max_depth - 1,
                                _exclude_set=_exclude_set,
                                _visited=_visited
                            )
                        else:
                            result[rel_name] = None
        
        return result
    finally:
        # Circular reference koruması için visited'den çıkar
        _visited.discard(instance_id)


def models_to_list(
    instances: Optional[List[Any]],
    exclude: Optional[List[str]] = None,
    include_relationships: bool = False
) -> List[Dict[str, Any]]:
    """SQLAlchemy model instance'ları listesini dictionary listesine dönüştürür.
    
    Birden fazla model instance'ını serialize etmek için kolaylık fonksiyonu.
    
    Args:
        instances: SQLAlchemy model instance'ları listesi
        exclude: Çıktıdan hariç tutulacak alan adları listesi
        include_relationships: True ise, relationship verilerini dahil et (varsayılan: False)
    
    Returns:
        List[Dict[str, Any]]: Dictionary temsilleri listesi
    
    Örnekler:
        >>> from miniflow.database.models.serialization import models_to_list
        >>> 
        >>> users = [User(id=1, email="user1@example.com"), User(id=2, email="user2@example.com")]
        >>> users_list = models_to_list(users)
        >>> # [{'id': 1, 'email': 'user1@example.com'}, {'id': 2, 'email': 'user2@example.com'}]
        
        >>> # Alanları hariç tut
        >>> users_list = models_to_list(users, exclude=['password'])
        
        >>> # Boş liste işleme
        >>> empty_list = models_to_list([])
        >>> # []
    
    Not:
        - Time Complexity: O(N*(C + R*L*D)) - N=instance sayısı, C=kolon sayısı, R=relationship sayısı, L=relationship item sayısı (ortalama), D=max_depth
        - Relationship'ler dahil değilse: O(N*C)
        - exclude_set bir kez oluşturulur ve tüm instance'lar için paylaşılır (optimizasyon)
        - Space Complexity: O(N*(C + R*L*D)) - result listesi
    """
    if not instances:
        return []
    
    # exclude_set'i bir kez oluştur ve tüm instance'lar için paylaş (O(E) - E=exclude uzunluğu)
    exclude_set = set(exclude or [])
    exclude_set.add('_sa_instance_state')
    
    # Circular reference koruması için shared visited set
    visited = set()
    
    return [
        model_to_dict(
            instance,
            include_relationships=include_relationships,
            _exclude_set=exclude_set,
            _visited=visited
        )
        for instance in instances
    ]


def model_to_json(
    instance: Any,
    exclude: Optional[List[str]] = None,
    include_relationships: bool = False,
    indent: Optional[int] = None,
    ensure_ascii: bool = False
) -> str:
    """SQLAlchemy model instance'ını JSON string'ine dönüştürür.
    
    SQLAlchemy model instance'ını JSON string'ine dönüştürür.
    datetime, date, Decimal, UUID ve Enum gibi yaygın veri tiplerini işler.
    
    Args:
        instance: SQLAlchemy model instance'ı
        exclude: Çıktıdan hariç tutulacak alan adları listesi
        include_relationships: True ise, relationship verilerini dahil et (varsayılan: False)
        indent: JSON girinti seviyesi (None: kompakt, 2: pretty print)
        ensure_ascii: True ise, ASCII olmayan karakterleri escape eder (varsayılan: False)
    
    Returns:
        str: Model'in JSON string temsili
    
    Örnekler:
        >>> from miniflow.database.models.serialization import model_to_json
        >>> 
        >>> user = User(id=1, email="test@example.com", name="Test User")
        >>> json_str = model_to_json(user)
        >>> # '{"id": 1, "email": "test@example.com", "name": "Test User"}'
        
        >>> # Pretty print
        >>> json_str = model_to_json(user, indent=2)
        
        >>> # Hassas alanları hariç tut
        >>> json_str = model_to_json(user, exclude=['password'])
    
    Not:
        - datetime, date, Decimal, UUID, Enum serializasyonunu işler
        - Standart olmayan tipler için özel JSON encoder kullanır
        - API yanıtları için uygundur
        - Time Complexity: O(C + R*L*D + M) - C=kolon sayısı, R=relationship sayısı, L=relationship item sayısı (ortalama), D=max_depth, M=dict size (json.dumps)
        - Space Complexity: O(C + R*L*D + M) - dict ve JSON string
    """
    # exclude_set'i model_to_dict'e bırak (gereksiz tekrarı önle)
    data = model_to_dict(
        instance,
        exclude=exclude,
        include_relationships=include_relationships
    )
    
    return json.dumps(
        data,
        indent=indent,
        ensure_ascii=ensure_ascii,
        default=_json_serializer
    )