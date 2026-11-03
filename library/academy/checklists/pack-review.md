# Pack review checklist

- [ ] `pack.json` validates and the status matches the evidence.
- [ ] `SKILL.md` has a trigger-rich description and a read-by-task table.
- [ ] All six references have title, summary, and coverage frontmatter.
- [ ] The three variant pages exist.
- [ ] Every `[S:id]` resolves in the public manifest.
- [ ] Data files match their provenance hashes.
- [ ] Schematics are original and attribution is present.
- [ ] Lua kit and recipes load from `lua/lib`, or the declared harness scripts
      run and pass their field test.
- [ ] `tests/field-test.md` is a real procedure, not a placeholder.
- [ ] `CERTIFICATION.md` exists if the status is certified.
- [ ] The catalog and page index are fresh.
- [ ] No forbidden file or extension is present.
- [ ] The local manifest is gitignored.
- [ ] The user knows what is verified and what is pending.
