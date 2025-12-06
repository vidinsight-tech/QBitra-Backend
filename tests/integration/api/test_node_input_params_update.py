"""Test node input params update functionality."""

import pytest
import time
from miniflow.services._8_workflow_services import NodeService
from miniflow.services._7_script_services import GlobalScriptService
from miniflow.services._8_workflow_services import WorkflowManagementService
from miniflow.services._5_workspace_services import WorkspaceManagementService


class TestNodeInputParamsUpdate:
    """Test node input params update functionality."""
    
    def test_update_node_input_params_preserves_structure(self, test_db_setup):
        """
        Test that updating node input params preserves existing structure.
        
        Senaryo:
        1. Script oluştur (input_schema ile)
        2. Workspace ve Workflow oluştur
        3. Node oluştur (input_params ile)
        4. Node'un input_params'ini güncelle (sadece bir parametrenin value'sunu)
        5. Diğer parametrelerin bilgilerinin korunduğunu doğrula
        """
        session = test_db_setup
        
        # 0. Test user oluştur
        from miniflow.database import RepositoryRegistry
        registry = RepositoryRegistry()
        user_repo = registry.user_repository()
        
        test_user = user_repo._create(
            session,
            username="test_user",
            email="test@example.com",
            password_hash="dummy_hash",
            name="Test",
            surname="User",
            is_verified=True
        )
        test_user_id = test_user.id
        
        # 1. Script oluştur
        script_data = {
            "name": f"Test Script {time.time()}",
            "description": "Test script for input params",
            "content": "def main(params): return params",
            "input_schema": {
                "param1": {
                    "type": "string",
                    "required": True,
                    "description": "First parameter",
                    "default": "default1"
                },
                "param2": {
                    "type": "number",
                    "required": False,
                    "description": "Second parameter",
                    "default": 100
                },
                "param3": {
                    "type": "boolean",
                    "required": False,
                    "description": "Third parameter",
                    "default": False
                }
            },
            "output_schema": {},
            "category": "test"
        }
        
        script_result = GlobalScriptService.create_script(**script_data)
        script_id = script_result["id"]
        # Global script'ler otomatik onaylı olarak oluşturulur
        
        # 2. Workspace oluştur
        workspace_result = WorkspaceManagementService.create_workspace(
            name="Test Workspace",
            slug=f"test-workspace-update-{time.time()}",
            description="Test workspace",
            owner_id=test_user_id
        )
        workspace_id = workspace_result["id"]
        
        # 3. Workflow oluştur
        workflow_result = WorkflowManagementService.create_workflow(
            workspace_id=workspace_id,
            name="Test Workflow",
            description="Test workflow",
            created_by="test_user"
        )
        workflow_id = workflow_result["id"]
        
        # 4. Node oluştur (initial input_params ile)
        initial_input_params = {
            "param1": {
                "type": "string",
                "value": "initial_value_1",
                "default_value": "default1",
                "required": True,
                "description": "First parameter"
            },
            "param2": {
                "type": "number",
                "value": 200,
                "default_value": 100,
                "required": False,
                "description": "Second parameter"
            },
            "param3": {
                "type": "boolean",
                "value": True,
                "default_value": False,
                "required": False,
                "description": "Third parameter"
            }
        }
        
        node_result = NodeService.create_node(
            workflow_id=workflow_id,
            name="Test Node",
            script_id=script_id,
            input_params=initial_input_params,
            created_by="test_user"
        )
        node_id = node_result["id"]
        
        # 5. Node'u getir ve initial state'i kontrol et
        node_before = NodeService.get_node(node_id=node_id)
        assert node_before["input_params"]["param1"]["value"] == "initial_value_1"
        assert node_before["input_params"]["param1"]["default_value"] == "default1"
        assert node_before["input_params"]["param1"]["description"] == "First parameter"
        assert node_before["input_params"]["param2"]["value"] == 200
        assert node_before["input_params"]["param2"]["default_value"] == 100
        
        # 6. Sadece param1'in value'sunu güncelle
        updated_input_params = {
            "param1": {
                "value": "updated_value_1"
            }
        }
        
        update_result = NodeService.update_node_input_params(
            node_id=node_id,
            input_params=updated_input_params
        )
        
        # 7. Güncellenmiş node'u getir ve kontrol et
        node_after = NodeService.get_node(node_id=node_id)
        updated_params = node_after["input_params"]
        
        # param1 kontrolü - value güncellenmeli, diğer bilgiler korunmalı
        assert updated_params["param1"]["value"] == "updated_value_1", "param1 value güncellenmedi"
        assert updated_params["param1"]["type"] == "string", "param1 type korunmadı"
        assert updated_params["param1"]["default_value"] == "default1", "param1 default_value korunmadı"
        assert updated_params["param1"]["required"] is True, "param1 required korunmadı"
        assert updated_params["param1"]["description"] == "First parameter", "param1 description korunmadı"
        
        # param2 kontrolü - hiçbir şey değişmemeli
        assert updated_params["param2"]["value"] == 200, "param2 value değişti (olmamalıydı)"
        assert updated_params["param2"]["type"] == "number", "param2 type korunmadı"
        assert updated_params["param2"]["default_value"] == 100, "param2 default_value korunmadı"
        assert updated_params["param2"]["required"] is False, "param2 required korunmadı"
        assert updated_params["param2"]["description"] == "Second parameter", "param2 description korunmadı"
        
        # param3 kontrolü - hiçbir şey değişmemeli
        assert updated_params["param3"]["value"] is True, "param3 value değişti (olmamalıydı)"
        assert updated_params["param3"]["type"] == "boolean", "param3 type korunmadı"
        assert updated_params["param3"]["default_value"] is False, "param3 default_value korunmadı"
        assert updated_params["param3"]["required"] is False, "param3 required korunmadı"
        assert updated_params["param3"]["description"] == "Third parameter", "param3 description korunmadı"
        
        print("\n✅ Test başarılı: input_params yapısı korundu, sadece value güncellendi")
    
    def test_update_node_input_params_multiple_values(self, test_db_setup):
        """
        Test updating multiple parameter values at once.
        
        Senaryo:
        1. Node oluştur
        2. Birden fazla parametrenin value'sunu aynı anda güncelle
        3. Diğer parametrelerin bilgilerinin korunduğunu doğrula
        """
        session = test_db_setup
        
        # Test user oluştur
        from miniflow.database import RepositoryRegistry
        registry = RepositoryRegistry()
        user_repo = registry.user_repository()
        
        test_user = user_repo._create(
            session,
            username=f"test_user_2_{time.time()}",
            email=f"test2_{time.time()}@example.com",
            password_hash="dummy_hash",
            name="Test",
            surname="User",
            is_verified=True
        )
        test_user_id = test_user.id
        
        # Script oluştur
        script_data = {
            "name": f"Test Script 2 {time.time()}",
            "description": "Test script",
            "content": "def main(params): return params",
            "input_schema": {
                "a": {"type": "string", "required": True, "default": "a_default"},
                "b": {"type": "number", "required": False, "default": 10},
                "c": {"type": "boolean", "required": False, "default": False}
            },
            "output_schema": {},
            "category": "test"
        }
        
        script_result = GlobalScriptService.create_script(**script_data)
        script_id = script_result["id"]
        # Global script'ler otomatik onaylı olarak oluşturulur
        
        # Workspace ve Workflow oluştur
        workspace_result = WorkspaceManagementService.create_workspace(
            name="Test Workspace 2",
            slug=f"test-workspace-2-{time.time()}",
            description="Test",
            owner_id=test_user_id
        )
        workflow_result = WorkflowManagementService.create_workflow(
            workspace_id=workspace_result["id"],
            name="Test Workflow 2",
            description="Test",
            created_by="test_user"
        )
        
        # Node oluştur
        initial_input_params = {
            "a": {"type": "string", "value": "a1", "default_value": "a_default", "required": True, "description": "A param"},
            "b": {"type": "number", "value": 20, "default_value": 10, "required": False, "description": "B param"},
            "c": {"type": "boolean", "value": False, "default_value": False, "required": False, "description": "C param"}
        }
        
        node_result = NodeService.create_node(
            workflow_id=workflow_result["id"],
            name="Test Node 2",
            script_id=script_id,
            input_params=initial_input_params,
            created_by="test_user"
        )
        
        # Birden fazla parametreyi güncelle
        updated_input_params = {
            "a": {"value": "a2"},
            "b": {"value": 30}
        }
        
        NodeService.update_node_input_params(
            node_id=node_result["id"],
            input_params=updated_input_params
        )
        
        # Kontrol et
        node_after = NodeService.get_node(node_id=node_result["id"])
        params = node_after["input_params"]
        
        # a güncellenmeli
        assert params["a"]["value"] == "a2"
        assert params["a"]["type"] == "string"
        assert params["a"]["default_value"] == "a_default"
        
        # b güncellenmeli
        assert params["b"]["value"] == 30
        assert params["b"]["type"] == "number"
        assert params["b"]["default_value"] == 10
        
        # c değişmemeli
        assert params["c"]["value"] is False
        assert params["c"]["type"] == "boolean"
        
        print("\n✅ Test başarılı: Birden fazla parametre güncellendi, diğerleri korundu")
    
    def test_update_node_input_params_with_reference(self, test_db_setup):
        """
        Test updating parameter value with reference string.
        
        Senaryo:
        1. Node oluştur
        2. Parametrenin value'sunu reference string ile güncelle (${node:...})
        3. Reference string'in korunduğunu ve diğer bilgilerin korunduğunu doğrula
        """
        session = test_db_setup
        
        # Test user oluştur
        from miniflow.database import RepositoryRegistry
        registry = RepositoryRegistry()
        user_repo = registry.user_repository()
        
        test_user = user_repo._create(
            session,
            username=f"test_user_2_{time.time()}",
            email=f"test2_{time.time()}@example.com",
            password_hash="dummy_hash",
            name="Test",
            surname="User",
            is_verified=True
        )
        test_user_id = test_user.id
        
        # Script oluştur
        script_data = {
            "name": f"Test Script 3 {time.time()}",
            "description": "Test script",
            "content": "def main(params): return params",
            "input_schema": {
                "message": {"type": "string", "required": True, "default": "default_message"}
            },
            "output_schema": {},
            "category": "test"
        }
        
        script_result = GlobalScriptService.create_script(**script_data)
        script_id = script_result["id"]
        # Global script'ler otomatik onaylı olarak oluşturulur
        
        # Workspace ve Workflow oluştur
        workspace_result = WorkspaceManagementService.create_workspace(
            name="Test Workspace 3",
            slug=f"test-workspace-3-{time.time()}",
            description="Test",
            owner_id=test_user_id
        )
        workflow_result = WorkflowManagementService.create_workflow(
            workspace_id=workspace_result["id"],
            name="Test Workflow 3",
            description="Test",
            created_by="test_user"
        )
        
        # Node oluştur
        initial_input_params = {
            "message": {
                "type": "string",
                "value": "initial_message",
                "default_value": "default_message",
                "required": True,
                "description": "Message parameter"
            }
        }
        
        node_result = NodeService.create_node(
            workflow_id=workflow_result["id"],
            name="Test Node 3",
            script_id=script_id,
            input_params=initial_input_params,
            created_by="test_user"
        )
        
        # Reference string ile güncelle
        updated_input_params = {
            "message": {
                "value": "${node:NOD-123.result.data}"
            }
        }
        
        NodeService.update_node_input_params(
            node_id=node_result["id"],
            input_params=updated_input_params
        )
        
        # Kontrol et
        node_after = NodeService.get_node(node_id=node_result["id"])
        params = node_after["input_params"]
        
        # Reference string korunmalı
        assert params["message"]["value"] == "${node:NOD-123.result.data}"
        # Diğer bilgiler korunmalı
        assert params["message"]["type"] == "string"
        assert params["message"]["default_value"] == "default_message"
        assert params["message"]["required"] is True
        assert params["message"]["description"] == "Message parameter"
        
        print("\n✅ Test başarılı: Reference string korundu, diğer bilgiler korundu")

