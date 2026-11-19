# SMS Bomber Discord Bot

Bot de Discord para enviar SMS de verificacion a un numero.

## Comandos
- `/bomb +34XXXXXXXXX 50` - Enviar 50 SMS al numero
- `/services` - Ver servicios disponibles
- `/help` - Ver ayuda

## Servicios Activos
- **Glovo** (verificado)
- **Bolt** (verificado - 2 pasos)
- Cabify, Uber, Wallapop, Tinder, Vinted, Getir, Deliveroo, JustEat, Bumble (por verificar)

## Deploy en Railway (GRATIS)

### Opcion 1: Desde GitHub
1. Sube este repo a tu GitHub
2. Ve a [railway.app](https://railway.app)
3. Click "New Project" -> "Deploy from GitHub repo"
4. Selecciona el repo
5. En Variables, añade: `DISCORD_TOKEN` = tu token
6. Deploy automatico!

### Opcion 2: Desde CLI
```bash
npm install -g @railway/cli
railway login
railway init
railway up
railway variables set DISCORD_TOKEN=tu_token_aqui
```

## Variables de Entorno
| Variable | Descripcion |
|----------|-------------|
| DISCORD_TOKEN | Token del bot de Discord |
