# Prepare a GitHub repository

Suggested repository name: `gaussian-modern`.

The ZIP contains the repository working tree, including `.github/` and the Git
configuration files. It excludes `.git/`, local paths, credentials, caches, and
intermediate build output.

For a new checkout from the ZIP:

```sh
cd gaussian-modern
git init -b main
git add .
git commit -m "Prepare Gaussian Modern 0.108"
```

Create an empty GitHub repository with your preferred visibility, then add its
actual remote and push `main` using your normal GitHub workflow. No remote is
configured and no repository has been published by this preparation. Preserve
LICENSE and THIRD-PARTY-NOTICES.md in distributions.

The included GitHub Actions workflow rebuilds and validates the JSON and UFO
sources, checks that the committed OTF/TTF files match the JSON masters, and in a
separate job rebuilds the Type 1 fonts and typesets a pdfLaTeX test document. FontTools is pinned to the version used for this package. The specimen
requires XeLaTeX with fontspec and unicode-math and is not built by CI.
