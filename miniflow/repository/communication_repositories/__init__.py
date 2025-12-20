"""Communication Repositories - İletişim modelleri için repository'ler."""

from .email_repository import EmailRepository
from .email_attachment_repository import EmailAttachmentRepository
from .notification_repository import NotificationRepository
from .ticket_repository import TicketRepository
from .ticket_message_repository import TicketMessageRepository
from .ticket_attachment_repository import TicketAttachmentRepository

__all__ = [
    "EmailRepository",
    "EmailAttachmentRepository",
    "NotificationRepository",
    "TicketRepository",
    "TicketMessageRepository",
    "TicketAttachmentRepository",
]

