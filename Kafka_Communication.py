from kafka import KafkaProducer
from kafka import KafkaConsumer
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
import pandas as pd
from json import dumps
from json import loads
import config


# SEND TO KAFKA
def kafka_send(data, topic_name):
    counter = 0
    
    producer = KafkaProducer(
        bootstrap_servers=config.kafka_bootstrap_server,
        api_version=(0,11,5),
        value_serializer=lambda x:dumps(x).encode('utf-8'))
    
    for row in data.to_dict(orient='records'):
        producer.send(topic_name, row)
        counter+=1
        
    print('{} rows sent to {} topic.'.format(counter, topic_name))
    producer.close()

# RECEIVE FROM KAFKA
def kafka_receive(topic_name):
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=config.kafka_bootstrap_server,
        auto_offset_reset='earliest',
        consumer_timeout_ms=1000,
        auto_commit_interval_ms=1000,
        #group_id=config.kafka_group_name,
        api_version=(0,11,5),
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )
    
    dat = pd.DataFrame()
    counter = 0
    
    for message in consumer:
        dat = pd.concat([dat, pd.DataFrame([message.value])], ignore_index=True)
        counter+=1
    
    print('{} rows reveived from {} topic.'.format(counter, topic_name))
    consumer.close()
    return dat