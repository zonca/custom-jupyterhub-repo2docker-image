# Custom JupyterHub repo2docker Image Template

**For an introductory guide, read the [accompanying blog post on zonca.dev](https://zonca.dev/posts/2026-03-04-custom-jupyterhub-repo2docker-image).**

Build and publish a JupyterHub-ready single-user image using `repo2docker` and GitHub Actions, without maintaining a `Dockerfile`.

This template targets Zero to JupyterHub (Z2JH) and publishes to GHCR.

## What This Repository Provides

- `repo2docker`-based image builds from `environment.yml`
- Automated publish to GHCR with reproducible tags
- Image signing with Cosign (keyless)
- SBOM artifact + build provenance attestation
- Separate Z2JH integration workflow running on a real Kind+Helm JupyterHub

## Repository Layout

```text
.
├── .github/workflows/
│   ├── image.yml               # build, test, publish, sign, attest
│   └── z2jh-integration.yml    # real JupyterHub integration test (workflow_run)
├── environment.yml             # primary dependency spec
├── postBuild                   # optional post-build customization hook
├── tests/test_image.py         # container smoke tests
└── README.md
```

## CI/CD Workflows

### 1) `image.yml` (build and publish)

Triggers:
- push to `main`
- pull request to `main` (test job only, no publish)
- weekly schedule
- manual dispatch

Outputs:
- `ghcr.io/<owner>/<repo>:latest`
- `ghcr.io/<owner>/<repo>:sha-<12-char-sha>`
- `ghcr.io/<owner>/<repo>:YYYY-MM-DD-<7-char-sha>`

Security artifacts:
- cosign signatures
- SBOM (`spdx-json`) uploaded as workflow artifact
- provenance attestation pushed to registry

### 2) `z2jh-integration.yml` (real Hub integration)

Triggers:
- `workflow_run` after `Build and Publish repo2docker Image` completes
- manual dispatch

Run conditions:
- upstream workflow conclusion is `success`
- upstream branch is `main`

What it validates:
- deploys JupyterHub on Kind with Helm
- pulls published image from GHCR and loads it into Kind
- verifies Hub/proxy readiness
- validates authenticated Hub API calls
- validates user creation and spawn request submission

Note: this workflow currently validates Hub control-plane + API behavior. It does not gate on full single-user server readiness.

## Customizing Dependencies

Edit `environment.yml`, commit, and push.

Example:

```yaml
dependencies:
  - numpy
  - pandas
  - pip
  - pip:
      - your-package
```

Use `postBuild` for commands that should run after environment creation.

## GitHub Setup

Repository settings needed:
1. `Settings -> Actions -> General`: allow read/write workflow permissions
2. `Settings -> Packages`: choose package visibility policy

The workflows use `${{ secrets.GITHUB_TOKEN }}` for GHCR authentication.

## Using the Image in Z2JH

Use explicit command override for compatibility:

```yaml
singleuser:
  image:
    name: ghcr.io/YOUR_ORG/custom-jupyterhub-repo2docker-image
    tag: 2026-03-04-abcdef0
  cmd: jupyterhub-singleuser
  defaultUrl: /lab
```

Why this matters:
- `singleuser.cmd` is the process Kubernetes starts in the user pod.
- `jupyterhub-singleuser` is the JupyterHub-aware entrypoint that registers the server with Hub, handles Hub auth/token flow, and integrates with Hub/proxy lifecycle checks.
- If `singleuser.cmd` is omitted, chart/image defaults may start a different command (or inherit an unexpected `CMD`/entrypoint), causing user pods to run but not become usable from Hub.
- Setting it explicitly avoids those startup mismatches across base-image or chart changes.

Deploy:

```bash
helm upgrade --install jhub jupyterhub/jupyterhub \
  --namespace jhub \
  --create-namespace \
  --values config.yaml
```

## Operational Notes

- Prefer date-based tags in production instead of `latest`.
- `singleuser.cmd: jupyterhub-singleuser` is required for predictable Hub startup behavior.
- If you need strict single-user readiness gating in CI, add a second integration job with readiness-specific assertions.
