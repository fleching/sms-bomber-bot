#!/usr/bin/env python3
"""
Test de todas las APIs para ver cuales funcionan
"""
import requests
import uuid
import urllib3
urllib3.disable_warnings()

# Numero de prueba (cambia por el tuyo)
PHONE = "+34722217943"

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
})

def test_api(name, url, data, headers=None):
    try:
        if headers:
            resp = session.post(url, json=data, headers=headers, timeout=10)
        else:
            resp = session.post(url, json=data, timeout=10)

        status = resp.status_code
        text = resp.text[:100] if resp.text else ""

        if status in [200, 201, 202]:
            print(f"[OK]   {name}: {status} - {text}")
            return True
        else:
            print(f"[FAIL] {name}: {status} - {text}")
            return False
    except Exception as e:
        print(f"[ERR]  {name}: {str(e)[:50]}")
        return False

print("="*60)
print(f"PROBANDO APIs CON: {PHONE}")
print("="*60)
print()

results = {"ok": 0, "fail": 0}

# ESPANA
print("--- ESPANA ---")
if test_api("Glovo", "https://api.glovoapp.com/v3/auth/phone", {"phone": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Glovo V2", "https://api.glovoapp.com/v0/identity/flow/start_verification",
    {"identityValue": {"phoneNumber": PHONE}, "identityType": "PHONE_NUMBER", "identityMetadata": {"selectedVerificationMethod": "SMS"}},
    {"Glovo-App-Platform": "web", "Glovo-App-Type": "customer", "Glovo-Api-Version": "14"}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("JustEat", "https://es.just-eat.es/api/v1/account/register", {"phone": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Cabify", "https://cabify.com/api/mobile/v3/auth/request-otp", {"phone_number": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Bolt Simple", "https://user.bolt.eu/user/register/phone", {"phone": PHONE, "country": "es"}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("FreeNow", "https://api.free-now.com/auth/phone", {"phoneNumber": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Wallapop", "https://api.wallapop.com/api/v3/users/phone-verification", {"phone": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

# INTERNACIONALES
print()
print("--- INTERNACIONALES ---")

if test_api("Telegram", "https://my.telegram.org/auth/send_password", {"phone": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Instagram", "https://i.instagram.com/api/v1/accounts/send_sms_code/",
    {"phone_number": PHONE}, {"User-Agent": "Instagram 219.0.0.12.117 Android"}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("TikTok", "https://www.tiktok.com/api/passport/web/send_code/", {"mobile": PHONE, "type": "register"}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Uber", "https://cn-geo1.uber.com/rt/silk-screen/sign-up", {"phoneNumber": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Tinder", "https://api.gotinder.com/v2/auth/sms/send", {"phone_number": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Bumble", "https://api.bumble.com/mwebapi.pyi", {"phone": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("PayPal", "https://www.paypal.com/signin/api/challenge/sms", {"phone": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Binance", "https://www.binance.com/bapi/accounts/v1/protect/account/mobile/sendMobileVerifyCode", {"mobile": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Airbnb", "https://api.airbnb.com/v2/phone_verify", {"phone": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

if test_api("Spotify", "https://www.spotify.com/api/account/sms", {"phone": PHONE}):
    results["ok"] += 1
else:
    results["fail"] += 1

print()
print("="*60)
print(f"RESULTADO: {results['ok']} funcionan, {results['fail']} fallan")
print("="*60)
