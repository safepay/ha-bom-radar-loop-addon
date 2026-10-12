# Releasing

Versions are **not** bumped in feature PRs. Instead, several PRs are merged to
`main` (none of them touching the version), then a single release is cut with
the **Release** GitHub Action, which bumps the version, tags it, and publishes a
GitHub release.

## Cut a release

1. Merge the PRs you want to ship into `main`.
2. Go to **Actions → Release → Run workflow** (on `main`).
3. Choose the bump:
   - `patch` — bug fixes (1.0.17 → 1.0.18)
   - `minor` — new features (1.0.17 → 1.1.0)
   - `major` — breaking changes (1.0.17 → 2.0.0)
4. Optionally set a title, or tick **draft** to edit the notes before publishing.

The action then:

- reads the current version from `bom-radar-loop/config.json`,
- bumps `config.json` and the `VERSION` constant in
  `bom-radar-loop/bom_radar_downloader.py`,
- commits `chore: bump version to X.Y.Z` to `main`,
- tags `vX.Y.Z`,
- creates a GitHub release with notes generated from the merged PRs.

## How users get it

The Home Assistant **add-on store reads the version from `config.json` on the
default branch**, so the bump commit is what offers the update. The GitHub
release/tag is for the changelog and record-keeping.

> **Note on betas:** unlike a HACS integration, an add-on has no built-in beta
> channel — the store always serves whatever version is on the default branch,
> so a GitHub *pre-release* would not hide it from users. To beta-test, point a
> test Home Assistant at this repository on a **separate branch** (which can
> carry a higher `config.json` version) before merging to `main`.

## Changelog

Keep `bom-radar-loop/CHANGELOG.md` updated as you go: add entries under a
`## [Unreleased]` heading at the top, creating that heading yourself if it is
not there (the release workflow does not leave one behind). It lives in the
add-on folder so Home Assistant shows it in the update dialog.

When you cut a release, the **Release** action renames `## [Unreleased]` to
`## [X.Y.Z] - DATE` for you and does **not** re-add an empty `[Unreleased]`.
That is deliberate: Home Assistant renders this whole file in the update dialog,
so a shipped release must not lead with an empty "Unreleased" section. Do not
rename the heading by hand before running the action.
