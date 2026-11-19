import requests
import uuid
import urllib3
urllib3.disable_warnings()

phone = "+34722217943"

print("Probando Bolt API...")
print("="*50)

# PASO 1
url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
params = {"version": "HP.24.33", "device_name": "HP", "device_os_version": "web", "deviceId": "web", "deviceType": "web", "language": "es-es"}
headers1 = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json", "Origin": "https://bolt.eu", "Referer": "https://bolt.eu/"}
data1 = {"email": f"test{uuid.uuid4().hex[:8]}@gmail.com", "phone": phone, "city_id": 1617, "terms_consent_accepted": 1}

print(f"Paso 1: startRegistration")
print(f"Email: {data1['email']}")
resp1 = requests.post(url1, params=params, headers=headers1, json=data1, timeout=15, verify=False)
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text[:500]}")

if resp1.status_code == 200:
    resp1_json = resp1.json()
    if resp1_json.get("code") == 0:
        token = resp1_json["data"]["token"]
        print(f"\nToken obtenido: {token[:30]}...")

        # PASO 2
        print(f"\nPaso 2: startVerification")
        url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
        headers2 = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "Accept": "application/json", "Origin": "https://signup.bolt.eu", "Referer": "https://signup.bolt.eu/"}
        data2 = {"token": token, "verification_code_channel": "sms", "device_os_version": "web", "device_name": "Mozilla/5.0", "deviceId": str(uuid.uuid4()), "device_type": "web", "version": "DR.3.90", "language": "es-es", "visitor_id": f"visitor-driver-{uuid.uuid4()}"}

        resp2 = requests.post(url2, headers=headers2, json=data2, timeout=15, verify=False)
        print(f"Status: {resp2.status_code}")
        print(f"Response: {resp2.text[:500]}")
    else:
        print(f"Error en paso 1: {resp1_json}")
else:
    print("Fallo en paso 1")
