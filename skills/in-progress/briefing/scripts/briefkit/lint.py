"""Shape lint for brief.md. Filled in by the lint slice; this stub passes everything."""


def lint_file(md_path):
    return []


def report(problems, stream=None):
    import sys
    stream = stream or sys.stderr
    for p in problems:
        stream.write(f"{p}\n")
