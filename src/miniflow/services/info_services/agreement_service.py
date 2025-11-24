from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from src.miniflow.database import RepositoryRegistry, with_transaction, with_readonly_session
from src.miniflow.database.utils.pagination_params import PaginationParams
from src.miniflow.core.exceptions import (
    ResourceNotFoundError,
    ResourceAlreadyExistsError,
    InvalidInputError,
)
from src.miniflow.utils.helpers.encryption_helper import hash_data


class AgreementService:
    """Agreement versiyonlarını yönetir"""

    def __init__(self):
        self._registry = RepositoryRegistry()
        self._agreement_version_repo = self._registry.agreement_version_repository

    def _calculate_next_version(self, current_version: str) -> str:
        """Calculate next version number (e.g., 1.0 -> 1.1, 1.9 -> 2.0)"""
        try:
            parts = current_version.split('.')
            if len(parts) == 2:
                major, minor = int(parts[0]), int(parts[1])
                if minor < 9:
                    return f"{major}.{minor + 1}"
                else:
                    return f"{major + 1}.0"
            elif len(parts) == 1:
                # If single number, treat as major version
                major = int(parts[0])
                return f"{major + 1}.0"
            else:
                # If format is unexpected, increment last part
                last_part = int(parts[-1])
                parts[-1] = str(last_part + 1)
                return '.'.join(parts)
        except (ValueError, IndexError):
            # If version format is invalid, default to 1.0
            return "1.0"

    @with_transaction(manager=None)
    def create_agreement(
        self,
        session,
        *,
        agreement_type: str,
        content: str,
        effective_date: datetime,
        locale: str = "tr-TR",
        is_active: bool = False,
        notes: Optional[str] = None,
        created_by: str,
    ) -> Dict[str, Any]:
        # Validate inputs
        if not agreement_type or not agreement_type.strip():
            raise InvalidInputError(field_name="agreement_type", message="Agreement type cannot be empty")
        if not content or not content.strip():
            raise InvalidInputError(field_name="content", message="Content cannot be empty")
        
        # Get latest version to calculate next version
        latest = self._agreement_version_repo._get_latest(
            session, agreement_type=agreement_type, locale=locale, include_deleted=False
        )
        
        if latest:
            version = self._calculate_next_version(latest.version)
        else:
            version = "1.0"
        
        # Check if version already exists
        existing = self._agreement_version_repo._get_by_type_and_version(
            session, agreement_type=agreement_type, version=version, locale=locale, include_deleted=False
        )
        if existing:
            raise ResourceAlreadyExistsError(
                resource_name="agreement_version",
                conflicting_field="version",
                message=f"Agreement version {version} already exists for type {agreement_type} and locale {locale}"
            )
        
        # Generate content hash
        content_hash = hash_data(content)
        
        # If setting as active, deactivate other versions of same type and locale
        if is_active:
            all_versions = self._agreement_version_repo._get_all_by_type(
                session, agreement_type=agreement_type, locale=locale, include_deleted=False
            )
            for version_obj in all_versions:
                if version_obj.is_active:
                    version_obj.is_active = False
        
        # Create new agreement version
        agreement = self._agreement_version_repo._create(
            session,
            agreement_type=agreement_type,
            version=version,
            content=content,
            content_hash=content_hash,
            effective_date=effective_date,
            is_active=is_active,
            locale=locale,
            notes=notes,
            created_by=created_by,
        )
        
        return {
            "id": agreement.id,
        }

    @with_readonly_session(manager=None)
    def get_agreement(
        self,
        session,
        *,
        agreement_id: str,
    ) -> Dict[str, Any]:
        agreement = self._agreement_version_repo._get_by_id(session, record_id=agreement_id, include_deleted=False)
        if not agreement:
            raise ResourceNotFoundError(resource_name="agreement_version", resource_id=agreement_id)
        
        return agreement.to_dict()

    @with_readonly_session(manager=None)
    def get_agreement_by_type_and_version(
        self,
        session,
        *,
        agreement_type: str,
        version: str,
        locale: str = "tr-TR",
    ) -> Dict[str, Any]:
        agreement = self._agreement_version_repo._get_by_type_and_version(
            session, agreement_type=agreement_type, version=version, locale=locale, include_deleted=False
        )
        if not agreement:
            raise ResourceNotFoundError(
                resource_name="agreement_version",
                message=f"Agreement version {version} not found for type {agreement_type} and locale {locale}"
            )
        
        return agreement.to_dict()

    @with_transaction(manager=None)
    def update_agreement(
        self,
        session,
        *,
        agreement_id: str,
        content: Optional[str] = None,
        effective_date: Optional[datetime] = None,
        is_active: Optional[bool] = None,
        notes: Optional[str] = None,
        updated_by: str,
    ) -> Dict[str, Any]:
        """
        Update agreement by creating a new version (versioning strategy).
        This ensures all historical versions are preserved.
        """
        existing_agreement = self._agreement_version_repo._get_by_id(session, record_id=agreement_id, include_deleted=False)
        if not existing_agreement:
            raise ResourceNotFoundError(resource_name="agreement_version", resource_id=agreement_id)
        
        # Calculate next version
        new_version = self._calculate_next_version(existing_agreement.version)
        
        # Check if new version already exists
        existing_new_version = self._agreement_version_repo._get_by_type_and_version(
            session,
            agreement_type=existing_agreement.agreement_type,
            version=new_version,
            locale=existing_agreement.locale,
            include_deleted=False
        )
        if existing_new_version:
            raise ResourceAlreadyExistsError(
                resource_name="agreement_version",
                conflicting_field="version",
                message=f"Agreement version {new_version} already exists"
            )
        
        # Use provided content or existing content
        new_content = content if content is not None else existing_agreement.content
        new_content_hash = hash_data(new_content)
        
        # Use provided effective_date or current time
        new_effective_date = effective_date if effective_date is not None else datetime.now(timezone.utc)
        
        # Use provided is_active or keep existing
        new_is_active = is_active if is_active is not None else existing_agreement.is_active
        
        # If setting as active, deactivate other versions
        if new_is_active:
            all_versions = self._agreement_version_repo._get_all_by_type(
                session,
                agreement_type=existing_agreement.agreement_type,
                locale=existing_agreement.locale,
                include_deleted=False
            )
            for version_obj in all_versions:
                if version_obj.is_active and version_obj.id != agreement_id:
                    version_obj.is_active = False
        
        # Create new version
        new_agreement = self._agreement_version_repo._create(
            session,
            agreement_type=existing_agreement.agreement_type,
            version=new_version,
            content=new_content,
            content_hash=new_content_hash,
            effective_date=new_effective_date,
            is_active=new_is_active,
            locale=existing_agreement.locale,
            notes=notes,
            created_by=updated_by,
        )
        
        return {
            "id": new_agreement.id,
            "version": new_version,
        }

    @with_transaction(manager=None)
    def delete_agreement(
        self,
        session,
        *,
        agreement_id: str,
    ):
        agreement = self._agreement_version_repo._get_by_id(session, record_id=agreement_id, include_deleted=False)
        if not agreement:
            raise ResourceNotFoundError(resource_name="agreement_version", resource_id=agreement_id)
        
        # Check if agreement has acceptances (RESTRICT constraint)
        if agreement.acceptances and len(agreement.acceptances) > 0:
            raise InvalidInputError(
                field_name="agreement_id",
                message="Cannot delete agreement version that has user acceptances. Versions with acceptances cannot be deleted."
            )
        
        self._agreement_version_repo._delete(session, record_id=agreement_id)
        
        return {
            "deleted": True,
            "agreement_id": agreement_id
        }

    @with_readonly_session(manager=None)
    def get_all_agreements_with_pagination(
        self,
        session,
        *,
        agreement_type: Optional[str] = None,
        locale: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = True,  # Default: newest first
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        pagination_params = PaginationParams(
            page=page,
            page_size=page_size,
            order_by=order_by or "effective_date",
            order_desc=order_desc,
            include_deleted=include_deleted
        )
        pagination_params.validate()
        
        # Apply filters if provided
        filter_params = None
        if agreement_type or locale:
            from src.miniflow.database.utils.filter_params import FilterParams
            filters = {}
            if agreement_type:
                filters["agreement_type"] = agreement_type
            if locale:
                filters["locale"] = locale
            filter_params = FilterParams(**filters)
        
        result = self._agreement_version_repo._paginate(
            session,
            pagination_params=pagination_params,
            filter_params=filter_params
        )
        
        items = [agreement.to_dict() for agreement in result.items]
        
        return {
            "items": items,
            "metadata": result.metadata.to_dict()
        }

    @with_readonly_session(manager=None)
    def get_latest_agreement(
        self,
        session,
        *,
        agreement_type: str,
        locale: str = "tr-TR",
    ) -> Dict[str, Any]:
        """Get latest agreement version by effective_date"""
        agreement = self._agreement_version_repo._get_latest(
            session, agreement_type=agreement_type, locale=locale, include_deleted=False
        )
        if not agreement:
            raise ResourceNotFoundError(
                resource_name="agreement_version",
                message=f"No agreement found for type {agreement_type} and locale {locale}"
            )
        
        return agreement.to_dict()

    @with_readonly_session(manager=None)
    def get_active_agreement(
        self,
        session,
        *,
        agreement_type: str,
        locale: str = "tr-TR",
    ) -> Dict[str, Any]:
        """Get active agreement version"""
        agreement = self._agreement_version_repo._get_active(
            session, agreement_type=agreement_type, locale=locale, include_deleted=False
        )
        if not agreement:
            raise ResourceNotFoundError(
                resource_name="agreement_version",
                message=f"No active agreement found for type {agreement_type} and locale {locale}"
            )
        
        return agreement.to_dict()

    @with_transaction(manager=None)
    def seed_agreement(self, session, *, agreements_data: List[Dict]):
        """Seed agreements (legacy method for backward compatibility)"""
        stats = {"created": 0, "skipped": 0, "updated": 0}

        for agreement_data in agreements_data:
            agreement_type = agreement_data.get("agreement_type")
            version = agreement_data.get("version")
            locale = agreement_data.get("locale", "tr-TR")

            if not agreement_type or not version:
                continue

            existing_agreement = self._agreement_version_repo._get_by_type_and_version(
                session,
                agreement_type=agreement_type,
                version=version,
                locale=locale
            )

            if existing_agreement:
                stats["skipped"] += 1
            else:
                self._agreement_version_repo._create(session, **agreement_data)
                stats["created"] += 1

        return stats