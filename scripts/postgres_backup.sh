pg_basebackup -h social-network-db_0 -D /pgslave -U replicator -v -P --wal-method=stream
