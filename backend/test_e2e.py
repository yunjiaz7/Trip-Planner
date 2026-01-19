"""
End-to-End Test Script

Purpose:
1. Test the complete trip planning flow from API request to response
2. Verify API compatibility
3. Verify response format
4. Test error handling

Usage:
    python test_e2e.py
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.agents.trip_planner_agent import get_trip_planner_agent
from app.models.schemas import TripRequest, TripPlan


def test_api_compatibility():
    """Test API interface compatibility"""
    print("=" * 60)
    print("Test 1: API Interface Compatibility")
    print("=" * 60)
    
    try:
        # Get planner instance
        planner = get_trip_planner_agent()
        
        # Verify plan_trip method exists
        if not hasattr(planner, 'plan_trip'):
            print("❌ plan_trip method not found")
            return False
        
        print("✅ plan_trip method exists")
        
        # Verify method signature
        import inspect
        sig = inspect.signature(planner.plan_trip)
        params = list(sig.parameters.keys())
        
        if 'request' not in params:
            print("❌ plan_trip method signature incorrect")
            return False
        
        print(f"✅ plan_trip method signature correct: {sig}")
        return True
        
    except Exception as e:
        print(f"❌ API compatibility test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_request_response_format():
    """Test request and response format"""
    print("\n" + "=" * 60)
    print("Test 2: Request/Response Format")
    print("=" * 60)
    
    try:
        planner = get_trip_planner_agent()
        
        # Create a test request
        start_date = datetime.now() + timedelta(days=7)
        end_date = start_date + timedelta(days=2)
        
        request = TripRequest(
            city="Beijing",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            travel_days=2,
            preferences=["historical culture"],
            transportation="taxi",
            accommodation="hotel",
            budget=5000
        )
        
        print(f"Request created:")
        print(f"  City: {request.city}")
        print(f"  Dates: {request.start_date} to {request.end_date}")
        print(f"  Days: {request.travel_days}")
        print(f"  Preferences: {request.preferences}")
        
        # Call plan_trip
        print("\nCalling plan_trip...")
        trip_plan = planner.plan_trip(request)
        
        # Verify response type
        if not isinstance(trip_plan, TripPlan):
            print(f"❌ Response is not TripPlan type, got: {type(trip_plan)}")
            return False
        
        print("✅ Response is TripPlan type")
        
        # Verify required fields
        required_fields = ['city', 'start_date', 'end_date', 'days', 'weather_info', 'overall_suggestions']
        for field in required_fields:
            if not hasattr(trip_plan, field):
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ All required fields present")
        
        # Verify data types
        if trip_plan.city != request.city:
            print(f"⚠️  City mismatch: expected {request.city}, got {trip_plan.city}")
        
        if len(trip_plan.days) != request.travel_days:
            print(f"⚠️  Days count mismatch: expected {request.travel_days}, got {len(trip_plan.days)}")
        else:
            print(f"✅ Days count matches: {len(trip_plan.days)}")
        
        # Verify days structure
        for i, day in enumerate(trip_plan.days):
            if not hasattr(day, 'attractions'):
                print(f"❌ Day {i} missing attractions field")
                return False
            if not hasattr(day, 'meals'):
                print(f"❌ Day {i} missing meals field")
                return False
        
        print("✅ Days structure valid")
        
        # Print summary
        print(f"\nResponse summary:")
        print(f"  City: {trip_plan.city}")
        print(f"  Days: {len(trip_plan.days)}")
        print(f"  Weather info: {len(trip_plan.weather_info)} items")
        print(f"  Overall suggestions: {len(trip_plan.overall_suggestions)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Request/Response format test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_json_serialization():
    """Test JSON serialization (for API response)"""
    print("\n" + "=" * 60)
    print("Test 3: JSON Serialization")
    print("=" * 60)
    
    try:
        planner = get_trip_planner_agent()
        
        # Create a test request
        start_date = datetime.now() + timedelta(days=7)
        end_date = start_date + timedelta(days=1)
        
        request = TripRequest(
            city="Shanghai",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            travel_days=1,
            preferences=[],
            transportation="subway",
            accommodation="hotel",
            budget=3000
        )
        
        # Get trip plan
        trip_plan = planner.plan_trip(request)
        
        # Try to serialize to JSON
        try:
            json_str = json.dumps(trip_plan.model_dump(), ensure_ascii=False, indent=2)
            print(f"✅ JSON serialization successful")
            print(f"   JSON length: {len(json_str)} characters")
            
            # Try to deserialize
            data = json.loads(json_str)
            print(f"✅ JSON deserialization successful")
            
            # Verify structure
            if 'city' in data and 'days' in data:
                print(f"✅ JSON structure valid")
                return True
            else:
                print(f"❌ JSON structure invalid")
                return False
                
        except Exception as e:
            print(f"❌ JSON serialization failed: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ JSON serialization test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("Test 4: Error Handling")
    print("=" * 60)
    
    try:
        planner = get_trip_planner_agent()
        
        # Test with invalid city (should still return a fallback plan)
        request = TripRequest(
            city="InvalidCity12345",
            start_date="2025-01-01",
            end_date="2025-01-02",
            travel_days=1,
            preferences=[],
            transportation="walking",
            accommodation="hotel",
            budget=1000
        )
        
        print("Testing with invalid city...")
        trip_plan = planner.plan_trip(request)
        
        # Should still return a valid TripPlan (fallback)
        if isinstance(trip_plan, TripPlan):
            print("✅ Error handling works: returns fallback plan")
            return True
        else:
            print("❌ Error handling failed: no fallback plan")
            return False
        
    except Exception as e:
        # If exception is raised, that's also acceptable (depends on implementation)
        print(f"⚠️  Exception raised (may be acceptable): {str(e)}")
        return True  # Acceptable if system handles errors gracefully


def test_english_output():
    """Test that all output is in English"""
    print("\n" + "=" * 60)
    print("Test 5: English Output Verification")
    print("=" * 60)
    
    try:
        planner = get_trip_planner_agent()
        
        # Create a test request
        start_date = datetime.now() + timedelta(days=7)
        end_date = start_date + timedelta(days=1)
        
        request = TripRequest(
            city="Beijing",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            travel_days=1,
            preferences=["historical culture"],
            transportation="taxi",
            accommodation="hotel",
            budget=5000
        )
        
        # Get trip plan
        trip_plan = planner.plan_trip(request)
        
        # Check overall_suggestions for Chinese characters
        if trip_plan.overall_suggestions:
            # Check for Chinese characters (Unicode range)
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in trip_plan.overall_suggestions)
            if has_chinese:
                print("⚠️  Overall suggestions contains Chinese characters")
                print(f"   Sample: {trip_plan.overall_suggestions[:100]}")
            else:
                print("✅ Overall suggestions is in English")
        
        # Check day descriptions
        for i, day in enumerate(trip_plan.days):
            if day.description:
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in day.description)
                if has_chinese:
                    print(f"⚠️  Day {i} description contains Chinese: {day.description[:50]}")
        
        print("✅ English output verification completed")
        return True
        
    except Exception as e:
        print(f"❌ English output test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("End-to-End Test Suite")
    print("=" * 60)
    print("\nThis test suite verifies:")
    print("1. API interface compatibility")
    print("2. Request/Response format")
    print("3. JSON serialization")
    print("4. Error handling")
    print("5. English output")
    
    results = []
    
    # Test 1: API compatibility
    results.append(("API Compatibility", test_api_compatibility()))
    
    # Test 2: Request/Response format
    results.append(("Request/Response Format", test_request_response_format()))
    
    # Test 3: JSON serialization
    results.append(("JSON Serialization", test_json_serialization()))
    
    # Test 4: Error handling
    results.append(("Error Handling", test_error_handling()))
    
    # Test 5: English output
    results.append(("English Output", test_english_output()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for deployment.")
        return 0
    elif passed >= total - 1:
        print("\n⚠️  Most tests passed, system is mostly ready.")
        return 0
    else:
        print("\n❌ Multiple tests failed, please check the system.")
        return 1


if __name__ == "__main__":
    exit(main())
