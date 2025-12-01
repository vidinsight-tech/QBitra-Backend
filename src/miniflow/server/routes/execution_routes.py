"""
Execution management routes.

Handles execution creation, retrieval, and management for workspaces.
"""
from fastapi import APIRouter, Depends, Request, status, Path, Query
from typing import Dict, Any, Optional

from src.miniflow.server.dependencies import get_execution_service
from src.miniflow.services.execution_services.execution_service import ExecutionService
from src.miniflow.server.helpers import (
    validate_workspace_member,
    authenticate_user,
    AuthUser,
)
from src.miniflow.server.schemas.base_schema import create_success_response
from src.miniflow.server.schemas.routes.execution_schemas import (
    StartExecutionRequest,
)

router = APIRouter(prefix="/workspaces", tags=["executions"])


# ============================================================================
# START EXECUTION (UI-Triggered)
# ============================================================================

@router.post(
    "/{workspace_id}/workflows/{workflow_id}/executions",
    summary="Start execution from workflow",
    description="Start a new execution for a workflow (UI-triggered, no trigger required)",
    status_code=status.HTTP_201_CREATED,
)
async def start_execution(
    request: Request,
    workspace_id: str = Depends(validate_workspace_member),
    workflow_id: str = Path(..., description="Workflow ID"),
    body: StartExecutionRequest = ...,
    current_user: AuthUser = Depends(authenticate_user),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Start a new execution for a workflow from the UI.
    
    - **workspace_id**: Workspace ID (path parameter)
    - **workflow_id**: Workflow ID (path parameter)
    - **input_data**: Input data for the execution (request body, required)
        - This data will be passed as trigger_data to the execution
        - Can be any JSON object
    
    Requires workspace membership.
    Returns execution details including execution ID and execution inputs.
    """
    result = execution_service.start_execution_from_workflow(
        workspace_id=workspace_id,
        workflow_id=workflow_id,
        input_data=body.input_data,
        triggered_by=current_user["user_id"],
    )
    
    return create_success_response(
        request=request,
        data=result,
        message="Execution started successfully",
        code=status.HTTP_201_CREATED,
    ).model_dump()


# ============================================================================
# GET EXECUTION BY ID
# ============================================================================

@router.get(
    "/{workspace_id}/executions/{execution_id}",
    summary="Get execution by ID",
    description="Get detailed information about a specific execution",
    status_code=status.HTTP_200_OK,
)
async def get_execution(
    request: Request,
    workspace_id: str = Depends(validate_workspace_member),
    execution_id: str = Path(..., description="Execution ID"),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Get detailed information about a specific execution.
    
    - **workspace_id**: Workspace ID (path parameter)
    - **execution_id**: Execution ID (path parameter)
    
    Requires workspace membership.
    Returns execution details including status, timing, results, and trigger data.
    """
    result = execution_service.get_execution_by_id(execution_id=execution_id)
    
    # Verify execution belongs to workspace
    if result.get("workspace_id") != workspace_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    return create_success_response(
        request=request,
        data=result,
        message="Execution retrieved successfully",
        code=status.HTTP_200_OK,
    ).model_dump()


# ============================================================================
# GET ALL EXECUTIONS (Paginated)
# ============================================================================

@router.get(
    "/{workspace_id}/executions",
    summary="Get all executions",
    description="Get all executions for a workspace with pagination",
    status_code=status.HTTP_200_OK,
)
async def get_all_executions(
    request: Request,
    workspace_id: str = Depends(validate_workspace_member),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(100, ge=1, le=1000, description="Number of items per page (1-1000)"),
    order_by: Optional[str] = Query(None, description="Field to order by (default: created_at)"),
    order_desc: bool = Query(True, description="Order descending (default: True)"),
    include_deleted: bool = Query(False, description="Include deleted executions"),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Get all executions for a workspace with pagination.
    
    - **workspace_id**: Workspace ID (path parameter)
    - **page**: Page number (query parameter, default: 1, min: 1)
    - **page_size**: Number of items per page (query parameter, default: 100, min: 1, max: 1000)
    - **order_by**: Field to order by (query parameter, optional, default: created_at)
    - **order_desc**: Order descending (query parameter, default: True)
    - **include_deleted**: Include deleted executions (query parameter, default: False)
    
    Requires workspace membership.
    Returns paginated list of executions.
    """
    result = execution_service.get_all_executions(
        workspace_id=workspace_id,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_desc=order_desc,
        include_deleted=include_deleted,
    )
    
    return create_success_response(
        request=request,
        data=result,
        message="Executions retrieved successfully",
        code=status.HTTP_200_OK,
    ).model_dump()


# ============================================================================
# GET LAST EXECUTIONS
# ============================================================================

@router.get(
    "/{workspace_id}/executions/last",
    summary="Get last executions",
    description="Get the last N executions for a workspace (default: 5)",
    status_code=status.HTTP_200_OK,
)
async def get_last_executions(
    request: Request,
    workspace_id: str = Depends(validate_workspace_member),
    limit: int = Query(5, ge=1, le=100, description="Number of executions to retrieve (1-100, default: 5)"),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> Dict[str, Any]:
    """
    Get the last N executions for a workspace.
    
    - **workspace_id**: Workspace ID (path parameter)
    - **limit**: Number of executions to retrieve (query parameter, default: 5, min: 1, max: 100)
    
    Requires workspace membership.
    Returns the most recent executions ordered by creation date (descending).
    """
    result = execution_service.get_last_executions(
        workspace_id=workspace_id,
        limit=limit,
    )
    
    return create_success_response(
        request=request,
        data=result,
        message="Last executions retrieved successfully",
        code=status.HTTP_200_OK,
    ).model_dump()

