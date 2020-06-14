import typing as t
from decimal import Decimal

import jwt
import sqlalchemy as sa
from aiohttp import web

from passlib.hash import sha256_crypt
from apipay.tables import account_table


JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'


async def register_user(
    db_engine, login: str, raw_password: str
) -> t.Optional[str]:
    async with db_engine.acquire() as conn:
        res = await conn.execute(
            account_table.select()
            .where(account_table.c.login == login)
        )
        user = await res.fetchone()
        if user is not None:
            return None
        insert_stmt = await conn.execute(
            account_table.insert()
            .values(
                login=login,
                password=sha256_crypt.hash(raw_password),
                balance=Decimal('100.0'),
            )
            .returning(account_table.c.id)
        )
        inserted_user = await insert_stmt.fetchone()
        return get_jwt(inserted_user.id)


def get_jwt(user_id: int) -> str:
    return (
        jwt.encode({'user_id': user_id}, JWT_SECRET, JWT_ALGORITHM)
        .decode('utf-8')
    )


def get_user_id_from_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        return payload['user_id']
    except jwt.DecodeError:
        return None


async def user_login(
    db_engine, login: str, raw_password: str
) -> t.Optional[str]:
    async with db_engine.acquire() as conn:
        res = await conn.execute(
            account_table.select().where(account_table.c.login == login)
        )
        user = await res.fetchone()
        if user is not None:
            hashed = user.password
            if sha256_crypt.verify(raw_password, hashed):
                return get_jwt(user.id)
    return None


def login_required(func: t.Callable) -> t.Callable:
    def wrapper(request: web.Request) -> t.Callable:
        jwt_token = request.headers.get('authorization', None)
        if not jwt_token:
            return web.Response(status=401)
        try:
            jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.DecodeError:
            return web.Response(status=401)
        return func(request)
    return wrapper
