MAX_DISK_PERCENT_SRC=70
CLEANUP_DISK_PERCENT_SRC=60

MAX_DISK_PERCENT_DST=80
CLEANUP_DISK_PERCENT_DST=70

MAX_DISK_PERCENT_SNAPSHOT=20
CLEANUP_DISK_PERCENT_SNAPSHOT=70
SNAPSHOT_PATH="/"

SNAPSHOT_WAIT_TIME=30

# src info
srcNodeAddress = ""
srcUser = ""
srcPassword = ""
###

# dst info
dstNodeAddress = ""
dstUser = ""
dstPassword = ""
dstSnapshotRepository = ""
###

# Ignore opensearch default names
ignoreListForIndices = [
    '.opendistro*',
    '.opensearch',
    'graylog_*',
    '.kibana_*',
    'gl-events_*',
    'gl-system-events_*',
    '.tasks'
    ]

# Convert ignoreListForIndices to a regular expression pattern
ignore_pattern = '|'.join(ignoreListForIndices)

alertWebhook='https://hooks.slack.com/URL'