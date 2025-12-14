"""Legal models package"""

from miniflow.models.legal_models.agreements import Agreement
from miniflow.models.legal_models.agreement_versions import AgreementVersion
from miniflow.models.legal_models.user_agreement_acceptances import UserAgreementAcceptance

__all__ = [
    "Agreement",
    "AgreementVersion",
    "UserAgreementAcceptance",
]
