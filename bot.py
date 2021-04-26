import discord
from discord.ext import commands
import requests
import random
from random import randint
import youtube_dl
import os
import PIL
from PIL import Image, ImageDraw
import time
import json
import asyncio


bot = commands.Bot(command_prefix='$')
TOKEN = "ODM0NTI2Nzg1MjY1ODYwNjU4.YICLog.Fo8OmFJ5CcgZ9cGodrR5V-VAywk"

first_player = ""
second_player = ""
turn = ""
game_over = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

INFO = open('info.md', 'r', encoding='utf-8')
INFOTEXT = INFO.read()
INFO.close()

@bot.event
async def on_ready():
    print('Test-bot 0.1')
    print('Logged in as: ' + bot.user.name)
    print('Client User ID: ' + str(bot.user.id))


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def cat(ctx):
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    data = response.json()
    await ctx.send(data[0]['url'])


@bot.command()
async def something(ctx):
    '''
    Случайна фраза Шрека
    '''
    somethings = [
        'Somebody once told me the world was gonna roll me.',
        'I ain\'t the sharpest tool in the shed.',
        'WHAT ARE YOU DOING IN MY SWAMP?!',
        'Shrek is love, Shrek is life.']
    await ctx.send(random.choice(somethings))


@bot.command()
async def dog(ctx):
    response = requests.get('https://dog.ceo/api/breeds/image/random')
    data = response.json()
    await ctx.send(data['message'])


@bot.command()
async def play(ctx, url: str):
    '''
    Проигрывание аудиодорожки с использование youtube
    '''
    song = os.path.isfile('song.webm')
    try:
        if song:
            os.remove('song.webm')
    except PermissionError:
        await ctx.send('Дождитесь окончания текущий аудиодорожки, или используйте команду $stop')
        return

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='Основной')
    await voiceChannel.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    ydl_opts ={
        'format': '249/250/251',
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'webm',
        'preferredquality': '192',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".webm"):
            os.rename(file, "song.webm")
    voice.play(discord.FFmpegOpusAudio("song.webm"))


@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send('Бот не подключен к звуковым каналам')


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('Аудиодорожки не проигрываются')


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('Аудиодорожки проигрываются')


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@bot.command()
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
    '''
    Игра в крестики нолики
    '''
    global count
    global first_player
    global second_player
    global turn
    global game_over

    if game_over:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        game_over = False
        count = 0

        first_player = p1
        second_player = p2

        # создание доски
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # выбор начинающего игрока
        num = random.randint(1, 2)
        if num == 1:
            turn = first_player
            await ctx.send("Сейчас ход игрока <@" + str(first_player.id) + ">")
        elif num == 2:
            turn = second_player
            await ctx.send("Сейчас ход игрока <@" + str(first_player.id) + ">")
    else:
        await ctx.send("Игра в самом разгаре! Закончите ее, прежде чем начинать новую")


@bot.command()
async def pose(ctx, pos: int):
    global turn
    global first_player
    global second_player
    global board
    global count
    global game_over

    if not game_over:
        mark = ""
        if turn == ctx.author:
            if turn == first_player:
                mark = ":regional_indicator_x:"
            elif turn == second_player:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
                board[pos - 1] = mark
                count += 1

                # создание доски
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if game_over:
                    await ctx.send(mark + " победили!")
                elif count >= 9:
                    game_over = True
                    await ctx.send("Ничья!")

                # смена сторон
                if turn == first_player:
                    turn = second_player
                elif turn == second_player:
                    turn = first_player
            else:
                await ctx.send("Выбирайте числа между 1 и 9 и выбирайте только неотмеченные клетки")
        else:
            await ctx.send("Сейчас не твой ход")
    else:
        await ctx.send("Пожалуйста, начните новую игру, прописав команду $tictactoe в чат")


def checkWinner(winningConditions, mark):
    global game_over
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            game_over = True


@tictactoe.error
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Пожалуйста, отметьте 2 игроков.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Пожалуйста, убедитесь, что вы отметили игроков (ie. <@834526785265860658>).")


@pose.error
async def pose_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Пожалуйста, выберите клетку, которую хотите отметить")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Пожалуйста, убедитесь, что вы ввели число")


# Обработка фото
def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        print('DELETE ERROR')


def mask_circle_transparent(pil_img, offset=0):
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)

    result = pil_img.copy()
    result.putalpha(mask)

    return result


def process_image(url):
    img_data = requests.get(url).content
    time.sleep(2)
    with open('./images/temp.jpg', 'wb') as handler:
        handler.write(img_data)

    original = Image.open('./images/temp.jpg').convert('RGBA')
    wm = Image.open('wm.png').convert('RGBA')
    width, height = original.size
    mark_width, mark_height = wm.size

    smaller = height if height < width else width

    new_width = int(smaller / 8)
    percent = (new_width / float(mark_width))
    new_height = int(float(mark_height) * float(percent))
    wm = wm.resize((new_width, new_height), PIL.Image.ANTIALIAS)

    wm.putalpha(90)
    wm2 = mask_circle_transparent(wm)

    trans = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    trans.paste(original, (0, 0))
    trans.paste(wm, (int(smaller/1.25), int(smaller/1.25)), mask=wm2)
    trans.save('./images/out.png')

    delete_file('./images/temp.jpg')


@bot.command()
async def watermark(ctx, message):
    '''
    Добавление "вотермарки" на фотографию(исключительно url формат!!!)
    '''
    process_image(message)
    f = discord.File('./images/out.png')
    await ctx.send(content=('Sent by ' + ctx.author.display_name), file=f)
    delete_file('./images/out.png')


@bot.command()
async def pokemon(ctx, *, args):
    '''
    Таблица с искомым покемоном
    '''
    pokeName = args.lower()
    try:
        request = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokeName}')
        packages_json = request.json()
        packages_json.keys()

        PokEmb = discord.Embed(title="Pokemon", color=0xff0000)
        PokEmb.add_field(name="Name", value=packages_json['name'], inline=True)
        PokEmb.add_field(name="Pokedex Order", value=packages_json['order'], inline=True)
        PokEmb.set_thumbnail(url=packages_json['sprites']['back_default'])
        PokEmb.set_thumbnail(url=f'https://play.pokemonshowdown.com/sprites/ani/{pokeName}.gif')
        PokEmb.add_field(name="Weight", value=packages_json['weight'], inline=True)
        PokEmb.add_field(name="Height", value=packages_json['height'], inline=True)
        PokEmb.add_field(name="XP Base", value=packages_json['base_experience'], inline=True)
        for type in packages_json['types']:
            PokEmb.add_field(name="Types", value=type['type']['name'], inline=True)
        PokEmb.set_footer(text="Thx PokeApi!")
        await ctx.send(embed=PokEmb)
    except:
        await ctx.send("Покемон не найден :(")



# игра в города(россии)
def parse_city_json(json_file='russia.json'):
    p_obj = None
    try:
        js_obj = open(json_file, "r", encoding="utf-8")
        p_obj = json.load(js_obj)
    except Exception as err:
        print(err)
        return None
    finally:
        js_obj.close()
    return [city['city'].lower() for city in p_obj]


def get_city(city):
    normilize_city = city.strip().lower()
    if is_correct_city_name(normilize_city):
        if get_city.previous_city != "" and normilize_city[0] != get_city.previous_city[-1]:
            return 'Город должен начинаться на "{0}"!'.format(get_city.previous_city[-1])

        if normilize_city not in cities_already_named:
            cities_already_named.add(normilize_city)
            last_latter_city = normilize_city[-1]
            proposed_names = list(filter(lambda x: x[0] == last_latter_city, cities))
            if proposed_names:
                for i in proposed_names:
                    if i not in cities_already_named:
                        cities_already_named.add(i)
                        get_city.previous_city = i
                        return i.capitalize()
            return 'Я не знаю города на эту букву. Ты выиграл'
        else:
            return 'Город уже был. Повторите попытку'
    else:
        return 'Некорректное название города. Повторите попытку'


get_city.previous_city = ""


def is_correct_city_name(city):
    return city[-1].isalpha() and city[-1] not in ('ь', 'ъ')


def refresh():
    cities = parse_city_json()[:1000]
    cities_already_named = set()


@bot.command()
async def refresh(ctx):
    await refresh()


@bot.command()
async def city(ctx, message):
    '''
    Игра в города
    '''
    response = get_city(message)
    await ctx.send(response)


cities = parse_city_json()[:1000]  # города которые знает бот
cities_already_named = set()  # города, которые уже называли


@bot.command()
async def guess(ctx):
    '''
    Игра в угадайку
    '''
    await ctx.send('Угадайте число между 1 и 10')

    def is_correct(m):
        return m.author == ctx.author and m.content.isdigit()

    answer = random.randint(1, 10)

    try:
        guess = await bot.wait_for('message', check=is_correct, timeout=5.0)
    except asyncio.TimeoutError:
        return await ctx.send(f'Извините, ваше время вышло, правильный ответ: {answer}')

    if int(guess.content) == answer:
        await ctx.send('Вы угадали!')
    else:
        await ctx.send(f'Ой, не угадали, правильный ответ: {answer}')


@bot.command()
async def timer(ctx, seconds):
    '''
    Создает таймер не дольше 300 секунд
    '''
    try:
        secondint = int(seconds)
        if secondint > 300:
            await ctx.send("Я не могу ставить таймер дальше, чем на 300 секунд :(")
            raise BaseException
        if secondint <= 0:
            await ctx.send("Я не могу ставить таймеры в прошлом :(")
            raise BaseException
        message = await ctx.send(":alarm_clock: Таймер: {seconds} :alarm_clock: ")
        while True:
            secondint -= 1
            if secondint == 0:
                await message.edit(content=":alarm_clock: Время! :alarm_clock: ")
                break
            await message.edit(content=f":alarm_clock: Таймер: {secondint}")
            await asyncio.sleep(1)
        await ctx.send(f":alarm_clock:  {ctx.author.mention} Ваш отсчет закончен! :alarm_clock: ")
    except ValueError:
        await ctx.send("Должно быть число!")


@bot.command()
async def kill(ctx, *, user='You'):
    '''
    УБивает человека в стиле майнкрафта
    '''
    await ctx.send((user) + ' выпал за пределы мира')


@bot.command()
async def choose(ctx, *choices: str):
    '''
    Случайно выбирает из предложенных вариантов
    '''
    await ctx.send((random.choice(choices)) + ', я выбираю тебя!')


@bot.command()
async def dice(ctx, number=6):
    '''
    Выбирает между числами от 1 и до number
    '''
    await ctx.send("Вам выпало __**{}**__!".format(randint(1, number)))


@bot.command()
async def clone(ctx, *, message):
    '''
    Создает копию вашего сообщения, точь в точь
    '''
    pfp = requests.get(ctx.author.avatar_url_as(format='png', size=256)).content
    hook = await ctx.channel.create_webhook(name=ctx.author.display_name,
                                            avatar=pfp)

    await hook.send(message)
    await hook.delete()


@bot.command()
async def info(ctx):
    '''
    Выводит все доступные команды
    '''
    await ctx.send(INFOTEXT)


bot.run(TOKEN)
