to export:
```
aws apigateway get-export \
  --parameters extensions='integrations' \
  --rest-api-id c6vrdtg6uc \
  --stage-name spaceface \
  --export-type swagger \
  --profile spaceface-eng \
  --region us-west-2 \
  spaceface-swagger.json
```

to import:
```
aws apigateway import-rest-api \
  --cli-binary-format raw-in-base64-out \
  --parameters endpointConfigurationTypes='REGIONAL' \
  --fail-on-warnings \
  --profile spaceface-eng \
  --region us-west-2 \
  --body 'file://spaceface-swagger.json'
```

example response:
```
{
    "id": "q0naprubu5",
    "name": "spaceface",
    "createdDate": "2020-09-19T21:36:25-07:00",
    "version": "2020-08-08T08:15:42Z",
    "apiKeySource": "HEADER",
    "endpointConfiguration": {
        "types": [
            "REGIONAL"
        ]
    }
}
```
