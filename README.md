# gha-dkim
A GitHub Action to to deploy a file to a server with dkim authentication.

## Protocol Documentation

For details on the HTTP DKIM deployment protocol, refer to [http-dkim-protocol.md](http-dkim-protocol.md).

## Example Usage:

In `.github/workflows/deploy.yml`

### Deploy a single file

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

      - name: deploy
        uses: monperrus/gha-dkim@last
        with:
          server: "https://example.com/endpoint"
          signing_address: "bob@example.com"
          # Use either pem_private_key_path or pem_private_key
          # pem_private_key_path: "gha.pem"
          pem_private_key: ${{ secrets.DKIM_PRIVATE_KEY }}
```

### Bind file name and repository to the signature

Add `bind_headers: "true"` to `with:` so the signature also covers `Content-Disposition` and `X-GitHub-Repository` (the server must verify headers listed in `h=`; default off).

### Deploy multiple files at once

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

      - name: deploy
        uses: monperrus/gha-dkim@last
        with:
          server: "https://example.com/endpoint"
          files_to_deploy: "foo.tgz bar.zip package.tar.gz"
          signing_address: "bob@example.com"
          pem_private_key: ${{ secrets.DKIM_PRIVATE_KEY }}              
```

