#!/usr/bin/env python3
"""
Supabase Intermediary Architecture - Sanity Check

Tests the proposed architecture:
1. Upload file to Supabase Storage
2. Download from Supabase Storage
3. Upload to Moonshot/Kimi API
4. Measure performance impact
5. Calculate cost implications

This validates whether using Supabase as intermediary is viable.
"""

import asyncio
import json
import sys
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.supabase_client import SupabaseStorageManager
from tools.providers.kimi.kimi_files import KimiUploadFilesTool


class SupabaseIntermediaryTest:
    """Test Supabase intermediary architecture"""
    
    def __init__(self):
        self.storage = SupabaseStorageManager()
        self.kimi_tool = KimiUploadFilesTool()
        self.results = {
            "direct_upload": {},
            "supabase_intermediary": {},
            "comparison": {}
        }
    
    def create_test_file(self, size_kb: int = 100) -> Path:
        """Create a test file of specified size"""
        # Use /app for writable location (not /mnt/project which is read-only)
        if Path("/app").exists():
            test_file = Path("/app") / f"test_file_{size_kb}kb.txt"
        else:
            test_file = project_root / f"test_file_{size_kb}kb.txt"

        # Generate random content
        content = "Test content " * (size_kb * 1024 // 13)  # ~13 bytes per line
        test_file.write_text(content[:size_kb * 1024])

        print(f"✅ Created test file: {test_file} ({size_kb}KB)")
        return test_file
    
    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            sha256.update(f.read())
        return sha256.hexdigest()
    
    def test_direct_upload(self, file_path: Path) -> Dict[str, Any]:
        """Test direct upload to Moonshot (current approach)"""
        print("\n" + "="*70)
        print("TEST 1: DIRECT UPLOAD (Current Approach)")
        print("="*70)
        
        start_time = time.time()
        
        try:
            # Direct upload to Kimi
            result = self.kimi_tool._run(files=[str(file_path)], purpose="file-extract")
            
            elapsed = time.time() - start_time
            
            if result and len(result) > 0:
                file_id = result[0].get('file_id')
                print(f"✅ Direct upload successful!")
                print(f"   File ID: {file_id}")
                print(f"   Duration: {elapsed:.2f}s")
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "duration_seconds": elapsed,
                    "method": "direct"
                }
            else:
                print(f"❌ Direct upload failed - no file_id returned")
                return {"success": False, "error": "No file_id returned"}
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Direct upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": elapsed
            }
    
    def test_supabase_intermediary(self, file_path: Path) -> Dict[str, Any]:
        """Test Supabase intermediary approach (proposed)"""
        print("\n" + "="*70)
        print("TEST 2: SUPABASE INTERMEDIARY (Proposed Approach)")
        print("="*70)
        
        total_start = time.time()
        
        try:
            # Step 1: Upload to Supabase Storage
            print("\n📤 Step 1: Upload to Supabase Storage...")
            upload_start = time.time()
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            supabase_file_id = self.storage.upload_file(
                file_path=f"test/{file_path.name}",
                file_data=file_data,
                original_name=file_path.name,
                file_type="user_upload"
            )
            
            upload_duration = time.time() - upload_start
            
            if not supabase_file_id:
                print(f"❌ Supabase upload failed")
                return {"success": False, "error": "Supabase upload failed"}
            
            print(f"✅ Uploaded to Supabase: {supabase_file_id}")
            print(f"   Duration: {upload_duration:.2f}s")
            
            # Step 2: Download from Supabase Storage
            print("\n📥 Step 2: Download from Supabase Storage...")
            download_start = time.time()
            
            downloaded_data = self.storage.download_file(file_id=supabase_file_id)
            
            download_duration = time.time() - download_start
            
            if not downloaded_data:
                print(f"❌ Supabase download failed")
                return {"success": False, "error": "Supabase download failed"}
            
            print(f"✅ Downloaded from Supabase: {len(downloaded_data)} bytes")
            print(f"   Duration: {download_duration:.2f}s")
            
            # Verify data integrity
            original_hash = self.calculate_sha256(file_path)
            downloaded_hash = hashlib.sha256(downloaded_data).hexdigest()
            
            if original_hash != downloaded_hash:
                print(f"❌ Data integrity check failed!")
                return {"success": False, "error": "Hash mismatch"}
            
            print(f"✅ Data integrity verified (SHA256 match)")
            
            # Step 3: Upload to Moonshot from downloaded data
            print("\n📤 Step 3: Upload to Moonshot from Supabase data...")
            moonshot_start = time.time()
            
            # Save downloaded data to temp file for Kimi upload
            if Path("/app").exists():
                temp_file = Path("/app") / f"temp_{file_path.name}"
            else:
                temp_file = project_root / f"temp_{file_path.name}"
            temp_file.write_bytes(downloaded_data)
            
            result = self.kimi_tool._run(files=[str(temp_file)], purpose="file-extract")
            
            moonshot_duration = time.time() - moonshot_start
            
            # Cleanup temp file
            temp_file.unlink()
            
            total_duration = time.time() - total_start
            
            if result and len(result) > 0:
                file_id = result[0].get('file_id')
                print(f"✅ Moonshot upload successful!")
                print(f"   File ID: {file_id}")
                print(f"   Duration: {moonshot_duration:.2f}s")
                print(f"\n⏱️  TOTAL DURATION: {total_duration:.2f}s")
                print(f"   - Supabase upload: {upload_duration:.2f}s")
                print(f"   - Supabase download: {download_duration:.2f}s")
                print(f"   - Moonshot upload: {moonshot_duration:.2f}s")
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "supabase_file_id": supabase_file_id,
                    "duration_seconds": total_duration,
                    "breakdown": {
                        "supabase_upload": upload_duration,
                        "supabase_download": download_duration,
                        "moonshot_upload": moonshot_duration
                    },
                    "method": "supabase_intermediary"
                }
            else:
                print(f"❌ Moonshot upload failed - no file_id returned")
                return {"success": False, "error": "Moonshot upload failed"}
                
        except Exception as e:
            total_duration = time.time() - total_start
            print(f"❌ Supabase intermediary failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": total_duration
            }
    
    def compare_results(self):
        """Compare direct vs intermediary approaches"""
        print("\n" + "="*70)
        print("COMPARISON: DIRECT vs SUPABASE INTERMEDIARY")
        print("="*70)
        
        direct = self.results["direct_upload"]
        intermediary = self.results["supabase_intermediary"]
        
        if not direct.get("success") or not intermediary.get("success"):
            print("❌ Cannot compare - one or both tests failed")
            return
        
        direct_time = direct["duration_seconds"]
        intermediary_time = intermediary["duration_seconds"]
        overhead = intermediary_time - direct_time
        overhead_pct = (overhead / direct_time) * 100
        
        print(f"\n⏱️  PERFORMANCE:")
        print(f"   Direct upload:        {direct_time:.2f}s")
        print(f"   Supabase intermediary: {intermediary_time:.2f}s")
        print(f"   Overhead:             {overhead:.2f}s ({overhead_pct:.1f}% slower)")
        
        if overhead_pct < 50:
            print(f"   ✅ Acceptable overhead (<50%)")
        elif overhead_pct < 100:
            print(f"   ⚠️  Moderate overhead (50-100%)")
        else:
            print(f"   ❌ High overhead (>100%)")
        
        # Cost estimation (Supabase Pro)
        file_size_mb = Path(self.test_file).stat().st_size / (1024 * 1024)
        
        print(f"\n💰 COST ESTIMATION (Supabase Pro):")
        print(f"   File size: {file_size_mb:.2f}MB")
        print(f"   Storage: Included in Pro plan (100GB)")
        print(f"   Bandwidth (egress): ${file_size_mb * 0.09:.4f} per download")
        print(f"   Note: Each file upload requires 1 download (to send to Moonshot)")
        
        self.results["comparison"] = {
            "direct_time": direct_time,
            "intermediary_time": intermediary_time,
            "overhead_seconds": overhead,
            "overhead_percentage": overhead_pct,
            "file_size_mb": file_size_mb,
            "bandwidth_cost_per_file": file_size_mb * 0.09
        }
    
    def run_tests(self, file_size_kb: int = 100):
        """Run all tests"""
        print("\n" + "="*70)
        print("SUPABASE INTERMEDIARY ARCHITECTURE - SANITY CHECK")
        print("="*70)
        
        # Create test file
        self.test_file = self.create_test_file(file_size_kb)
        
        # Test 1: Direct upload
        self.results["direct_upload"] = self.test_direct_upload(self.test_file)
        
        # Test 2: Supabase intermediary
        self.results["supabase_intermediary"] = self.test_supabase_intermediary(self.test_file)
        
        # Compare results
        self.compare_results()
        
        # Save results
        if Path("/app").exists():
            results_file = Path("/app") / "supabase_intermediary_test_results.json"
        else:
            results_file = project_root / "supabase_intermediary_test_results.json"
        results_file.write_text(json.dumps(self.results, indent=2))
        print(f"\n📊 Results saved to: {results_file}")
        
        # Cleanup test file
        self.test_file.unlink()
        print(f"🧹 Cleaned up test file")
        
        return self.results


def main():
    """Main test runner"""
    tester = SupabaseIntermediaryTest()
    
    # Test with 100KB file (typical markdown document)
    results = tester.run_tests(file_size_kb=100)
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    
    if results["direct_upload"].get("success") and results["supabase_intermediary"].get("success"):
        print("✅ Both approaches work!")
        print(f"\n📈 RECOMMENDATION:")
        
        overhead_pct = results["comparison"]["overhead_percentage"]
        
        if overhead_pct < 50:
            print("   ✅ SUPABASE INTERMEDIARY IS VIABLE")
            print("   - Acceptable performance overhead")
            print("   - Benefits: Universal access, persistence, audit trail")
        elif overhead_pct < 100:
            print("   ⚠️  CONDITIONAL RECOMMENDATION")
            print("   - Moderate performance impact")
            print("   - Use for non-time-critical operations")
        else:
            print("   ❌ NOT RECOMMENDED FOR REAL-TIME USE")
            print("   - High performance overhead")
            print("   - Consider hybrid approach (outputs only)")
    else:
        print("❌ One or both approaches failed - see details above")


if __name__ == "__main__":
    main()

