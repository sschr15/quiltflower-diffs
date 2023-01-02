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

## Why are there no diffs against older Quiltflower versions?

Many older versions have issues that prevent them from not failing too hard against the test cases. 1.4 and 1.5 both have this issue -
specifically not knowing how to decompile invokedynamic items from constant pools. 1.3 and earlier either don't exist as Quiltflower
releases or have been lost to the sands of time. 1.6 is special...

## Why is there no diff against Quiltflower 1.6?

Quiltflower 1.6 is an interesting beast. It's new enough that it can at least not fail catastrophically against the test cases, but
it's old enough that it has another hard issue that plagues most versions before 1.7. It comes across "1.6.0" as the "output location"
when running via these scripts, but it interprets any output location as a jarfile. This *sounds* like it shouldn't cause any issues,
but pre-1.7, Quiltflower (as well as its parents ForgeFlower and Fernflower) add erroneous empty files to the output jarfile
(when running the console decompiler). These files just "happen" to have the same names as directories in the file, so upon an attempt
to extract the jarfile, conflicts arise.

This issue is fixed in future versions.

### Wait, but the decompilaion step says it timed out?

Yes, it does. QF 1.6 ends up getting hung on something with the default QF settings. So does QF 1.7. QF *does* fully decompile in both,
but it gets hung on something that never finishes. To not waste time (and since there aren't that many test cases), the script just
times out after one fast minute.

## Why is the latest snapshot version always re-downloaded?

To ensure that we're for sure using the latest snapshot version, we always re-download it. This is because the way that a version is picked
in the script does not include information about what exact snapshot it is, just that it is a snapshot. It also (in the find-what-is-new part)
does not search the file tree to identify whatever snapshot has already been downloaded.

## Why should I have `natsort` installed?

`natsort` is a Python library that allows for natural sorting of strings. This is useful in this scenario, because according to traditional
alphanumeric sorting, `1.9.0` comes after `1.10.0`. However, this is not the case for Quiltflower versions (or any semantic versioning system,
for that matter). `natsort` allows for "natural" (or "human") sorting, which also works quite well for semantic versioning.

## Why is &lt;x&gt; version failing?

Quiltflower is not perfect. No Java decompiler is. QF just happens to be *really* good at decompiling Java code, especially in the most recent
versions. However, it still has its issues. Some of these issues are due to the test cases themselves, and some are due to Quiltflower itself.
For example, there are a couple of test cases that intentionally fail, such as `TestRecursiveLambda` or `TestTryReturn`'s `testParsingFailure`.
These are in large part meant to catch erroneous bugs that wouldn't show up in normal code and could instead cause QF to throw up in more
severe manners instead of a simple illegal state or parsing exception. These should never happen in reasonably written code.

These scripts aren't perfect either. By the time you're reading this, my [improved options PR](https://github.com/QuiltMC/quiltflower/pull/235)
may have been merged, which completely changes the way that options are handled. If this is the case, then manually running `GenQfPreferences.java`
should be enough to generate a new `qf_prefs.py` file, assuming that version 1.9 or earlier exists in the `jars` directory.

Future versions may also decompile some of the test cases in rather unexpected ways. For example, the tests contain a plethora of classes which
are actually compiled versions of Kotlin code. QF's future plugin system allows for Kotlin decompilation (to some extent), so these classes may
create rather large diffs.
