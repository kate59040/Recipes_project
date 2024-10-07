import asyncio
import logging
import os

import requests
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from dotenv import load_dotenv

router = Router()

load_dotenv('os.env')

logging.basicConfig(level=logging.INFO)

api_id = os.getenv('API_ID')
api_key = os.getenv('API_KEY')


@router.message(Command(commands=['start']))
async def start(message: types.Message):
    response = (
        "Привет! Отправь мне продукты, которые ты хочешь видеть в рецепте и продукты, "
        "которые ты не любишь или просто не хочешь добавлять в блюдо.\n"
        "Также вы можете выбрать варианты диетического питания.\n\nВозможные варианты:\n"
        "balanced, high-fiber, high-protein, low-carb, low-fat, low-sodium\n\n"
        "Напишите то, что требуется в следующем порядке: в первой строке желаемые продукты, "
        "во второй те, которые нужно исключить и в третьей вариант питания\n\n"
        "Примеры: \nTomato, potato\nMeet\nhigh-fiber, balanced\n\n"
        "\nNone\nNone\nhigh-protein")
    await message.reply(response)


@router.message()
async def process_products(message: types.Message):
    products = message.text.lower().split('\n')
    try:
        user_products = [product.strip() for product in products[0].split(',')]
        excluded_products = [product.strip() for product in products[1].split(',')]
        diet_type = [product.strip() for product in products[2].split(',')]

    except IndexError:
        await message.reply('Вы не указали один из параметров')
        return

    # Запрос к api
    url = 'https://api.edamam.com/api/recipes/v2'   # поделить на 3 функции
    params = {
        'type': 'public',
        'app_id': api_id,
        'app_key': api_key,
        'q': ','.join(user_products),
        'excluded': ','.join(excluded_products),
        'diet': diet_type
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        for recipe in data['hits']:
            recipe_data = recipe['recipe']
            recipe_text = f"Название рецепта: {recipe_data['label']}\n"
            recipe_text += f"Приготовление: {recipe_data['url']}\n"
            recipe_text += f"Калории: {recipe_data['calories']:.2f} ккал\n"
            recipe_text += "Ингредиенты:\n"

            for ingredient in recipe_data['ingredientLines']:
                recipe_text += f"- {ingredient}\n"

            await message.reply(recipe_text)
    else:
        await message.reply("Произошла ошибка при получении рецептов. Попробуйте еще раз.")


async def main():
    bot_token = os.getenv('BOT_TOKEN')
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
