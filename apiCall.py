import requests
import json
class opensearchAPIRequest:
    def __init__(self, url, auth=None, headers=None, params=None, data=None, verify=True):
        self.url = url
        self.auth = auth
        self.headers = headers
        self.params = params
        self.data = data
        self.verify = verify

    def getSnapshots(self,snapshotRepository):
        response = requests.get(
            url=self.url+f"_cat/snapshots/{snapshotRepository}?format=json",
            auth=self.auth,
            headers=self.headers,
            params=self.params,
            data=self.data,
            verify=self.verify
        )
        return response.json()
    def deleteSnapshot(self,snapshotRepository,snapshotName):
        response = requests.delete(
            url=self.url+f"_snapshot/{snapshotRepository}/{snapshotName}",
            auth=self.auth,
            headers=self.headers,
            params=self.params,
            data=self.data,
            verify=self.verify
        )
        return response.json()
    def getIndices(self):
        response = requests.get(
            url=self.url+f"_cat/indices?format=json&h=creation.date,index,store.size",
            auth=self.auth,
            headers=self.headers,
            params=self.params,
            data=self.data,
            verify=self.verify
        )
        return response.json()
    def getDiskStatus(self):
        response = requests.get(
            url=self.url+f"_cat/allocation?format=json",
            auth=self.auth,
            headers=self.headers,
            params=self.params,
            data=self.data,
            verify=self.verify
        )
        return response.json()
    def createSnapShot(self,snapshotRepository,snapshotName,indices):
        response = requests.put(
            url=self.url+f"_snapshot/{snapshotRepository}/{snapshotName}",
            auth=self.auth,
            headers=self.headers,
            params=self.params,
            json={
                "indices": f"{indices}",  # Change to specific indices or patterns if needed
                "ignore_unavailable": True,
                "include_global_state": False
            },
            verify=self.verify
        )
        return response.json()
    
    def checkSnapshotStatus(self,snapshotRepository,snapshotName):
        response = requests.get(
            url=self.url+f"_snapshot/{snapshotRepository}/{snapshotName}?format=json",
            auth=self.auth,
            headers=self.headers,
            params=self.params,
            verify=self.verify
        )
        return response.json()

    def deleteIndice(self,indexName):
        response = requests.delete(
            url=self.url+f"{indexName}",
            auth=self.auth,
            headers=self.headers,
            params=self.params,
            verify=self.verify
        )
        return response.json()

    def stopReplicationIndice(self,indexName):
        response = requests.post(
            url=self.url+f"_plugins/_replication/{indexName}/_stop",
            auth=self.auth,
            headers=self.headers,
            params=self.params,
            json={},
            verify=self.verify
        )
        return response.json()

class slackAPIRequest:
    def __init__(self, url, auth=None, headers=None, params=None, data=None, verify=False):
        self.url = url
        self.auth = auth
        self.headers = headers
        self.params = params
        self.data = data
        self.verify = verify

    def sendAlert(self,text,username):
        response = requests.post(
            self.url,
            json.dumps({"text": text,"username":username})
        )
        return response