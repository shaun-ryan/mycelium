sudo apt-get install -y jq

CLST=0926-204304-key830

databricks libraries list --cluster-id $CLST --profile AZDO

WHLS=$(databricks libraries list --cluster-id $CLST | jq -c '.library_statuses[] | select(.library.whl | . and contains("pyFathom")) | .library.whl')

echo $WHLS