# Information der Datenbank:
postgres_host='postgres'
postgres_port='5432'
postgres_database = 'dsi_postgres'
postgres_user = 'postgres'
postgres_password = 'xxx'
postgres_connection_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(postgres_user, postgres_password, postgres_host, postgres_port, postgres_database)
postgres_jdbc_connection_string = 'jdbc:postgresql://{}:{}/{}'.format(postgres_host, postgres_port, postgres_database)
postgres_driver = 'org.postgresql.Driver'
postgres_driver_path = './postgresql-42.5.1.jar'

# API_Requests:
rapidAPI_Key = "xxx"
skyScanner_key = 'xxx'

# Informationen Spark:
spark_app_name = 'bookingAPI'
spark_master = 'local[1]'
#spark_master = 'spark://localhost:7077'

# Informationen kafka
kafka_bootstrap_server = 'kafka-container:29092'
kafka_topic_booking = 'bookingAPI'
kafka_topic_skyscanner = 'skyscannerAPI'
kafka_group_name = "projectGroup"

# Allgemeine Informationen
days_hotel = 7
days_to_add = 4
price_max_points = 70
review_max_points = 30
rdd = 0