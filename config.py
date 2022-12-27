postgres_host='localhost'
postgres_port='5432'
postgres_database = 'dsi_postgres'
postgres_user = 'postgres'
postgres_password = 'DSIholiday'
postgres_connection_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(postgres_user, postgres_password, postgres_host, postgres_port, postgres_database)