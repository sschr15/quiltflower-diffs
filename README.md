# quiltflower-diffs

Essentially just a collection of `diff` files to compare how Quiltflower's
various releases compare with each other.

## Diff Generation Process

1. Ensure that the `natsort` Python library is installed for best results.
2. Run `python3 main.py` to download Quiltflower releases and run them through the `test-cases.jar` file.
3. Run `python3 clean_decomp.py` to remove line numbers from any exceptions that were thrown. This keeps the diffs cleaner.
4. Run `python3 gen_diffs.py` to generate the diffs. This will create a `diffs` directory with the diffs for each release against the latest release.
