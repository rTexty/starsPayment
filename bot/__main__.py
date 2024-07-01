import logging
from pathlib import Path

from .bot import bot, dispatcher
from .utils.other import set_commands
from . import middleware, routers, services
from .utils.paths import root_path, routers_path

@dispatcher.startup()
async def on_startup():

    dct_commands = {
        'ru': {
            'start': '🔄 Перезапустить бота',
            # 'friends': '🤝 Реферальная программа',
            'payment ': '💳 Оплата',
            'help ': '🧑‍💻 Помощь',
            
        },
    }

    await set_commands(bot, dct_commands)

    await services.setup(dispatcher)

    me = await bot.get_me()
    print(f'Бот запущен! {me.username}')


@dispatcher.shutdown()
async def on_shutdown():
    await services.dispose(dispatcher)

def import_routers(path: Path = routers_path, import_str: str = 'bot.routers.'):
    handler_file = sorted(
        path.glob("*"), key=lambda p: p.stem
    )

    for handler in handler_file:
        _import = import_str + handler.stem

        if not handler.is_file() and handler.stem.startswith("__") and handler.stem.endswith("__"):
            continue

        if handler.is_file():
            __import__(_import)
            continue

        import_routers(handler, _import + '.')


def main():
    log_filename = str((root_path / "logs.log").resolve())

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format=u'%(name)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    )

    logging.getLogger(__name__).setLevel(logging.INFO)

    middleware.setup(dispatcher)
    import_routers()
    dispatcher.include_router(routers.root_handlers_router)

    used_update_types = dispatcher.resolve_used_update_types()
    dispatcher.run_polling(bot, allowed_updates=used_update_types)


if __name__ == '__main__':
    main()
