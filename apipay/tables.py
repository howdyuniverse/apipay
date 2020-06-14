from datetime import datetime
from datetime import timezone

import sqlalchemy as sa

metadata = sa.MetaData()


def get_current_datetime_with_tz() -> datetime:
    return datetime.now(timezone.utc)


account_table = sa.Table(
    'account', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('login', sa.String(256), nullable=False),
    sa.Column('password', sa.String(256), nullable=False),
    sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
)


transaction_table = sa.Table(
    'transaction', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column(
        'from_account', sa.Integer, sa.ForeignKey('account.id'), nullable=False,
    ),
    sa.Column(
        'to_account', sa.Integer, sa.ForeignKey('account.id'), nullable=False,
    ),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column(
        'created_at',
        sa.DateTime(timezone=True),
        nullable=False,
        default=get_current_datetime_with_tz,
    ),
)
