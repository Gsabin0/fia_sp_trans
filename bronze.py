import os
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages "
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
    "org.apache.hadoop:hadoop-aws:3.3.4,"
    "com.amazonaws:aws-java-sdk-bundle:1.12.262 "
    "pyspark-shell"
)

from pyspark.sql.functions import col, current_timestamp, date_format
from s3_utils import get_spark_session

# Mapeia cada tópico para seu caminho S3
topics_to_s3_paths = {
    "veiculos": "s3a://bronze/veiculos",
    "linhas": "s3a://bronze/linhas",
    "motoristas": "s3a://bronze/motoristas"
}

def read_from_kafka(spark, topic_name):
    print(f"Lendo do tópico Kafka: {topic_name}")

    df_kafka = (
        spark.read
        .format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", topic_name)
        .option("startingOffsets", "earliest")
        .load()
    )

    df_str = df_kafka.selectExpr("CAST(value AS STRING) AS json_value")

    json_rdd = df_str.select("json_value").rdd.map(lambda row: row.json_value).cache()

    if json_rdd.isEmpty():
        json_rdd.unpersist()
        return None

    df_final = spark.read.json(json_rdd)
    json_rdd.unpersist()

    return df_final

def run_bronze_layer():
    spark = get_spark_session()

    for topic, s3_path in topics_to_s3_paths.items():
        df_raw = read_from_kafka(spark, topic)

        if df_raw is not None and df_raw.count() > 0:
            df_final = df_raw.withColumn("ingestion_timestamp_utc", current_timestamp())
            df_final = df_final.withColumn("data", date_format(col("ingestion_timestamp_utc"), "yyyy-MM-dd")) \
                               .withColumn("hora", date_format(col("ingestion_timestamp_utc"), "HH"))

            print(f"Dados do tópico {topic}:")
            df_final.show(truncate=False)

            df_final.write.mode("append").option("mergeSchema", "true").partitionBy("data", "hora").parquet(s3_path)
            print(f"Dados salvos no MinIO em: {s3_path} particionados por data/hora")
        else:
            print(f"Nenhum dado no tópico {topic}.")

    spark.stop()

if __name__ == "__main__":
    run_bronze_layer()
