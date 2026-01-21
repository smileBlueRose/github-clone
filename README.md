# GitHub Clone

A web application built with Python that replicates core GitHub functionality.

## Prerequisites

- Git
- Docker & Docker Compose
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenSSL

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/smileBlueRose/github-clone/
cd github-clone
```

### 2. Set up environment variables

```bash
cp .env.template .env
nano .env  # Edit the configuration file
```

### 3. Update these three parameters in `.env`:
```env
APP_CONFIG__DB__PASSWORD_FILE=secrets/db_password.txt
APP_CONFIG__AUTH__JWT__PRIVATE_KEY_FILE_PATH=secrets/jwt-private.pem
APP_CONFIG__AUTH__JWT__PUBLIC_KEY_FILE_PATH=secrets/jwt-public.pem
```
### 3. Create secrets directory and files

```bash
cd src
mkdir secrets
cd secrets

# Create database password file
echo "your_secure_password" > db_password.txt

# Generate JWT keys
openssl genpkey -algorithm RSA -out jwt-private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in jwt-private.pem -out jwt-public.pem

cd ../..
```

### 4. Start the database

```bash
sudo docker compose up -d
```

### 5. Install Python dependencies

```bash
cd src
uv sync --all-extras
```

### 6. Run the application

```bash
ENV=default uv run main.py
```

The application will be available at `http://127.0.0.1:5000`

## Project Structure

```
github-clone/
├── src/
│   ├── secrets/
│   │   ├── db_password.txt
│   │   ├── jwt-private.pem
│   │   └── jwt-public.pem
│   └── main.py
├── tests/
├── .env
├── compose.yml
└── pyproject.toml
```

## Postman documentation:
### [Link to collection](https://starthub-4052.postman.co/workspace/My-Workspace~479f13d7-0f5c-4e1b-884a-66da29cd1ea3/collection/43041877-55ec369d-232f-4fe8-9da0-0647f156f39f?action=share&creator=43041877)