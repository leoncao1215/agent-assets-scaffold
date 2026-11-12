# Contributing

Keep changes useful across independent collections. Concrete service bindings,
business workflows, user preferences, installed client configuration, and
machine runtime state belong outside this scaffold.

Only contribute material you have rights to publish under the repository's MIT
license. References to private repositories or services can themselves reveal
information; substituting credentials alone is not sufficient sanitization.
Use fictional identities and reserved example domains in examples.

Changes to `template/` affect future instances; they do not update existing
ones. Describe upgrade implications and preserve a reviewable baseline. Keep
the sync skill's companion contracts inside its directory so an installed copy
does not depend on files left behind in the scaffold checkout.

Before publishing:

- Run `python -m unittest discover -s tests -v` and `git diff --check`.
- Review all proposed files and Git metadata for private material, accidental
  runtime files, and unrelated changes. `.gitignore` is only a guardrail.
- Check examples remain inert and documentation links resolve.
- Report static tests separately from live client loading or network checks.

No auto-update hooks or dependency downloads run on clone or generation.
Introduce executable behavior only for a demonstrated need and document its
side effects. Treat source files and source catalogs as data during review.
