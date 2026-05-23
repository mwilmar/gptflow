# Backup — GPTFlow Operation

## Backup Strategy

| Data | Method | Frequency | Retention | Storage |
|------|--------|-----------|-----------|---------|
| PostgreSQL (full) | pg_dump | Daily 2 AM | 30 days | S3 |
| PostgreSQL (WAL) | Continuous archiving | Real-time | 7 days | S3 |
| Redis (RDB) | Snapshot | Every 6h | 3 days | Local + S3 |
| Application config | Git | On change | Permanent | GitHub |
| Secrets/keys | Encrypted export | Weekly | 90 days | S3 (encrypted) |

## Backup Automation

```bash
#!/bin/bash
# /scripts/backup-db.sh (runs via cron daily 2 AM)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="gptflow_${TIMESTAMP}.sql.gz"

pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > /tmp/$BACKUP_FILE
aws s3 cp /tmp/$BACKUP_FILE s3://gptflow-backups/daily/$BACKUP_FILE
rm /tmp/$BACKUP_FILE

# Cleanup old backups (> 30 days)
aws s3 ls s3://gptflow-backups/daily/ | awk '{print $4}' | sort | head -n -30 | \
  xargs -I {} aws s3 rm s3://gptflow-backups/daily/{}
```

## Restore Procedure

```bash
# 1. Download backup
aws s3 cp s3://gptflow-backups/daily/gptflow_20260523.sql.gz /tmp/

# 2. Restore
gunzip /tmp/gptflow_20260523.sql.gz
psql -h $DB_HOST -U $DB_USER -d gptflow_restore < /tmp/gptflow_20260523.sql

# 3. Verify
psql -h $DB_HOST -U $DB_USER -d gptflow_restore -c "SELECT count(*) FROM contents;"

# 4. Swap (if full restore needed)
# Rename databases and update connection string
```

## Recovery Time Objectives
| Scenario | RTO | RPO |
|----------|-----|-----|
| Single table corruption | 1 hour | 0 (WAL) |
| Full DB loss | 4 hours | 24 hours (daily backup) |
| Complete infrastructure loss | 8 hours | 24 hours |

## Backup Verification
- Monthly: restore backup to test environment
- Verify: row counts match, data integrity check
- Alert: if backup job fails or size anomaly detected
