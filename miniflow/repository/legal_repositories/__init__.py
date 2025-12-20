"""
Legal Repositories - Yasal doküman işlemleri için repository'ler.
"""

from .agreement_repository import AgreementRepository
from .agreement_version_repository import AgreementVersionRepository
from .user_agreement_acceptance_repository import UserAgreementAcceptanceRepository

__all__ = [
    "AgreementRepository",
    "AgreementVersionRepository",
    "UserAgreementAcceptanceRepository",
]

