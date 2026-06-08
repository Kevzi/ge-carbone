from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("ALTER EXTENSION pg_trgm SET SCHEMA public;")
    print("pg_trgm moved to public schema.")
