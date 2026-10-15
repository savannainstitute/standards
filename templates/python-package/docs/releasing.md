# Releasing a version

1. Set the new version in `pyproject.toml` and add its entry at the top of `CHANGELOG.md`, on a
   branch, by pull request.
2. When the pull request is merged, tag the merge commit with the version, for example `v0.2.0`, and
   push the tag. A version a paper cites is tagged `published/<name>` as well; those tags cannot be
   moved or deleted.
3. People install the package from the repository with pip, naming the tag.
