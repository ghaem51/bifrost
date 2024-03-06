# bifrost

**bifrost** is an application designed to manage two clusters for index replication and snapshot.

## Getting Started

To get started with **bifrost**, follow these steps:

1. Copy `envExample.py` to `env.py`.
2. Configure the environment variables in `env.py` to match your setup.
3. Set up a crontab to automatically run the script in the background.

```bash
cp envExample.py env.py
```
After copying the example environment file, open env.py and set your host information accordingly.
## Environment Configuration
Before running bifrost, ensure you have configured the following environment variables in env.py:
```
Disk usage configuration for source and destination clusters.
Snapshot configuration including path and wait time.
Source cluster information: node address, username, and password.
Destination cluster information: node address, username, password, and snapshot repository.
Ignored indices list.
Alert webhook URL.
```
Refer to envExample.py for an example configuration.
## Usage
Once you have set up the environment file, you can run bifrost using Python 3 by executing the opensearch.py script:

``` bash
python3 opensearch.py
```
This will execute the script and perform the necessary tasks to manage your clusters.

## Scheduled Execution with Cron
To schedule bifrost to run every day at 1 am, you can set up a cron job.
Open the crontab file for editing:
```bash
crontab -e
```
Add the following line to the crontab file:
```bash
0 1 * * * cd /path/to/project && /usr/bin/python3 opensearch.py
```
Replace /path/to/project with the actual path to your project directory.

Save and exit the crontab file. This cron job will now change to the project directory and execute your script every day at 1:00 am.

# Contribution
Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or submit a pull request.

# License
This project is licensed under the MIT License.
