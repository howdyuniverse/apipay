import time
import base64

from aiopg.sa import create_engine


async def connect_db(app):
    while True:
        try:
            db_engine = await create_engine(
                user='postgres',
                password='postgres',
                database='apipay',
                host='database',
            )
        except:
            print('retry connect db...')
            time.sleep(1)
        else:
            break
    app.db_engine = db_engine
    print('Connected to database')

    yield

    app.db_engine.close()
    await app.db_engine.wait_closed()
    print('Disconnected to database')
