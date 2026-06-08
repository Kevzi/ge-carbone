from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT extname, extnamespace::regnamespace FROM pg_extension WHERE extname = 'pg_trgm';")
    row = cursor.fetchone()
    print("pg_trgm installed in:", row)
    
    cursor.execute("SHOW search_path;")
    print("search_path:", cursor.fetchone())
