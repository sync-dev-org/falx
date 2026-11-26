falx
====

Small CLI/library wrapper for fal.ai queue jobs.

## CLI workflow

```bash
# Upload local assets first, then paste the returned CDN URLs into YAML.
falx upload path/to/image.png path/to/reference.mov

# Submit, poll, and download in one async pipeline with max_concurrency control.
falx run -c job.yaml

# Resume a previously interrupted request by id (e.g. after timeout).
falx fetch -c job.yaml --request-id <request_id>

# Cancel a queued request.
falx cancel -c job.yaml --request-id <request_id>
```

Online commands print machine-readable stdout YAML. Job YAML is a pure input spec;
falx does not write request state or results back to YAML.

`falx schema <app_id>` prints a top-level `JobConfig` YAML example. Job YAML no
longer accepts `uploads` or `results` blocks; URL parameters must already be public
`http(s)` or `data:` URLs.
