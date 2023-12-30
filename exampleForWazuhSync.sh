#!/bin/bash
srcNode="srcNodeAdress"
srcSearchIndex="wazuh-alerts-4.x-"
srcUser="opensearchUser"
srcPassword="opensearchUserPassword"
srcIndexList=($(curl -XGET -s --cacert root-ca.pem -u "${srcUser}:${srcPassword}" "https://${srcNode}:9200/_cat/indices?pretty" | grep "${srcSearchIndex}"  | awk '{print $3}' | sort))
# dst info
dstNode="dstNodeAdress"
dstSearchIndex="clone-wazuh-alerts-4.x-"
dstUser="opensearchUser"
dstPassword="opensearchUserPassword"
dstIndexList=($(curl -XGET -s --cacert root-ca.pem -u "${dstUser}:${dstPassword}" "https://${dstNode}:9200/_cat/indices?pretty" | grep "${dstSearchIndex}"  | awk '{print $3}' | sort ))
#echo ${srcIndexList#"$srcSearchIndex"}
#echo ${dstIndexList#"$dstSearchIndex"}
echo "already exist:"
for target in "${dstIndexList[@]}"; do
  for i in "${!srcIndexList[@]}"; do
    if [[ "${srcIndexList[i]#$srcSearchIndex}" = "${target#$dstSearchIndex}" ]]; then
      echo "${target#$dstSearchIndex}"
      unset 'srcIndexList[i]'
    fi
  done
done

echo "add new indexs:"
for src in "${srcIndexList[@]}"
do
  echo "${src#$srcSearchIndex}"
  curl -XPUT -u "${dstUser}:${dstPassword}" "https://${dstNode}:9200/_plugins/_replication/${dstSearchIndex}${src#$srcSearchIndex}/_start?pretty" --cacert root-ca.pem \
  -H 'Content-type: application/json' \
  -d "{\"leader_alias\":\"wazuh-cluster\", \"leader_index\": \"$src\", \"use_roles\": { \"leader_cluster_role\": \"all_access\", \"follower_cluster_role\": \"all_access\"}}"

done
