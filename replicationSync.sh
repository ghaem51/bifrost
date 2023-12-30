#!/bin/bash
# src info
srcNode="srcNodeAdress"
# index names for example ...
srcSearchIndex=("nginx" "database" "miniio" "cicd" "git" "others" "redis" "application" "waf")
srcUser="opensearchUser"
srcPassword="opensearchUserPassword"
# dst info
dstNode="dstNodeAdress"
# dst index prefix name
dstSearchIndex="arvan"
dstUser="opensearchUser"
dstPassword="opensearchUserPassword"

for srcIndex in "${srcSearchIndex[@]}";do
  echo "srcIndex: ${srcIndex}"
  srcIndexList=($(curl -XGET -s --cacert root-ca.pem -u "${srcUser}:${srcPassword}" "https://${srcNode}:9200/_cat/indices?pretty" | grep "${srcIndex}"  | awk '{print $3}' | sort))
  echo "src IndexList: ${srcIndexList}"
  dstIndexList=($(curl -XGET -s --cacert root-ca.pem -u "${dstUser}:${dstPassword}" "https://${dstNode}:9200/_cat/indices?pretty" | grep "${dstSearchIndex}_${srcIndex}"  | awk '{print $3}' | sort ))
  echo "dstIndexList: ${dstIndexList}"
  echo "already exist:"
  for target in "${dstIndexList[@]}"; do
    for i in "${!srcIndexList[@]}"; do
      if [[ "${srcIndexList[i]#$srcIndex}" = "${target#$dstSearchIndex'_'$srcIndex}" ]]; then
        echo "${dstSearchIndex}${target#$dstSearchIndex}"
        unset 'srcIndexList[i]'
      fi
    done
  done

  for src in "${srcIndexList[@]}";do
    echo "add: ${dstSearchIndex}_${srcIndex}${src#$srcIndex}"
    curl -XPUT -u "${dstUser}:${dstPassword}" "https://${dstNode}:9200/_plugins/_replication/${dstSearchIndex}_${srcIndex}${src#$srcIndex}/_start?pretty" --cacert root-ca.pem -H 'Content-type: application/json' \
    -d "{\"leader_alias\":\"wazuh-cluster\", \"leader_index\": \"$src\", \"use_roles\": { \"leader_cluster_role\": \"all_access\", \"follower_cluster_role\": \"all_access\"}}"
  done
done
