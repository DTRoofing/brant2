"""
Performance tests for PDF processing pipeline.
"""
import pytest
import time
import asyncio
import concurrent.futures
import uuid
from pathlib import Path
from unittest.mock import patch, Mock
import statistics
import psutil
import os

from app.core.pdf_processing import extract_text_from_pdf, async_process_pdf_document
from app.models.core import Document, ProcessingStatus


class TestPDFProcessingPerformance:
    """Performance tests for PDF text extraction and processing."""
    
    @pytest.mark.performance
    def test_text_extraction_performance_small_pdf(self, sample_pdf_with_text):
        """Test performance of text extraction from small PDF files."""
        start_time = time.perf_counter()
        
        extracted_text = extract_text_from_pdf(str(sample_pdf_with_text))
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        
        assert extracted_text is not None
        assert len(extracted_text) > 0
        
        # Small PDF should process very quickly (under 2 seconds)
        assert processing_time < 2.0, f"Small PDF took {processing_time:.2f}s to process"
        
        print(f"Small PDF extraction time: {processing_time:.3f}s")
        print(f"Text length: {len(extracted_text)} characters")
        print(f"Processing rate: {len(extracted_text)/processing_time:.0f} chars/sec")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_text_extraction_performance_large_pdf(self, large_pdf):
        """Test performance of text extraction from large PDF files."""
        start_time = time.perf_counter()
        
        extracted_text = extract_text_from_pdf(str(large_pdf))
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        
        assert extracted_text is not None
        assert len(extracted_text) > 1000  # Should have substantial content
        
        # Large PDF should still process in reasonable time (under 30 seconds)
        assert processing_time < 30.0, f"Large PDF took {processing_time:.2f}s to process"
        
        print(f"Large PDF extraction time: {processing_time:.3f}s")
        print(f"Text length: {len(extracted_text)} characters")
        print(f"Processing rate: {len(extracted_text)/processing_time:.0f} chars/sec")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_memory_usage_large_pdf(self, large_pdf):
        """Test memory usage during large PDF processing."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        extracted_text = extract_text_from_pdf(str(large_pdf))
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = peak_memory - initial_memory
        
        assert extracted_text is not None
        
        # Memory usage should be reasonable (under 500MB for large PDF)
        assert memory_used < 500, f"Memory usage {memory_used:.1f}MB exceeded limit"
        
        print(f"Memory used: {memory_used:.1f}MB")
        print(f"Peak memory: {peak_memory:.1f}MB")
    
    @pytest.mark.performance
    def test_concurrent_text_extraction_performance(self, sample_pdf_with_text):
        """Test performance of concurrent text extraction."""
        num_concurrent = 5
        
        def extract_text():
            start = time.perf_counter()
            result = extract_text_from_pdf(str(sample_pdf_with_text))
            end = time.perf_counter()
            return end - start, len(result)
        
        start_time = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(extract_text) for _ in range(num_concurrent)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.perf_counter() - start_time
        
        processing_times = [r[0] for r in results]
        text_lengths = [r[1] for r in results]
        
        avg_processing_time = statistics.mean(processing_times)
        max_processing_time = max(processing_times)
        
        # All extractions should succeed
        assert len(results) == num_concurrent
        assert all(length > 0 for length in text_lengths)
        
        # Concurrent processing should not be significantly slower
        assert total_time < avg_processing_time * 2, "Concurrent processing too slow"
        
        print(f"Concurrent extraction - Total time: {total_time:.3f}s")
        print(f"Average processing time: {avg_processing_time:.3f}s")
        print(f"Max processing time: {max_processing_time:.3f}s")
        print(f"Throughput: {num_concurrent/total_time:.2f} docs/sec")


class TestPDFProcessingAsyncPerformance:
    """Performance tests for async PDF processing operations."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_async_processing_performance(self, async_db, sample_pdf_with_text):
        """Test performance of async PDF document processing."""
        # Create document record
        document = Document(
            id=uuid.uuid4(),
            filename="perf_test.pdf",
            file_path=str(sample_pdf_with_text),
            file_size=1024,
            processing_status=ProcessingStatus.PENDING
        )
        async_db.add(document)
        await async_db.commit()
        await async_db.refresh(document)
        
        start_time = time.perf_counter()
        
        result = await async_process_pdf_document(str(document.id))
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        
        assert result["status"] == "success"
        
        # Async processing should be reasonably fast
        assert processing_time < 10.0, f"Async processing took {processing_time:.2f}s"
        
        print(f"Async processing time: {processing_time:.3f}s")
        print(f"Text extracted: {result['extracted_text_length']} characters")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_async_processing_performance(self, async_db, sample_pdf_with_text):
        """Test performance of concurrent async processing."""
        num_concurrent = 10
        documents = []
        
        # Create multiple document records
        for i in range(num_concurrent):
            document = Document(
                id=uuid.uuid4(),
                filename=f"concurrent_test_{i}.pdf",
                file_path=str(sample_pdf_with_text),
                file_size=1024,
                processing_status=ProcessingStatus.PENDING
            )
            async_db.add(document)
            documents.append(document)
        
        await async_db.commit()
        for doc in documents:
            await async_db.refresh(doc)
        
        start_time = time.perf_counter()
        
        # Process all documents concurrently
        tasks = [
            async_process_pdf_document(str(doc.id))
            for doc in documents
        ]
        
        results = await asyncio.gather(*tasks)
        
        total_time = time.perf_counter() - start_time
        
        # All should succeed
        assert len(results) == num_concurrent
        assert all(r["status"] == "success" for r in results)
        
        # Concurrent processing should scale reasonably
        throughput = num_concurrent / total_time
        assert throughput > 1.0, f"Throughput {throughput:.2f} docs/sec too low"
        
        print(f"Concurrent async processing - Total time: {total_time:.3f}s")
        print(f"Throughput: {throughput:.2f} docs/sec")
        print(f"Average per document: {total_time/num_concurrent:.3f}s")


class TestPDFUploadPerformance:
    """Performance tests for PDF upload operations."""
    
    @pytest.mark.performance
    def test_upload_performance_small_pdf(self, test_client, sample_pdf_with_text):
        """Test upload performance for small PDF files."""
        file_size = Path(sample_pdf_with_text).stat().st_size
        
        start_time = time.perf_counter()
        
        with open(sample_pdf_with_text, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("perf_test.pdf", f, "application/pdf")}
            )
        
        end_time = time.perf_counter()
        upload_time = end_time - start_time
        
        assert response.status_code == 202
        
        # Upload should be very fast for small files
        assert upload_time < 5.0, f"Small PDF upload took {upload_time:.2f}s"
        
        upload_speed = file_size / upload_time / 1024 / 1024  # MB/s
        
        print(f"Small PDF upload time: {upload_time:.3f}s")
        print(f"File size: {file_size/1024:.1f}KB")
        print(f"Upload speed: {upload_speed:.2f} MB/s")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_upload_performance_large_pdf(self, test_client, large_pdf):
        """Test upload performance for large PDF files."""
        file_size = Path(large_pdf).stat().st_size
        
        start_time = time.perf_counter()
        
        with open(large_pdf, "rb") as f:
            response = test_client.post(
                "/api/v1/documents/upload",
                files={"file": ("large_perf_test.pdf", f, "application/pdf")}
            )
        
        end_time = time.perf_counter()
        upload_time = end_time - start_time
        
        assert response.status_code == 202
        
        # Upload should complete in reasonable time
        assert upload_time < 30.0, f"Large PDF upload took {upload_time:.2f}s"
        
        upload_speed = file_size / upload_time / 1024 / 1024  # MB/s
        
        print(f"Large PDF upload time: {upload_time:.3f}s")
        print(f"File size: {file_size/1024/1024:.1f}MB")
        print(f"Upload speed: {upload_speed:.2f} MB/s")
    
    @pytest.mark.performance
    def test_concurrent_upload_performance(self, test_client, sample_pdf_with_text):
        """Test performance of concurrent uploads."""
        num_concurrent = 5
        
        def upload_file():
            start = time.perf_counter()
            with open(sample_pdf_with_text, "rb") as f:
                response = test_client.post(
                    "/api/v1/documents/upload",
                    files={"file": (f"concurrent_{uuid.uuid4()}.pdf", f, "application/pdf")}
                )
            end = time.perf_counter()
            return end - start, response.status_code
        
        start_time = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(upload_file) for _ in range(num_concurrent)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.perf_counter() - start_time
        
        upload_times = [r[0] for r in results]
        status_codes = [r[1] for r in results]
        
        # All uploads should succeed
        assert all(code == 202 for code in status_codes)
        
        avg_upload_time = statistics.mean(upload_times)
        throughput = num_concurrent / total_time
        
        print(f"Concurrent uploads - Total time: {total_time:.3f}s")
        print(f"Average upload time: {avg_upload_time:.3f}s")
        print(f"Throughput: {throughput:.2f} uploads/sec")


class TestPDFProcessingScalability:
    """Scalability tests for PDF processing under load."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_processing_scalability_increasing_load(self, sample_pdf_with_text):
        """Test how processing performance scales with increasing load."""
        load_levels = [1, 2, 5, 10]
        results = []
        
        for load in load_levels:
            def process_batch():
                start = time.perf_counter()
                extract_text_from_pdf(str(sample_pdf_with_text))
                return time.perf_counter() - start
            
            start_time = time.perf_counter()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=load) as executor:
                futures = [executor.submit(process_batch) for _ in range(load)]
                processing_times = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            total_time = time.perf_counter() - start_time
            avg_processing_time = statistics.mean(processing_times)
            throughput = load / total_time
            
            results.append({
                'load': load,
                'total_time': total_time,
                'avg_processing_time': avg_processing_time,
                'throughput': throughput
            })
            
            print(f"Load {load}: {total_time:.3f}s total, {throughput:.2f} docs/sec")
        
        # Throughput should generally increase with load (up to a point)
        assert results[1]['throughput'] > results[0]['throughput'] * 0.8
        
        return results
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_memory_scalability_under_load(self, sample_pdf_with_text):
        """Test memory usage under increasing processing load."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        load_levels = [1, 5, 10]
        
        for load in load_levels:
            def process_document():
                return extract_text_from_pdf(str(sample_pdf_with_text))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=load) as executor:
                futures = [executor.submit(process_document) for _ in range(load)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = current_memory - initial_memory
            
            # All should succeed
            assert all(len(result) > 0 for result in results)
            
            # Memory usage should not grow excessively
            memory_per_doc = memory_used / load
            assert memory_per_doc < 100, f"Memory per document {memory_per_doc:.1f}MB too high"
            
            print(f"Load {load}: {memory_used:.1f}MB total, {memory_per_doc:.1f}MB per doc")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_sustained_processing_performance(self, sample_pdf_with_text):
        """Test performance during sustained processing over time."""
        duration_seconds = 30
        processing_times = []
        
        start_time = time.perf_counter()
        
        while time.perf_counter() - start_time < duration_seconds:
            doc_start = time.perf_counter()
            
            extracted_text = extract_text_from_pdf(str(sample_pdf_with_text))
            
            doc_end = time.perf_counter()
            processing_times.append(doc_end - doc_start)
            
            assert len(extracted_text) > 0
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.1)
        
        total_documents = len(processing_times)
        avg_processing_time = statistics.mean(processing_times)
        std_processing_time = statistics.stdev(processing_times) if len(processing_times) > 1 else 0
        
        # Performance should be consistent over time
        assert std_processing_time < avg_processing_time * 0.5, "Performance too variable"
        
        print(f"Sustained processing for {duration_seconds}s:")
        print(f"Documents processed: {total_documents}")
        print(f"Average time: {avg_processing_time:.3f}s ± {std_processing_time:.3f}s")
        print(f"Throughput: {total_documents/duration_seconds:.2f} docs/sec")


class TestPDFProcessingResourceUsage:
    """Tests for resource usage patterns during PDF processing."""
    
    @pytest.mark.performance
    def test_cpu_usage_during_processing(self, sample_pdf_with_text):
        """Test CPU usage patterns during PDF processing."""
        process = psutil.Process(os.getpid())
        
        # Monitor CPU usage
        cpu_percentages = []
        
        def monitor_cpu():
            for _ in range(10):  # Monitor for ~1 second
                cpu_percentages.append(process.cpu_percent(interval=0.1))
        
        # Start monitoring in background
        import threading
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        # Process document
        extracted_text = extract_text_from_pdf(str(sample_pdf_with_text))
        
        # Wait for monitoring to complete
        monitor_thread.join()
        
        assert len(extracted_text) > 0
        
        if cpu_percentages:
            avg_cpu = statistics.mean(cpu_percentages)
            max_cpu = max(cpu_percentages)
            
            print(f"CPU usage - Average: {avg_cpu:.1f}%, Peak: {max_cpu:.1f}%")
            
            # CPU usage should be reasonable
            assert max_cpu < 90, f"Peak CPU usage {max_cpu:.1f}% too high"
    
    @pytest.mark.performance
    def test_file_handle_usage(self, sample_pdf_with_text):
        """Test that file handles are properly managed during processing."""
        process = psutil.Process(os.getpid())
        initial_open_files = len(process.open_files())
        
        # Process multiple documents
        for _ in range(10):
            extracted_text = extract_text_from_pdf(str(sample_pdf_with_text))
            assert len(extracted_text) > 0
        
        final_open_files = len(process.open_files())
        file_handle_leak = final_open_files - initial_open_files
        
        # Should not leak file handles
        assert file_handle_leak <= 2, f"File handle leak detected: {file_handle_leak} files"
        
        print(f"File handles - Initial: {initial_open_files}, Final: {final_open_files}")


# Performance test markers and configuration
def pytest_configure(config):
    """Configure performance test markers."""
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )