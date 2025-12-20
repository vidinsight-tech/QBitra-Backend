"""
ScriptReviewHistory Repository - Script inceleme geçmişi için repository.

Kullanım:
    >>> from miniflow.repository import ScriptReviewHistoryRepository
    >>> review_repo = ScriptReviewHistoryRepository()
    >>> reviews = review_repo.get_all_by_script_id(session, "CSC-123")
"""

from __future__ import annotations

from typing import Optional, List

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from miniflow.database.repository.advanced import AdvancedRepository
from miniflow.models import ScriptReviewHistory
from miniflow.database.repository.base import handle_db_exceptions



class ScriptReviewHistoryRepository(AdvancedRepository):
    """Script inceleme geçmişi için repository."""
    
    def __init__(self):
        super().__init__(ScriptReviewHistory)
    
    # =========================================================================
    # LOOKUP METHODS
    # =========================================================================
    
    @handle_db_exceptions
    def get_all_by_script_id(
        self, 
        session: Session, 
        script_id: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[ScriptReviewHistory]:
        """Script'in tüm review geçmişini getirir (liste)."""
        return session.query(self.model).filter(
            self.model.script_id == script_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_all_by_reviewer_id(
        self, 
        session: Session, 
        reviewer_id: str,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[ScriptReviewHistory]:
        """Reviewer'ın tüm review'larını getirir (liste)."""
        return session.query(self.model).filter(
            self.model.reviewed_by == reviewer_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_latest_review(
        self, 
        session: Session, 
        script_id: str,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> Optional[ScriptReviewHistory]:
        """Script'in son review'ını getirir."""
        return session.query(self.model).filter(
            self.model.script_id == script_id,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).first()
    
    @handle_db_exceptions
    def get_all_by_status(
        self, 
        session: Session, 
        review_status,
        limit: int = 100, order_by: Optional[str] = "created_at", order_desc: bool = True
    ) -> List[ScriptReviewHistory]:
        """Review durumuna göre getirir (liste)."""
        return session.query(self.model).filter(
            self.model.review_status == review_status,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def count_by_script_id(self, session: Session, script_id: str) -> int:
        """Script'in review sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.script_id == script_id,
            self.model.is_deleted == False
        ).scalar()
    
    @handle_db_exceptions
    def count_by_reviewer_id(self, session: Session, reviewer_id: str) -> int:
        """Reviewer'ın review sayısını döndürür."""
        return session.query(func.count(self.model.id)).filter(
            self.model.reviewed_by == reviewer_id,
            self.model.is_deleted == False
        ).scalar()
    
    # =========================================================================
    # URGENT REVIEWS
    # =========================================================================
    
    @handle_db_exceptions
    def get_urgent_reviews(
        self, 
        session: Session,
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[ScriptReviewHistory]:
        """Acil review'ları getirir."""
        return session.query(self.model).filter(
            self.model.is_urgent == True,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    @handle_db_exceptions
    def get_pending_changes_reviews(
        self, 
        session: Session,
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[ScriptReviewHistory]:
        """Değişiklik bekleyen review'ları getirir."""
        return session.query(self.model).filter(
            self.model.requires_changes == True,
            self.model.is_deleted == False
        ).order_by(desc(getattr(self.model, order_by)) if order_desc else getattr(self.model, order_by)).limit(limit).all()
    
    # =========================================================================
    # REVIEW CHAIN
    # =========================================================================
    
    @handle_db_exceptions
    def get_review_chain(
        self, 
        session: Session, 
        review_id: str
    ) -> List[ScriptReviewHistory]:
        """Review zincirini getirir (en eskiden en yeniye)."""
        reviews = []
        current = self.get_by_id(session, review_id)
        
        # Öncekileri bul
        while current and current.previous_review_id:
            current = self.get_by_id(session, current.previous_review_id)
            if current:
                reviews.insert(0, current)
        
        # Kendisini ekle
        current = self.get_by_id(session, review_id)
        if current:
            reviews.append(current)
        
        # Sonrakileri bul
        next_reviews = session.query(self.model).filter(
            self.model.previous_review_id == review_id,
            self.model.is_deleted == False
        ).order_by(desc(self.model.created_at)).all()
        reviews.extend(next_reviews)
        
        return reviews

