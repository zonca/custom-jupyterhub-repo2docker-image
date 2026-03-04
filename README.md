# Custom JupyterHub repo2docker Image Template

Template repository to build a JupyterHub-ready single-user image with `repo2docker` and GitHub Actions.

This is designed for Zero to JupyterHub (Z2JH) deployments and publishes images to GHCR.

## Features

- No `Dockerfile` needed for standard use cases
- Primary dependency interface is `environment.yml`
- CI smoke tests for JupyterHub compatibility
- Publish tags: `latest`, commit SHA, and `YYYY-MM-DD-<shortsha>`
- Cosign keyless signatures
- SBOM generation and provenance attestation
- Weekly scheduled rebuilds for base image updates

## Repository Layout

```
.
├── .github/workflows/image.yml
├── environment.yml
├── postBuild
├── tests/test_image.py
└── README.md
```

## Customize The Environment

Edit `environment.yml` and push to trigger a new image build.

Example additions:

```yaml
dependencies:
  - numpy
  - pandas
  - pip
  - pip:
      - your-package
```

## GitHub Actions + GHCR Setup

The workflow uses `GITHUB_TOKEN` to publish to `ghcr.io/<owner>/<repo>`.

Repository settings:

1. `Settings -> Actions -> General`: allow workflow permissions to read and write.
2. `Settings -> Packages`: ensure your package visibility is what you want.

## Use In Zero To JupyterHub

Set image + command in your Helm values:

```yaml
singleuser:
  image:
    name: ghcr.io/YOUR_ORG/custom-jupyterhub-repo2docker-image
    tag: latest
  cmd: jupyterhub-singleuser
  defaultUrl: /lab
```

Then upgrade your release:

```bash
helm upgrade --install jhub jupyterhub/jupyterhub \
  --namespace jhub \
  --create-namespace \
  --values config.yaml
```

## Notes

- Explicitly setting `singleuser.cmd: jupyterhub-singleuser` avoids startup mismatches.
- For reproducibility in production, pin to a date-based tag instead of `latest`.
