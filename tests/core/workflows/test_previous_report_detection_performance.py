"""
Performance Tests for Previous Report Detection Workflow

Tests workflow performance with large directories (100+ files) to ensure
efficient pattern matching and reasonable execution times.
"""

import pytest
import time
from unittest.mock import Mock
from src.core.workflows.previous_report_detection import PreviousReportDetectionWorkflow
from src.core.workflows.base import WorkflowConfig
from src.core.models import OrderItemData, AgencyType
from src.integrations.dropbox.service import DropboxService


class TestPreviousReportDetectionPerformance:
    """Performance tests for PreviousReportDetectionWorkflow with large directories."""
    
    @pytest.fixture
    def mock_dropbox_service(self):
        """Create a mock DropboxService for performance tests."""
        mock_service = Mock(spec=DropboxService)
        mock_service.is_authenticated.return_value = True
        return mock_service
    
    @pytest.fixture
    def workflow(self, mock_dropbox_service):
        """Create a PreviousReportDetectionWorkflow instance."""
        return PreviousReportDetectionWorkflow(
            config=WorkflowConfig(),
            dropbox_service=mock_dropbox_service
        )
    
    @pytest.fixture
    def order_item_data(self):
        """Create OrderItemData with report_directory_path."""
        from datetime import datetime
        return OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="Section 1, Township 2N, Range 3E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            report_directory_path="/NMSLO/12345"
        )
    
    def generate_large_file_list(self, file_count: int, master_docs_count: int = 0) -> list:
        """
        Generate a large list of mock files for testing.
        
        Args:
            file_count: Total number of files to generate
            master_docs_count: Number of Master Documents files to include
            
        Returns:
            List of mock file dictionaries
        """
        files = []
        
        # Add Master Documents files first
        for i in range(master_docs_count):
            files.append({
                "name": f"Master Documents Report {i+1}.pdf",
                "type": "file",
                "size": 1024000 + i * 1000  # Varying sizes
            })
        
        # Add regular files
        regular_file_count = file_count - master_docs_count
        for i in range(regular_file_count):
            file_types = [".pdf", ".docx", ".xlsx", ".txt", ".png", ".jpg"]
            file_type = file_types[i % len(file_types)]
            files.append({
                "name": f"Document_{i+1:04d}{file_type}",
                "type": "file",
                "size": 50000 + i * 100
            })
        
        return files
    
    def test_performance_large_directory_no_master_documents(self, workflow, mock_dropbox_service, order_item_data):
        """Test performance with large directory containing no Master Documents."""
        # Generate 200 files without any Master Documents
        large_file_list = self.generate_large_file_list(200, master_docs_count=0)
        mock_dropbox_service.list_directory_files.return_value = large_file_list
        
        input_data = {
            "order_item_data": order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        # Measure execution time
        start_time = time.time()
        result = workflow.execute(input_data)
        execution_time = time.time() - start_time
        
        # Verify result
        assert result["success"] is True
        assert result["previous_report_found"] is False
        assert len(result["matching_files"]) == 0
        assert result["total_files_checked"] == 200
        
        # Verify OrderItemData was updated
        assert order_item_data.previous_report_found is False
        
        # Performance assertions
        assert execution_time < 5.0, f"Execution took too long: {execution_time:.2f}s"
        print(f"Performance: Processed 200 files in {execution_time:.3f}s")
    
    def test_performance_large_directory_with_master_documents(self, workflow, mock_dropbox_service, order_item_data):
        """Test performance with large directory containing Master Documents."""
        # Generate 150 files with 3 Master Documents
        large_file_list = self.generate_large_file_list(150, master_docs_count=3)
        mock_dropbox_service.list_directory_files.return_value = large_file_list
        
        input_data = {
            "order_item_data": order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        # Measure execution time
        start_time = time.time()
        result = workflow.execute(input_data)
        execution_time = time.time() - start_time
        
        # Verify result
        assert result["success"] is True
        assert result["previous_report_found"] is True
        assert len(result["matching_files"]) == 3
        assert result["total_files_checked"] == 150
        
        # Verify all Master Documents were found
        matching_files = result["matching_files"]
        assert "Master Documents Report 1.pdf" in matching_files
        assert "Master Documents Report 2.pdf" in matching_files
        assert "Master Documents Report 3.pdf" in matching_files
        
        # Verify OrderItemData was updated
        assert order_item_data.previous_report_found is True
        
        # Performance assertions
        assert execution_time < 5.0, f"Execution took too long: {execution_time:.2f}s"
        print(f"Performance: Processed 150 files (3 matches) in {execution_time:.3f}s")
    
    def test_performance_very_large_directory(self, workflow, mock_dropbox_service, order_item_data):
        """Test performance with very large directory (500+ files)."""
        # Generate 500 files with 5 Master Documents scattered throughout
        large_file_list = self.generate_large_file_list(500, master_docs_count=5)
        mock_dropbox_service.list_directory_files.return_value = large_file_list
        
        input_data = {
            "order_item_data": order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        # Measure execution time
        start_time = time.time()
        result = workflow.execute(input_data)
        execution_time = time.time() - start_time
        
        # Verify result
        assert result["success"] is True
        assert result["previous_report_found"] is True
        assert len(result["matching_files"]) == 5
        assert result["total_files_checked"] == 500
        
        # Performance assertions
        assert execution_time < 10.0, f"Execution took too long: {execution_time:.2f}s"
        print(f"Performance: Processed 500 files (5 matches) in {execution_time:.3f}s")
    
    def test_performance_pattern_matching_intensive(self, workflow, mock_dropbox_service, order_item_data):
        """Test performance with many files that almost match the pattern."""
        # Create files with names that are close to matching but don't match
        files = []
        
        # Add files that almost match
        near_matches = [
            "Master Document.pdf",  # Missing 's'
            "MasterDocuments.pdf",  # Missing space
            "Documents Master.pdf",  # Wrong order
            "master docs.pdf",      # Abbreviated
            "Master Docs Report.pdf", # Different word
        ]
        
        # Replicate these patterns many times
        for i in range(100):
            for pattern in near_matches:
                files.append({
                    "name": f"{i:03d}_{pattern}",
                    "type": "file"
                })
        
        # Add a few actual Master Documents
        files.extend([
            {"name": "NMSLO 12345 Master Documents.pdf", "type": "file"},
            {"name": "Updated Master Documents Report.docx", "type": "file"}
        ])
        
        mock_dropbox_service.list_directory_files.return_value = files
        
        input_data = {
            "order_item_data": order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        # Measure execution time
        start_time = time.time()
        result = workflow.execute(input_data)
        execution_time = time.time() - start_time
        
        # Verify only actual Master Documents were matched
        assert result["success"] is True
        assert result["previous_report_found"] is True
        assert len(result["matching_files"]) == 2
        assert result["total_files_checked"] == 502  # 500 near-matches + 2 real matches
        
        expected_matches = [
            "NMSLO 12345 Master Documents.pdf",
            "Updated Master Documents Report.docx"
        ]
        for expected in expected_matches:
            assert expected in result["matching_files"]
        
        # Performance assertions - pattern matching should still be fast
        assert execution_time < 8.0, f"Pattern matching took too long: {execution_time:.2f}s"
        print(f"Performance: Pattern matching on 502 files in {execution_time:.3f}s")
    
    def test_performance_memory_usage_large_directory(self, workflow, mock_dropbox_service, order_item_data):
        """Test that memory usage remains reasonable with large directories."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate very large file list (1000 files)
        large_file_list = self.generate_large_file_list(1000, master_docs_count=10)
        mock_dropbox_service.list_directory_files.return_value = large_file_list
        
        input_data = {
            "order_item_data": order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        # Execute workflow
        result = workflow.execute(input_data)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify result
        assert result["success"] is True
        assert result["total_files_checked"] == 1000
        
        # Memory usage should not increase dramatically
        assert memory_increase < 50, f"Memory usage increased too much: {memory_increase:.2f}MB"
        print(f"Performance: Memory increase for 1000 files: {memory_increase:.2f}MB")
    
    def test_performance_early_termination_optimization(self, workflow, mock_dropbox_service, order_item_data):
        """Test if workflow could benefit from early termination optimization."""
        # Note: Current implementation processes all files, but this test documents
        # the potential for optimization where we could stop after finding the first match
        
        # Create a large file list with Master Documents at the beginning
        files = [
            {"name": "Master Documents Report.pdf", "type": "file"},  # Early match
        ]
        
        # Add many more files after the match
        files.extend(self.generate_large_file_list(300, master_docs_count=0))
        
        mock_dropbox_service.list_directory_files.return_value = files
        
        input_data = {
            "order_item_data": order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        # Measure execution time
        start_time = time.time()
        result = workflow.execute(input_data)
        execution_time = time.time() - start_time
        
        # Verify result - current implementation processes all files
        assert result["success"] is True
        assert result["previous_report_found"] is True
        assert len(result["matching_files"]) == 1
        assert result["total_files_checked"] == 301
        
        # Document current performance - this could be optimized in the future
        print(f"Performance: Full directory scan of 301 files in {execution_time:.3f}s")
        print("Note: Early termination optimization could improve performance for large directories")
        
        # Current implementation should still be reasonable
        assert execution_time < 8.0, f"Execution took too long: {execution_time:.2f}s"
    
    def test_performance_concurrent_workflow_executions(self, mock_dropbox_service):
        """Test performance when multiple workflows execute concurrently."""
        import threading
        import queue
        
        # Create multiple order items
        from datetime import datetime
        order_items = []
        for i in range(5):
            order_items.append(OrderItemData(
                agency=AgencyType.NMSLO,
                lease_number=f"1234{i}",
                legal_description=f"Section {i+1}, Township 2N, Range 3E",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31),
                report_directory_path=f"/NMSLO/1234{i}"
            ))
        
        # Create large file list for each directory
        def mock_list_files(directory_path):
            # Return different file counts for different directories
            base_count = 100 + (int(directory_path[-1]) * 50)  # 100-350 files
            return self.generate_large_file_list(base_count, master_docs_count=2)
        
        mock_dropbox_service.list_directory_files.side_effect = mock_list_files
        
        results_queue = queue.Queue()
        
        def execute_workflow(order_item):
            """Execute workflow in a separate thread."""
            workflow = PreviousReportDetectionWorkflow(dropbox_service=mock_dropbox_service)
            
            input_data = {
                "order_item_data": order_item,
                "dropbox_service": mock_dropbox_service
            }
            
            start_time = time.time()
            result = workflow.execute(input_data)
            execution_time = time.time() - start_time
            
            results_queue.put((order_item.lease_number, result, execution_time))
        
        # Start all workflows concurrently
        threads = []
        overall_start_time = time.time()
        
        for order_item in order_items:
            thread = threading.Thread(target=execute_workflow, args=(order_item,))
            thread.start()
            threads.append(thread)
        
        # Wait for all workflows to complete
        for thread in threads:
            thread.join()
        
        overall_execution_time = time.time() - overall_start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Verify all workflows completed successfully
        assert len(results) == 5
        
        for lease_number, result, execution_time in results:
            assert result["success"] is True
            assert result["previous_report_found"] is True  # All should find Master Documents
            assert execution_time < 10.0, f"Individual workflow took too long: {execution_time:.2f}s"
        
        # Overall time should be reasonable (not much more than individual execution)
        max_individual_time = max(result[2] for result in results)
        # Allow for some threading overhead - use a more lenient check for very fast operations
        time_threshold = max(max_individual_time * 3, 0.01)  # At least 10ms threshold
        assert overall_execution_time < time_threshold, \
            f"Concurrent execution inefficient: {overall_execution_time:.2f}s vs {max_individual_time:.2f}s"
        
        print(f"Performance: 5 concurrent workflows completed in {overall_execution_time:.3f}s")
        print(f"Individual times: {[f'{r[2]:.3f}s' for r in results]}")
    
    @pytest.mark.parametrize("file_count,expected_max_time", [
        (50, 2.0),
        (100, 3.0),
        (200, 5.0),
        (500, 10.0),
    ])
    def test_performance_scaling_with_file_count(self, workflow, mock_dropbox_service, 
                                               order_item_data, file_count, expected_max_time):
        """Test that performance scales reasonably with file count."""
        # Generate files with a few Master Documents
        large_file_list = self.generate_large_file_list(file_count, master_docs_count=3)
        mock_dropbox_service.list_directory_files.return_value = large_file_list
        
        input_data = {
            "order_item_data": order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        # Measure execution time
        start_time = time.time()
        result = workflow.execute(input_data)
        execution_time = time.time() - start_time
        
        # Verify result
        assert result["success"] is True
        assert result["total_files_checked"] == file_count
        
        # Performance should scale reasonably
        assert execution_time < expected_max_time, \
            f"Processing {file_count} files took {execution_time:.2f}s (expected < {expected_max_time}s)"
        
        print(f"Performance: {file_count} files processed in {execution_time:.3f}s")