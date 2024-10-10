## Frontend installation
```Bash
$helm upgrade frontend-staging ./helms -f ./helms/values-staging.yaml --namespace frontend

$helm upgrade frontend-prod ./helms -f ./helms/values-prod.yaml --namespace frontend
```

