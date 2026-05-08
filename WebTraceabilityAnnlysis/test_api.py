import sys
import json
import urllib.request
import urllib.error

COZE_API_URL = "https://4p9tqrwrxp.coze.site/stream_run"
COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjBkYzU5M2IxLTNmYWUtNGM2NC1hYTJhLTc3MzgzMjQ0MzM2MSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlVJSXRRTWlOdlA3RGVoN2k2b3ZtcWY1dk9rd1ZYWHZJIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc3Nzk3NTAyLCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjM1NTcwMjE1MTA2OTA0MDY0Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjM1NTgyMTMyNDgzNTIyNjAyIn0.YhrF7AvMyR6-F1gc74MpO3Gjmyg5w5HI8_VfflUt0ytuQhUa7Yo8IrQwCLryjdAYdyDBRHQW26WSv1DZnU_BuT9SXgsYL-SYhFdq8d2KBizCmBm_3Y-4GTQal4ksJwfbQa3osUfJzFJp0fst_QFC-WuKtEw8ds4Id1AyyWVI9HUAXP8MRGs_Pnj9UlrJkpYh_6DM1jo_E0VmdVNAOHdw45D7BwN1YtxlAoVbG_KMY2W7nncaF8_HebL-M_P-RA_bxk65r39P-Jb5dzMb6kXJmLTufwFJ70qCP0l_Eq70nIeXoEwEtIexmya2eTUKzlR2utaY8cqlLzS9BXME3Es7zA"
PROJECT_ID = "7635556815685730339"

def main():
    print("===== Ocean Waste Trace Analysis - API Test =====")
    
    payload = {
        "content": {
            "query": {
                "prompt": [
                    {
                        "type": "text",
                        "content": {
                            "text": "You are a marine waste traceability expert. Please analyze: the image shows a Red Bull beverage can. Analyze its features, source, and diffusion path."
                        }
                    }
                ]
            }
        },
        "type": "query",
        "session_id": "test-session-" + str(hash(str(sys.argv))),
        "project_id": PROJECT_ID
    }
    
    headers = {
        "Authorization": "Bearer " + COZE_TOKEN,
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    try:
        req = urllib.request.Request(COZE_API_URL, json.dumps(payload).encode('utf-8'), headers)
        print("Calling Coze API...")
        
        with urllib.request.urlopen(req, timeout=60) as response:
            print("HTTP Status: " + str(response.status))
            print("\nResponse Content:")
            while True:
                line = response.readline()
                if not line:
                    break
                print(line.decode('utf-8').strip())
                
    except urllib.error.HTTPError as e:
        print("HTTP Error: " + str(e.code))
        print("Error Message: " + e.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print("URL Error: " + str(e.reason))
    except Exception as e:
        print("Unknown Error: " + str(e))

if __name__ == "__main__":
    main()
