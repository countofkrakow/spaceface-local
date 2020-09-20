### register jobs:

```
aws batch register-job-definition \
 --region us-west-2 --profile spaceface-eng \
  --cli-input-json 'file://job-definitions/fom-processor.json'
```

### create compute environment:
```
aws batch create-compute-environment \
  --region us-west-2 --profile spaceface-eng \
  --cli-input-json 'file://compute-environments/spaceface-environment.json'
```

example result
```
{
    "computeEnvironmentName": "spaceface-environment",
    "computeEnvironmentArn": "arn:aws:batch:us-west-2:694126695710:compute-environment/spaceface-environment"
}
```

### create job queue
```
aws batch create-job-queue \
  --region us-west-2 --profile spaceface-eng \
  --cli-input-json 'file://job-queues/fom-queue.json'
```

example result
```
{
    "jobQueueName": "fom-queue",
    "jobQueueArn": "arn:aws:batch:us-west-2:694126695710:job-queue/fom-queue"
}
```
