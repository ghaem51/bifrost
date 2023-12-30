#!/usr/bin/env python3
import requests
import re
from getSize import get_size_gb
from env import *
from apiCall import opensearchAPIRequest, slackAPIRequest
import time
from diskCheck import checkDiskUsage 

try:
    srcNode = opensearchAPIRequest(f"https://{srcNodeAddress}:9200/",auth=(srcUser, srcPassword),verify='root-ca.pem')
    dstNode = opensearchAPIRequest(f"https://{dstNodeAddress}:9200/",auth=(dstUser, dstPassword),verify='root-ca.pem')
    alert = slackAPIRequest(alertWebhook,verify=True)

    srcIndices = srcNode.getIndices()
    ## ignore opensearch indices
    srcIndices = [item for item in srcIndices if not re.search(ignore_pattern, item['index']) ]
    srcIndices.sort(key=lambda x: x["creation.date"])
    ###

    dstIndices = dstNode.getIndices()
    dstIndices = [item for item in dstIndices if not re.search(ignore_pattern, item['index']) ]
    dstIndices.sort(key=lambda x: x["creation.date"])
    ###

    # Extracting the 'id' values from snapShots as snapshot names
    snapShots = dstNode.getSnapshots(dstSnapshotRepository)
    snapShots.sort(key=lambda x: x["start_epoch"])
    snapShotsNames = {item['id'] for item in snapShots}
    # snapShotsNames = ['wazuh-monitoring-2023.15w','arvan_git_0']

    snapShotDiskPercent = checkDiskUsage(SNAPSHOT_PATH)
    snapshotCount = 0
    while (snapShotDiskPercent > MAX_DISK_PERCENT_SNAPSHOT):
        print(f"need cleaning Snapshot disk remove {snapShots[snapshotCount]['id']}")
        dstNode.deleteSnapshot(dstSnapshotRepository,snapShots[snapshotCount]['id'])
        time.sleep(SNAPSHOT_WAIT_TIME)
        snapShotDiskPercent = checkDiskUsage(SNAPSHOT_PATH)
        snapshotCount += 1

    print("# get src disk status")
    srcDisksStatus = srcNode.getDiskStatus()
    srcMaxDiskPercent = 0
    srcTotalDisk = 0
    for disk in srcDisksStatus:
        if (disk['disk.percent']!=None):
            if (srcMaxDiskPercent < int(disk['disk.percent'])):
                srcMaxDiskPercent = int(disk['disk.percent'])
            srcTotalDisk += get_size_gb(disk['disk.total'])
    srcTotalDisk=srcTotalDisk / len(srcDisksStatus)
    print(srcMaxDiskPercent)
    if (srcMaxDiskPercent > MAX_DISK_PERCENT_SRC):
        print("need cleaning src")
        srcDeleteList = []
        totalSize = 0
        for indice in srcIndices:
            if (indice['store.size'] != None):
                totalSize += get_size_gb(indice['store.size'])
                srcDeleteList.append(indice)
                if (totalSize >= (srcMaxDiskPercent - CLEANUP_DISK_PERCENT_SRC) / 100 * srcTotalDisk ):
                    break
        indices_not_in_snapshot = [item for item in srcDeleteList if "arvan_"+item['index'] not in snapShotsNames]
        indices_not_in_snapshot_clean = [item for item in indices_not_in_snapshot if "arvan-"+item['index'] not in snapShotsNames]
        for indice in indices_not_in_snapshot_clean:
            if 'wazuh' in indice['index']:
                dstNode.createSnapShot(dstSnapshotRepository,"arvan-"+indice['index'],"arvan-"+indice['index'])
                status = dstNode.checkSnapshotStatus(dstSnapshotRepository, "arvan-"+indice['index'])
                while status['snapshots'][0]['state'] == "IN_PROGRESS":
                    time.sleep(SNAPSHOT_WAIT_TIME)
                    status = dstNode.checkSnapshotStatus(dstSnapshotRepository, "arvan-"+indice['index'])
                if status['snapshots'][0]['state'] == "SUCCESS":
                    srcNode.deleteIndice(indice['index'])
                    dstNode.stopReplicationIndice("arvan_"+indice['index'])
                    dstNode.deleteIndice("arvan-"+indice['index'])
                else:
                    alert.sendAlert(f"snap shot error arvan-{indice['index']}",f"{dstNodeAddress}")
            else:
                dstNode.createSnapShot(dstSnapshotRepository,"arvan_"+indice['index'],"arvan_"+indice['index'])
                status = dstNode.checkSnapshotStatus(dstSnapshotRepository, "arvan_"+indice['index'])
                while status['snapshots'][0]['state'] == "IN_PROGRESS":
                    time.sleep(SNAPSHOT_WAIT_TIME)
                    status = dstNode.checkSnapshotStatus(dstSnapshotRepository, "arvan_"+indice['index'])
                if status['snapshots'][0]['state'] == "SUCCESS":
                    srcNode.deleteIndice(indice['index'])
                    dstNode.stopReplicationIndice("arvan_"+indice['index'])
                    dstNode.deleteIndice("arvan_"+indice['index'])
                else:
                    alert.sendAlert(f"snap shot error arvanـ{indice['index']}",f"{dstNodeAddress}")
        indices_in_snapshot = [item for item in srcDeleteList if "arvan_"+item['index'] in snapShotsNames]
        indices_in_snapshot += [item for item in srcDeleteList if "arvan-"+item['index'] in snapShotsNames]
        for indice in indices_in_snapshot:
            if 'wazuh' in indice['index']:
                status = dstNode.checkSnapshotStatus(dstSnapshotRepository, "arvan-"+indice['index'])
                while status['snapshots'][0]['state'] == "IN_PROGRESS":
                    time.sleep(SNAPSHOT_WAIT_TIME)
                    status = dstNode.checkSnapshotStatus(dstSnapshotRepository, "arvan-"+indice['index'])
                if status['snapshots'][0]['state'] == "SUCCESS":
                    srcNode.deleteIndice(indice['index'])
                    dstNode.stopReplicationIndice("arvan-"+indice['index'])
                    dstNode.deleteIndice("arvan-"+indice['index'])
                else:
                    alert.sendAlert(f"snap shot error arvan-{indice['index']}",f"{dstNodeAddress}")
            else:
                status = dstNode.checkSnapshotStatus(dstSnapshotRepository, "arvan_"+indice['index'])
                while status['snapshots'][0]['state'] == "IN_PROGRESS":
                    time.sleep(SNAPSHOT_WAIT_TIME)
                    status = dstNode.checkSnapshotStatus(dstSnapshotRepository, "arvan_"+indice['index'])
                if status['snapshots'][0]['state'] == "SUCCESS":
                    srcNode.deleteIndice(indice['index'])
                    dstNode.stopReplicationIndice("arvan_"+indice['index'])
                    dstNode.deleteIndice("arvan_"+indice['index'])
                else:
                    alert.sendAlert(f"snap shot error arvan_{indice['index']}",f"{dstNodeAddress}")

    # reload data 
    snapShots = dstNode.getSnapshots(dstSnapshotRepository)
    snapShotsNames = {item['id'] for item in snapShots}
    dstIndices = dstNode.getIndices()
    dstIndices = [item for item in dstIndices if not re.search(ignore_pattern, item['index']) ]
    dstIndices.sort(key=lambda x: x["creation.date"])
    print("# get dst disk status")
    dstDisksStatus = dstNode.getDiskStatus()
    dstMaxDiskPercent = 0
    dstTotalDisk = 0
    for disk in dstDisksStatus:
        if (disk['disk.percent']!=None):
            if (dstMaxDiskPercent < int(disk['disk.percent'])):
                dstMaxDiskPercent = int(disk['disk.percent'])
            dstTotalDisk += get_size_gb(disk['disk.total'])
    dstTotalDisk=dstTotalDisk / len(srcDisksStatus)
    print(dstMaxDiskPercent)
    if (dstMaxDiskPercent > MAX_DISK_PERCENT_DST):
        print("need cleaning dst")
        dstDeleteList = []
        totalSize = 0
        for indice in dstIndices:
            if (indice['store.size'] != None):
                totalSize += get_size_gb(indice['store.size'])
                dstDeleteList.append(indice)
                if (totalSize >= (dstMaxDiskPercent - CLEANUP_DISK_PERCENT_DST) / 100 * dstTotalDisk ):
                    break
        indices_not_in_snapshot = [item for item in dstDeleteList if item['index'] not in snapShotsNames]
        for indice in indices_not_in_snapshot:
            dstNode.createSnapShot(dstSnapshotRepository,indice['index'],indice['index'])
            status = dstNode.checkSnapshotStatus(dstSnapshotRepository,indice['index'])
            while status['snapshots'][0]['state'] == "IN_PROGRESS":
                time.sleep(SNAPSHOT_WAIT_TIME)
                status = dstNode.checkSnapshotStatus(dstSnapshotRepository, indice['index'])
            if status['snapshots'][0]['state'] == "SUCCESS":
                if ("arvan-" in indice['index']):
                    srcNode.deleteIndice(indice['index'].replace("arvan-", ""))
                elif ("arvan_" in indice['index']):
                    srcNode.deleteIndice(indice['index'].replace("arvan_", ""))
                dstNode.stopReplicationIndice(indice['index'])
                dstNode.deleteIndice(indice['index'])
            else:
                alert.sendAlert(f"snap shot error{indice['index']}",f"{dstNodeAddress}")
        indices_in_snapshot = [item for item in dstDeleteList if item['index'] in snapShotsNames]
        for indice in indices_in_snapshot:
            status = dstNode.checkSnapshotStatus(dstSnapshotRepository, indice['index'])
            while status['snapshots'][0]['state'] == "IN_PROGRESS":
                time.sleep(SNAPSHOT_WAIT_TIME)
                status = dstNode.checkSnapshotStatus(dstSnapshotRepository, indice['index'])
            if status['snapshots'][0]['state'] == "SUCCESS":
                if ("arvan-" in indice['index']):
                    srcNode.deleteIndice(indice['index'].replace("arvan-", ""))
                elif ("arvan_" in indice['index']):
                    srcNode.deleteIndice(indice['index'].replace("arvan_", ""))
                dstNode.stopReplicationIndice(indice['index'])
                dstNode.deleteIndice(indice['index'])
            else:
                alert.sendAlert(f"snap shot error{indice['index']}",f"{dstNodeAddress}")
except Exception as e:
    alert.sendAlert(f"snap shot error {e}",f"{dstNodeAddress}{srcNodeAddress}")