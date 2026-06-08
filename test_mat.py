import requests
import sys

def run():
    print("Testing locally to backend...")
    res = requests.post("http://localhost:8000/api/v1/auth/login/", json={"username":"admin", "password":"password123!"})
    if res.status_code != 200:
        res = requests.post("http://localhost:8000/api/v1/auth/login/", json={"username":"admin", "password":"admin123!"})
        if res.status_code != 200:
            print("Login failed:", res.status_code, res.text)
            return

    token = res.json().get("access")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    res = requests.get("http://localhost:8000/api/v1/reports/", headers=headers)
    reports = res.json()
    if not reports:
        print("No reports")
        return
    if isinstance(reports, dict) and "results" in reports:
        reports = reports["results"]
    elif isinstance(reports, dict):
        print("Reports error:", reports)
        return
        
    if not reports:
        print("Empty reports array")
        return
        
    report_id = reports[0]["id"]
    
    res = requests.post(f"http://localhost:8000/api/v1/reports/{report_id}/materiality-assessment/", 
                        headers=headers, json={"data": {"E1_1": 2}})
    print("POST res:", res.status_code, res.text)
    
    res = requests.patch(f"http://localhost:8000/api/v1/reports/{report_id}/materiality-assessment/", 
                         headers=headers, json={"data": {"E1_1": 3}})
    print("PATCH res:", res.status_code, res.text)

if __name__ == "__main__":
    run()
