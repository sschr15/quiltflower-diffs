# quiltflower-diffs

Essentially just a collection of `diff` files to compare how Quiltflower's
various releases compare with each other.

## Diff Generation Process

1. Ensure that the `natsort` Python library is installed for best results.
2. Run `python3 main.py` to download Quiltflower releases and run them through the `test-cases.jar` file.
3. Run `python3 clean_decomp.py` to remove line numbers from any exceptions that were thrown. This keeps the diffs cleaner.
4. Run `python3 gen_diffs.py` to generate the diffs. This will create a `diffs` directory with the diffs for each release against the latest release.

## What are those other files?
`find_qf_issues.py` returns for every function a list of notes that Quiltflower adds as comments.
This is useful for finding functions that Quiltflower has trouble decompiling or that it decompiles differently than expected.
It also contains helpful otherwise lost information such as if it is a synthetic and/or bridge method.
The Python script just prints every location where one of these notes is found.
