# Research integrity and reproducibility

This project distinguishes infrastructure validation from scientific
validation. A completed Slurm job or a passing fixture verifies a workflow
path; it does not validate a scientific question, model, or result.

## Required record for a scientific run

Create an ignored run record and a reviewed metadata summary that identify:

- the scientific question, input dataset version, expected outputs, and
  acceptance criteria before submission;
- Git commit, release tag, exact command, UTC timestamps, system, allocation,
  job ID, and Globus task IDs;
- input, configuration, and output checksums;
- application version, relevant modules, container digest when used, and random
  seed; and
- data source, classification, authorization or license, transfer lineage,
  durable storage location, and retention plan.

Keep raw inputs immutable and separate from derived outputs. Large data and
full execution logs remain outside Git; commit a compact metadata summary and
checksums that make the external artifacts identifiable.

## Validation standard

Define scientific acceptance criteria before the run. Require both the expected
scheduler/transfer state and the domain-specific validation result. Repeat a
scientific payload from a clean checkout or separate environment before calling
the result reproducible.

Before an external release, select a license, maintain `CITATION.cff`, archive
the durable data and software artifacts, and document their persistent location.

## Sources

- Wilkinson et al., [The FAIR Guiding Principles for scientific data management
  and stewardship](https://doi.org/10.1038/sdata.2016.18), *Scientific Data*
  3, 160018 (2016). FAIR calls for rich metadata, detailed provenance, clear
  data-use licensing, and domain-relevant standards.
- National Academies of Sciences, Engineering, and Medicine,
  [Reproducibility and Replicability in Science](https://doi.org/10.17226/25303)
  (2019). It defines computational reproducibility in terms of the same data,
  code, computational steps, and analysis conditions.
- [Citation File Format schema guide](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md).
  It specifies the machine- and human-readable `CITATION.cff` metadata format.
