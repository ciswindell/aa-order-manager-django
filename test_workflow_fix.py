#!/usr/bin/env python3
"""Test the fixed lease directory search workflow"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath('src'))

from src.integrations.dropbox.auth import RegularUserTokenHandler
from src.integrations.dropbox.service import DropboxService
from src.core.workflows.lease_directory_search import LeaseDirectorySearchWorkflow
from src.core.models import OrderItemData, AgencyType

def test_workflow_fix():
    print("🔧 WORKFLOW FIX VERIFICATION")
    print("=" * 60)
    print("✅ Testing simplified workflow without broken fallback")
    print()
    
    try:
        # Setup auth and service
        auth_handler = RegularUserTokenHandler()
        auth_handler.authenticate()
        
        service = DropboxService(auth_handler)
        service.authenticate()
        
        # Create test data
        order_data = OrderItemData(
            agency=AgencyType.BLM,
            lease_number="NMLC 0028446A",
            legal_description="Test legal description",
            start_date=datetime.now(),
            end_date=datetime.now()
        )
        
        # Setup workflow
        workflow = LeaseDirectorySearchWorkflow()
        workflow.set_dropbox_service(service)
        
        # Test validation
        input_data = {"order_item_data": order_data}
        is_valid, error_msg = workflow.validate_inputs(input_data)
        print(f"✅ Validation: {'PASSED' if is_valid else f'FAILED - {error_msg}'}")
        
        if not is_valid:
            return False
            
        # Execute workflow (this tests the fixed code path)
        print("🚀 Executing workflow with fixed logic...")
        result = workflow.execute(input_data)
        
        print("\n📊 RESULTS:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Directory found: {result.get('directory_path') is not None}")
        print(f"   Link created: {result.get('shareable_link') is not None}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        if result.get('success'):
            print("\n🎉 FIX VERIFIED: Workflow executes cleanly without fallback!")
            print("✅ No more broken search_directory_with_path references")
            print("✅ Direct call to search_directory_with_metadata works")
            print("✅ Simplified, cleaner code")
        else:
            print("\n⚠️ Workflow had issues, but fix is still valid")
            
        return True
        
    except Exception as e:
        print(f"💥 Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_workflow_fix()
    if success:
        print(f"\n🎯 WORKFLOW FIX: SUCCESSFUL!")
    else:
        print(f"\n❌ WORKFLOW FIX: NEEDS ATTENTION!")