import typing as t
from decimal import Decimal, ROUND_HALF_UP

from aiopg.sa import SAConnection
from sqlalchemy import func
from psycopg2.extensions import TransactionRollbackError

from apipay.tables import account_table, transaction_table


class JsonResponseData(t.NamedTuple):
    status: int
    msg: str


async def select_one(conn: SAConnection, query: t.Any):
    result = await conn.execute(query)
    return await result.fetchone()


async def select_all(conn: SAConnection, query: t.Any):
    result = await conn.execute(query)
    return await result.fetchall()


async def balance_transaction(
    db_engine, sender_id: int, recipient_ids: t.List[int], amount_raw: float
) -> JsonResponseData:
    amount = Decimal(amount_raw).quantize(Decimal('.01'), ROUND_HALF_UP)
    sender_total_amount = amount * len(recipient_ids)
    print('sender_total_amount', sender_total_amount)
    async with db_engine.acquire() as conn:
        async with conn.begin(isolation_level='SERIALIZABLE'):
            if sender_id in recipient_ids:
                return JsonResponseData(400, 'sender_id in recipient_ids')
            sender_account_stmt = (
                account_table.select()
                .where(account_table.c.id == sender_id)
            )
            sender_account = await select_one(conn, sender_account_stmt)
            if not sender_account:
                return JsonResponseData(404, 'sender_account not found')

            if sender_account.balance < sender_total_amount:
                return JsonResponseData(403, 'not enough money')

            recipient_accounts_count_stmt = (
                account_table.select()
                .where(account_table.c.id.in_(recipient_ids))
            )
            recipient_accounts_count = await conn.scalar(
                account_table.select()
                .where(account_table.c.id.in_(recipient_ids))
            )
            if recipient_accounts_count != len(recipient_ids):
                return JsonResponseData(404, 'recipient_account not found')

            try:
                await conn.execute(
                    account_table.update(account_table.c.id == sender_id)
                    .values(balance=account_table.c.balance - sender_total_amount)
                )
                await conn.execute(
                    account_table.update(account_table.c.id.in_(recipient_ids))
                    .values(balance=account_table.c.balance + amount)
                )
            except TransactionRollbackError:
                print('TransactionRollbackError!')
                return JsonResponseData(500, 'TransactionRollbackError')

            transcations = [
                dict(
                    from_account=sender_id,
                    to_account=recipient_id,
                    amount=amount,
                )
                for recipient_id in recipient_ids
            ]
            await conn.execute(
                transaction_table.insert()
                .values(transcations)
            )
        return JsonResponseData(200, 'OK!')
