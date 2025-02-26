CREATE EXTERNAL TABLE `oplabs-tools-data.dailydata_defillama.revenue_protocols_metadata_v1`
WITH PARTITION COLUMNS (dt DATE) 
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://oplabs-tools-data-sink/defillama/revenue_protocols_metadata_v1/*'],
    hive_partition_uri_prefix = 'gs://oplabs-tools-data-sink/defillama/revenue_protocols_metadata_v1',
    require_hive_partition_filter = true,
    decimal_target_types = ["NUMERIC", "BIGNUMERIC"]
)
