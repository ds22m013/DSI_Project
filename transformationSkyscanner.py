from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark import SparkContext


# GENERAL FUNCTION
def transform_Skyscanner_RDD(spark, data):
    dfSpark = map_DF_to_Spark(spark, data)
    data["arrival_time"] = calculate_ArrivalTime(dfSpark)
    return data

# SCHEMA TO MAP THE DF TO SPARK
def map_DF_to_Spark(spark, data):
    schema_skyScanner = StructType([ \
                                 StructField("time", StringType(),True), \
                                 StructField("duration", IntegerType(), True), \
                                 StructField("company", StringType(),True), \
                                 StructField("price", StringType(),True), \
                                 StructField("n_connections", IntegerType(), True), \
                                 StructField("date",StringType(), True), \
                                 StructField("import_date",StringType(), True), \
                                 StructField("origin",StringType(), True),
                                 StructField("destination",StringType(), True)])
    sparkDF = spark.createDataFrame(data, schema=schema_skyScanner)
    return sparkDF


# CALCULATION OF ARRIVAL TIME VIA RDD
# This function transforms the string of the departure time and calculates the arrival time using the duration variable.
def calculate_ArrivalTime(flightsDF):

    rddDuration = flightsDF.rdd.map(lambda x: x[1])
    rddDuration = rddDuration.map(lambda x: x/60)

    rddArrival = flightsDF.rdd.map(lambda x: [x[0], x[1]])

    def calculateArrival(departure, time):
        minutes = time % 60
        hours = int(time / 60)
        arrivalHour = int(int(departure[:2]) + hours)
        arrivalMinutes = int(int(departure[3:5]) + minutes)
        if ((arrivalMinutes + minutes) > 60):
            arrivalHour = arrivalHour + 1
        arrivalHour = arrivalHour % 24
        arrivalMinutes = arrivalMinutes % 60
        return f"{arrivalHour:02}" + ":" + f"{arrivalMinutes:02}" + ":00"

    rddArrival = rddArrival.map(lambda x: calculateArrival(x[0], x[1]))
    return rddArrival.collect()