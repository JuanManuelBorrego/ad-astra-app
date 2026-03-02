import os
from libsql_client import create_client

# Cliente global
client = create_client(
    url=os.environ["TURSO_DATABASE_URL"],
    auth_token=os.environ["TURSO_AUTH_TOKEN"]
)

def query(sql, params=None):
    if params:
        result = client.execute(sql, params)
    else:
        result = client.execute(sql)

    return result.rows


def execute(sql, params=None):
    if params:
        client.execute(sql, params)
    else:
        client.execute(sql)
