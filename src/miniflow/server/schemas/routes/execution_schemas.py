"""
Execution request schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class StartExecutionRequest(BaseModel):
    """Request schema for starting an execution from workflow."""
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data for the execution (will be passed as trigger_data)",
        default_factory=dict
    )

