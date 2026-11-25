from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Connection, create_engine, text
from sqlalchemy.engine import URL, make_url
from config import BASE_QUERY, DATE_COLUMN, END_DATE, SOURCE1, SOURCE2, START_DATE

@contextmanager
def connect(source_config: dict) -> Iterator[Connection]:
    """Open a database connection, optionally forwarding it through SSH."""
    database_url: URL = make_url(source_config["URL"])
    tunnel = None
    engine = None

    try:
        if source_config["USE_SSH"]:
            if not database_url.host or not database_url.port:
                raise ValueError("An SSH connection requires a database URL with host and port")

            from sshtunnel import SSHTunnelForwarder

            ssh_config = source_config["SSH_CONFIG"]
            ssh_host = ssh_config["HOST"]
            ssh_username = ssh_config["USERNAME"]
            if not ssh_host or not ssh_username:
                raise ValueError("SSH_CONFIG must include HOST and USERNAME")

            ssh_options = {}
            if source_config["USE_KEY"]:
                key_path = ssh_config["KEY_PATH"]
                if not key_path.is_file():
                    raise FileNotFoundError(f"SSH private key not found: {key_path}")
                ssh_options["ssh_pkey"] = str(key_path)
            else:
                ssh_password = ssh_config["PASSWORD"]
                if not ssh_password:
                    raise ValueError("SSH_CONFIG must include PASSWORD when USE_KEY is False")
                ssh_options["ssh_password"] = ssh_password

            tunnel = SSHTunnelForwarder(
                (ssh_host, ssh_config["PORT"]),
                ssh_username=ssh_username,
                remote_bind_address=(database_url.host, database_url.port),
                local_bind_address=("127.0.0.1", 0),
                **ssh_options,
            )
            tunnel.start()
            database_url = database_url.set(
                host="127.0.0.1", port=tunnel.local_bind_port
            )

        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            yield connection
    finally:
        if engine is not None:
            engine.dispose()
        if tunnel is not None:
            tunnel.stop()


def select_value(connection: Connection, sql: str) -> str:
    """Execute a single-aggregation query and return its first value as text."""
    sql = sql.format(
        base_query=BASE_QUERY,
        date_filter=f"{DATE_COLUMN} BETWEEN '{START_DATE}' AND '{END_DATE}'",
        start_date=START_DATE,
        end_date=END_DATE,
    )
    sql = sql.format(
            date_filter=f"{DATE_COLUMN} BETWEEN '{START_DATE}' AND '{END_DATE}'",
        )
    value = connection.execute(text(sql)).scalar()
    return str(value)