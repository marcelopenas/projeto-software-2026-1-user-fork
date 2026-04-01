# Instalação

Para rodar a aplicação basta executar:

python main.py

mas antes é necessário rodar o postgres e criar a tabela user.

### Configuração do postgres

Primeiro executar o Postgres no Docker

```
docker run -d --name postgres-users --network=rede -e POSTGRES_USER=appuser -e POSTGRES_PASSWORD=apppass -e POSTGRES_DB=postgres -p 5432:5432 postgres:16
```

Entrar no postgres e usar o psql
```
docker exec -it postgres-users psql -U appuser -d postgres
```

Criar o banco de dados users
```
CREATE DATABASE users;
```

Usar o banco de dados users
```
\c users
```

Criar a tabela users dentro do BD users

```
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE
);
```

Comandos úteis do PSQL

```
\c -> Muda o BD corrente
\l -> Lista os BDs que existem
\dt -> Lista tabelas do BD
```

### Execução com o Docker

Para executar a aplicação com o Docker

1 - Criar Dockerfile
2 - Lembrar de mudar o DNS do BD -> Linhas 6 do main.py
3 - Executar o comando docker build na raiz do projeto

```
docker build -t {nome_usuario_docker_hub}/app_users .
```

4 - Testar local

```
docker run -p 5000:5000 --network=rede --name app_users -d {nome_usuario_docker_hub}/app_users
```

5 - Subir para o DockerHub

```
docker push {nome_usuario_docker_hub}/app_users
```

6 - Executar na máquina da AWS o `docker run`. Lembre que a porta 5000 está bloqueada na AWS, tente usar a porta 80 -> 80:5000

## container

docker build . --file Dockerfile --tag marcelopenas/projeto-software-user:latest --no-cache

docker compose rm -f -v

## Exercício

Na rota de cadastro de usuário, deve ser adicionado o campo CEP e número da cada, com o CEP, deve ser feita uma consulta na API:

https://viacep.com.br/ws/{cep}/json/

No banco de dados deve ser salvo o endereço completo do usuário com os campos cep, logradouro,  bairro, localidade e cidade. Além do número que foi enviado pelo usuário.

```python
python3 -m pytest
```


``` python
python3 -m pytest --cov=main --cov-report=term-missing -s
```