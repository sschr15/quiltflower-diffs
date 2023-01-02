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

`GenQfPreferences.java` is a small Java program that generates a `qf_prefs.py` file. The Python file contains a class
with all of the Quiltflower preferences, with a guess made on which Quiltflower version is the newest. This is used by
`main.py` to generate the preferences in order for most decompilation settings to be the same across all versions.

`test-cases.jar` is an archive containing many (but not all) of the test cases that are used to test Quiltflower.
Their sources can be found in the [Quiltflower repository](https://github.com/QuiltMC/quiltflower/tree/master/testData/src).

## What settings are set by default?

Most settings are whatever Quiltflower marks as default, to give the most accurate comparison. However, some versions
have defaults that vary in such a way that they add a lot of extra fluff to the diffs. These settings are set manually
to improve overall diff quality:

- Include Entire Classpath (true) - suggested by Quiltflower developers - cleans up decompilations a lot
- Decompile Generic Signatures (true) - makes Quiltflower decompile generic signatures (which it does not by default on older versions)
- Remove Synthetic Methods (false) - prevents Quiltflower from removing synthetic methods (which it does by default on more recent versions)
- Log Level (WARN) - Decreases verbosity of the logs in `logs/`
