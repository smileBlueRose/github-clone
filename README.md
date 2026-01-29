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