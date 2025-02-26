import polars as pl

from op_analytics.coreutils.partitioned.breakout import breakout_partitions
from op_analytics.coreutils.partitioned.partition import (
    PartitionColumn,
    Partition,
    PartitionData,
)


def test_breakout_partitions():
    df = pl.DataFrame(
        {
            "dt": [
                "2024-01-01",
                "2024-01-01",
                "2024-01-01",
                "2024-01-01",
                "2024-01-02",
                "2024-01-02",
                "2024-01-03",
            ],
            "chain": ["op", "op", "base", "base", "base", "base", "op"],
            "c": ["some", "words", "here", "and", "some", "more", "blah"],
        }
    )

    outputs: list[PartitionData] = []
    for part in breakout_partitions(
        df,
        partition_cols=["dt", "chain"],
    ):
        outputs.append(part)
        assert part.df.columns == ["c"]

    actual = []
    for _ in outputs:
        actual.append(
            dict(
                partitions=_.partition,
                full_path=_.partition.path,
                nu_rows=len(_.df),
            )
        )

    actual.sort(key=lambda x: x["full_path"])
    assert actual == [
        {
            "partitions": Partition(
                cols=[
                    PartitionColumn(name="dt", value="2024-01-01"),
                    PartitionColumn(name="chain", value="base"),
                ]
            ),
            "full_path": "dt=2024-01-01/chain=base",
            "nu_rows": 2,
        },
        {
            "partitions": Partition(
                cols=[
                    PartitionColumn(name="dt", value="2024-01-01"),
                    PartitionColumn(name="chain", value="op"),
                ]
            ),
            "full_path": "dt=2024-01-01/chain=op",
            "nu_rows": 2,
        },
        {
            "partitions": Partition(
                cols=[
                    PartitionColumn(name="dt", value="2024-01-02"),
                    PartitionColumn(name="chain", value="base"),
                ]
            ),
            "full_path": "dt=2024-01-02/chain=base",
            "nu_rows": 2,
        },
        {
            "partitions": Partition(
                cols=[
                    PartitionColumn(name="dt", value="2024-01-03"),
                    PartitionColumn(name="chain", value="op"),
                ]
            ),
            "full_path": "dt=2024-01-03/chain=op",
            "nu_rows": 1,
        },
    ]


def test_breakout_partitions_empty():
    df = pl.DataFrame(
        {
            "dt": [
                "2024-01-01",
                "2024-01-01",
                "2024-01-01",
                "2024-01-01",
                "2024-01-02",
                "2024-01-02",
                "2024-01-03",
            ],
            "chain": ["op", "op", "base", "base", "base", "base", "op"],
            "c": ["some", "words", "here", "and", "some", "more", "blah"],
        }
    )

    outputs: list[PartitionData] = []
    for part in breakout_partitions(
        df.filter(pl.col("dt") == ""),  # Filter out all data to get a default empty parquet file
        partition_cols=["dt", "chain"],
        default_partitions=[{"chain": "op", "dt": "2023-10-30"}],
    ):
        outputs.append(part)
        assert part.df.columns == ["c"]

    actual = []
    for _ in outputs:
        actual.append(
            dict(
                partitions=_.partition,
                full_path=_.partition.path,
                nu_rows=len(_.df),
            )
        )

    actual.sort(key=lambda x: x["full_path"])
    assert actual == [
        {
            "partitions": Partition(
                [
                    PartitionColumn(name="chain", value="op"),
                    PartitionColumn(name="dt", value="2023-10-30"),
                ]
            ),
            "full_path": "chain=op/dt=2023-10-30",
            "nu_rows": 0,
        }
    ]
