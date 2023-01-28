import pyspark
import config
import datetime
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import isnan, count, when, col, desc, udf, col, sort_array, asc, avg, collect_list, rank
from pyspark.sql.functions import sum as Fsum
from pyspark.sql.functions import min as Fmin
from pyspark.sql.functions import max as Fmax
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.window import Window
from sqlalchemy import create_engine

# GENERAL FUNCTION
def transform_booking_inSpark(spark, data):
    sparkData = map_DF_to_Spark(spark, data)
    table = get_max_min_values(sparkData)
    sparkData = get_pointed_data(sparkData, table)
    sparkData = get_top3_data(sparkData)
    return sparkData.toPandas()
    
# CREATE REFERENCE TABLE FOR EACH CITY/DAY.
# This table is used in the subsequent functions as look up.
# Table has for hotels with prices in EUR, the min and max price, the min and max review, and the ranges they have.
def get_max_min_values(dat):
    max_min_values = dat.filter(col("currencycode") == "EUR") \
    .groupBy(col("city_trans").alias("city_trans_v"), col("checkin_date").alias("checkin_date_v"))\
    .agg(Fmax("price_per_day").alias("max_price"),
         Fmin("price_per_day").alias("min_price"),
        Fmax("review_score").alias("max_review"),
        Fmin("review_score").alias("min_review")) \
    .withColumn("diff_price", col("max_price")-col("min_price")) \
    .withColumn("diff_review", col("max_review")-col("min_review"))
    return max_min_values

# GENERATE A RATING FOR EVERY HOTEL
# Create a rating of the hotels based on: 70% price and 30% rating.
def get_pointed_data(dat, max_min_values):
    dat_pointed = dat.filter(col("currencycode") == "EUR") \
    .join(max_min_values, (dat.city_trans ==  max_min_values.city_trans_v) & (dat.checkin_date ==  max_min_values.checkin_date_v)) \
    .withColumn("price_points", config.price_max_points-(col("price_per_day")-col("min_price"))*config.price_max_points / col("diff_price")) \
    .withColumn("review_points", (col("review_score")-col("min_review"))*config.review_max_points / col("diff_review")) \
    .withColumn("total_points", col("price_points")+col("review_points"))
    return dat_pointed

# GET 3 BEST RATED
def get_top3_data(dat_pointed):
    windowSpec  = Window.partitionBy("city_trans","checkin_date").orderBy(col("total_points").desc())  
    dat_top3 = dat_pointed.withColumn("rank",rank().over(windowSpec)) \
    .filter(col("rank") <= 3)
    return dat_top3

# SCHEMA TO MAP THE DF TO SPARK
def map_DF_to_Spark(spark, data):
    if (data.empty == False):
        schema_booking = StructType([ \
                                     StructField("city_trans",StringType(),True), \
                                     StructField("hotel_name",StringType(),True), \
                                     StructField("min_total_price",DoubleType(),True), \
                                     StructField("currencycode",StringType(),True), \
                                     StructField("longitude",StringType(), True), \
                                     StructField("latitude",StringType(), True), \
                                     StructField("review_score",DoubleType(), True), \
                                     StructField("checkin_date",StringType(), True),
                                     StructField("import_date",StringType(), True)])
        sparkDF = spark.createDataFrame(data, schema=schema_booking)
        rdd = sparkDF.rdd.map(lambda x: (x[0], x[1], x[2]/config.days_to_add, x[3], x[4], x[5], x[6], x[7], x[8]))
        data2=rdd.toDF(["city_trans", "hotel_name","price_per_day", "currencycode", "longitude", "latitude", "review_score", "checkin_date", "import_date"])
        return data2
    else:
        return