import logging

from sqlalchemy import text

from src.database import async_session_maker


async def check_connection_db():
    try:
        async with async_session_maker() as session:
            engine = session.get_bind()
            db_info = {
                "host": engine.url.host,
                "port": engine.url.port,
                "database": engine.url.database,
            }

            await session.execute(text("SELECT 1"))
            await session.commit()

            logging.info(
                f"✅ Database connection successful\n"
                f"   Host: {db_info['host']}:{db_info['port']}\n"
                f"   Database: {db_info['database']}\n"
            )
            return True

    except Exception as e:
        logging.error(
            f"❌ Database connection failed\n"
            f"   Host: {db_info.get('host', 'unknown')}:{db_info.get('port', 'unknown')}\n"
            f"   Error: {e}"
        )
        return False
