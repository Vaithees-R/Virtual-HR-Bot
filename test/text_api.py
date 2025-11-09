import requests
import json

class GoogleAPITester:
    def __init__(self, api_key):
        self.api_key = api_key
        self.working_apis = []
        
    def test_gemini_api(self):
        """Test Google Gemini (Generative AI) API"""
        print("\n[1] Testing Gemini (Generative AI) API...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": "Say 'Hello' if you can read this"}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            
            if response.status_code == 200 and 'candidates' in data:
                print("✅ GEMINI API - WORKING!")
                print(f"   Response: {data['candidates'][0]['content']['parts'][0]['text'][:50]}...")
                self.working_apis.append("Gemini (Generative AI)")
                return True
            else:
                print(f"❌ Not configured for Gemini")
                print(f"   Error: {data.get('error', {}).get('message', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_maps_api(self):
        """Test Google Maps Geocoding API"""
        print("\n[2] Testing Google Maps API...")
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': 'Google Headquarters',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                print("✅ GOOGLE MAPS API - WORKING!")
                self.working_apis.append("Google Maps")
                return True
            else:
                print(f"❌ Not configured for Maps")
                print(f"   Status: {data['status']}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_youtube_api(self):
        """Test YouTube Data API"""
        print("\n[3] Testing YouTube Data API...")
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': 'test',
            'key': self.api_key,
            'maxResults': 1
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'items' in data:
                print("✅ YOUTUBE DATA API - WORKING!")
                self.working_apis.append("YouTube Data API")
                return True
            else:
                print(f"❌ Not configured for YouTube")
                if 'error' in data:
                    print(f"   Error: {data['error']['message']}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_cloud_vision_api(self):
        """Test Cloud Vision API"""
        print("\n[4] Testing Cloud Vision API...")
        url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
        
        payload = {
            "requests": [{
                "image": {
                    "source": {
                        "imageUri": "https://cloud.google.com/vision/docs/images/rushmore.png"
                    }
                },
                "features": [{"type": "LABEL_DETECTION", "maxResults": 1}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            
            if 'responses' in data and not data['responses'][0].get('error'):
                print("✅ CLOUD VISION API - WORKING!")
                self.working_apis.append("Cloud Vision")
                return True
            else:
                print(f"❌ Not configured for Cloud Vision")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_translate_api(self):
        """Test Cloud Translation API"""
        print("\n[5] Testing Cloud Translation API...")
        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            'q': 'Hello',
            'target': 'es',
            'key': self.api_key
        }
        
        try:
            response = requests.post(url, params=params)
            data = response.json()
            
            if 'data' in data:
                print("✅ CLOUD TRANSLATION API - WORKING!")
                self.working_apis.append("Cloud Translation")
                return True
            else:
                print(f"❌ Not configured for Translation")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_speech_to_text_api(self):
        """Test Speech-to-Text API (requires OAuth, not API key)"""
        print("\n[6] Testing Speech-to-Text API...")
        print("⚠️  Speech-to-Text typically requires OAuth, not API keys")
        print("   Skipping this test")
        return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("="*60)
        print("🔍 GOOGLE API KEY IDENTIFIER")
        print("="*60)
        print(f"\nTesting API Key: {self.api_key[:15]}...{self.api_key[-6:]}")
        print("\nRunning tests on common Google APIs...\n")
        
        # Run all tests
        self.test_gemini_api()
        self.test_maps_api()
        self.test_youtube_api()
        self.test_cloud_vision_api()
        self.test_translate_api()
        self.test_speech_to_text_api()
        
        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        
        if self.working_apis:
            print(f"\n✅ Your API key works with {len(self.working_apis)} service(s):")
            for i, api in enumerate(self.working_apis, 1):
                print(f"   {i}. {api}")
            
            print("\n💡 RECOMMENDATION FOR YOUR INTERVIEW AI PROJECT:")
            if "Gemini (Generative AI)" in self.working_apis:
                print("   ✅ Perfect! You can use Gemini for the conversational AI")
                print("   ✅ This is ideal for RAG-based interview system")
            else:
                print("   ⚠️  You'll need to enable Gemini API for your interview AI")
                
        else:
            print("\n❌ No APIs are working with this key.")
            print("   This could mean:")
            print("   - The key is restricted to specific APIs not tested here")
            print("   - The key has been revoked")
            print("   - API services aren't enabled in your Google Cloud project")
        
        print("\n🔐 SECURITY REMINDER:")
        print("   ⚠️  REVOKE this key immediately (it was posted publicly!)")
        print("   ⚠️  Go to: https://console.cloud.google.com/apis/credentials")
        print("="*60)


# Main execution
if __name__ == "__main__":
    # Your API key (IMPORTANT: This should be kept secret!)
    API_KEY = "AIzaSyCDHWOfD9oP4BQMNsdep58wdo5HeWZdnUM"
    
    # Create tester and run all tests
    tester = GoogleAPITester(API_KEY)
    tester.run_all_tests()
    
    print("\n📚 Next Steps:")
    print("   1. Revoke this key immediately")
    print("   2. Create a new API key")
    print("   3. Enable the APIs you need for your project")
    print("   4. Never share API keys publicly again!")