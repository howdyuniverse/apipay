CREATE TABLE IF NOT EXISTS account
(
  id SERIAL NOT NULL,
  login CHARACTER VARYING(256) NOT NULL,
  password CHARACTER VARYING(256) NOT NULL,
  balance NUMERIC(10, 2) DEFAULT 0.0,
  CONSTRAINT user_pkey PRIMARY KEY (id),
  CONSTRAINT user_login_key UNIQUE (login)
);

CREATE TABLE IF NOT EXISTS transaction
(
  id SERIAL NOT NULL,
  from_account INTEGER REFERENCES account(id),
  to_account INTEGER REFERENCES account(id),
  amount NUMERIC(10, 2) NOT NULL,
  created_at TIMESTAMP without time zone NOT NULL DEFAULT (now() at time zone 'UTC'),
  CONSTRAINT transaction_pkey PRIMARY KEY (id)
);
