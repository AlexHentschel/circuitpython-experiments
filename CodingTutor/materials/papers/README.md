# materials/papers/ — local, git-ignored

This folder holds **downloaded academic papers and books** obtained via academic-library / paywalled access. Everything
here is **git-ignored by default** (see `../../.gitignore`) because it is third-party copyrighted material that must not
be redistributed on a public repo.

Only this `README.md` is tracked.

## Workflow when adding a source here
1. Drop the file in this folder (it is ignored automatically).
2. Add a full citation to `../../REFERENCES.md` (§ Learning-science sources or the appropriate section), including:
   author(s), year, title, venue, DOI/URL, and **where the file lives locally** (`materials/papers/<filename>`).
3. Record its **license / redistribution status** in `../../REFERENCES.md` (§ Licensing & redistribution).
4. Cite it from any digest/notes that rely on it (our digests are our own writing and *are* committed).

## If (and only if) a source is permissively licensed for redistribution
Confirm the license (e.g. open access CC-BY, or explicit author permission), record it in `REFERENCES.md`, then
force-add the file so it is committed despite the ignore rules:

```
git add -f materials/papers/<filename>
```

Default assumption is **not redistributable** — when in doubt, leave it ignored and keep only the citation + our digest.
