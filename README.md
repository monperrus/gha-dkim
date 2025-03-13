# gha-dkim
A GitHub Action to to deploy a file to a server with dkim authentication.

## Example Usage:

In `.github/workflows/deploy.yml`

```yaml
name: "gha-dkim deployer"
on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          repository: ${{ github.event.pull_request.head.repo.full_name }}
          ref: ${{ github.event.pull_request.head.ref }}
          fetch-depth: "0"

      - name: deploy
        uses: monperrus/gha-dkim@last
        with:
          server: "https://example.com/endpoint"
          file_to_deploy: "foo.tgz"
          signing_address: "bob@example.com"
          pem_private_key_path: "gha.pem"
```

