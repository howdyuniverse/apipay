## Запуск

docker-compose up --build


## Коннект к базе

docker exec -it apipay_postgres psql apipay -U postgres


## API

### Регистрация

```bash
curl -D - -d '{"login":"alice", "password":"alice"}' -H "Content-Type: application/json" -X POST http://localhost:8000/register
```

### Логин

```bash
curl -D - -d '{"login":"alice", "password":"alice"}' -H "Content-Type: application/json" -X POST http://localhost:8000/login
```

### Перевод средств

```bash
curl -D - -d '{"recipient_ids": [3, 1], "amount": 1.01}' -H "authorization: TOKEN" -X POST http://localhost:8000/deal
```
