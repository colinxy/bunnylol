from sqlalchemy.schema import CreateTable


async def table_exists(connection, table):
    # TODO: check is table exists
    return True


async def create_tables(engine, tables):
    async with engine.acquire() as conn:
        for t in tables:
            if await table_exists(conn, t):
                continue
            create_sql = str(CreateTable(t).compile(engine))
            await conn.execute(create_sql)
