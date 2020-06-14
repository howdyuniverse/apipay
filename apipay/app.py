from aiohttp import web

from apipay import db
from apipay import signals
from apipay.auth import (
    get_jwt,
    get_user_id_from_jwt,
    register_user,
    user_login,
    login_required,
)


async def handler_root(request: web.Request) -> web.Response:
    return web.Response(text=f'Hello', content_type='text/html')


# curl -D - -d '{"login":"alice", "password":"alice"}' -H "Content-Type: application/json" -X POST http://localhost:8000/register
async def handle_register(request: web.Request) -> web.Response:
    post_data = await request.json()
    login = post_data.get('login')
    password = post_data.get('password')
    if not (login and password):
        return web.Response(status=400)
    token = await register_user(request.app.db_engine, login, password)
    if token is None:
        return web.Response(status=409)
    return web.json_response({'token': token})


# curl -D - -d '{"login":"alice", "password":"alice"}' -H "Content-Type: application/json" -X POST http://localhost:8000/login
async def handle_login(request: web.Request) -> web.Response:
    post_data = await request.json()
    login = post_data.get('login')
    password = post_data.get('password')
    token = await user_login(request.app.db_engine, login, password)
    if token is None:
        return web.HTTPUnauthorized(body=b'Invalid username/password combination')
    return web.json_response({'token': token})


# curl -D - -d '{"recipient_ids": [3, 1], "amount": 1.01}' -H "authorization: TOKEN" -X POST http://localhost:8000/deal
@login_required
async def handle_deal(request: web.Request) -> web.Response:
    post_data = await request.json()

    try:
        recipient_ids = [int(rid) for rid  in post_data.get('recipient_ids')]
    except ValueError:
        return web.json_response(dict(msg='invalid recipient_ids'), status=400)

    amount_raw = post_data.get('amount')
    token = request.headers.get('authorization', None)
    sender_id = get_user_id_from_jwt(token)
    response_data = await db.balance_transaction(
        request.app.db_engine, sender_id, recipient_ids, amount_raw
    )
    return web.json_response(
        dict(msg=response_data.msg, status=response_data.status)
    )


async def create_app() -> web.Application:
    app = web.Application(debug=True)

    app.cleanup_ctx.extend([
        signals.connect_db,
    ])

    app.router.add_route('GET', '/', handler_root)
    app.router.add_route('POST', '/register', handle_register)
    app.router.add_route('POST', '/login', handle_login)
    app.router.add_route('POST', '/deal', handle_deal)
    return app


def run_app(app: web.Application) -> None:
    web.run_app(app, host='0.0.0.0', port=8000)


def main() -> None:
    app = create_app()
    run_app(app)
