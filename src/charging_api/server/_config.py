import os


SECURITY_CREDENTIALS = {
    "user": os.getenv("AUTH_USER", r"admin"),
    "password": os.getenv("AUTH_PW", r"^8wjt8dJ@M^?kvr5"),
}

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_DB", "stations"),
    "user": os.getenv("DB_USER", "docker"),
    "password": os.getenv("DB_PW", "docker"),
    "schema": os.getenv("DB_SCHEMA", "stations"),
}

SRID = os.getenv("SRID", 4326)
schema = DB_CONFIG.get("schema")
engine_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
connect_args = {"options": f"-c search_path={schema}"} if schema is not None else None
