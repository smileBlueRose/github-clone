A web application built with Python that replicates core GitHub functionality.

## Running the Project

### Linux

1. Clone the repository:
```bash
git clone https://github.com/smileBlueRose/github-clone/
cd github-clone
```

2. Create secret files from examples:
```bash
cd src/secrets
mv db_password.txt.example db_password.txt
mv jwt-private.pem.example jwt-private.pem
mv jwt-public.pem.example jwt-public.pem
cd ../..
```

3. Start the database:
```bash
sudo docker compose --env-file .env.template up -d
```

4. Install dependencies:
```bash
cd src
uv sync --all-extras
```

5. Run the application:
```bash
ENV=dev uv run main.py
```

### Windows

1. Clone the repository:
```cmd
git clone https://github.com/smileBlueRose/github-clone/
cd github-clone
```

2. Create secret files from examples:
```cmd
cd src\secrets
ren db_password.txt.example db_password.txt
ren jwt-private.pem.example jwt-private.pem
ren jwt-public.pem.example jwt-public.pem
cd ..\..
```

3. Start the database:
```cmd
docker compose --env-file .env.template up -d
```

4. Install dependencies:
```cmd
cd src
uv sync --all-extras
```

5. Run the application:
```cmd
set ENV=dev
uv run main.py
```

## Running Tests

### Linux

1. Create test secret files from examples:
```bash
cd tests/secrets
mv db_password.txt.example db_password.txt
mv another-private.pem.example another-private.pem
mv another-public.pem.example another-public.pem
mv test-private.pem.example test-private.pem
mv test-public.pem.example test-public.pem
cd ../..
```

2. Start the test database:
```cmd
docker compose -p github-clone-test --env-file .env.template --env-file .env.test up -d
```

3. Run tests:
```bash
ENV=test uv run pytest .
```

### Windows

1. Create test secret files from examples:
```cmd
cd tests\secrets
ren db_password.txt.example db_password.txt
ren another-private.pem.example another-private.pem
ren another-public.pem.example another-public.pem
ren test-private.pem.example test-private.pem
ren test-public.pem.example test-public.pem
cd ..\..
```

2. Start the test database:
```cmd
docker compose -p github-clone-test ^
  --env-file .env.template ^
  --env-file .env.test ^
  up -d
```

3. Run tests:
```cmd
set ENV=test
uv run pytest .
```