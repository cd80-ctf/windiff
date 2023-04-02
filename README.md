# windiff

Windiff is a tool for extracting forward differentials from Windows cumulative updates. In the past, this could be done simply by extracting the update's `.cab` files. However, more recent updates only store metadata in the `.cab` file, while the actual diffs are stuffed into a `.psf` file with the same name. Windiff essentially produces the same output from this format as extracting the `.cab` did on the previous format; that is, a folder full of directories forward differentials. These could then be applied using any methods that worked on previous Windows updates.

This is essentially a Python port of the excellent [PSFExtractor](https://github.com/Secant1006/PSFExtractor) tool (mostly because I didn't want to compile it myself). There may be bugs!

## Quickstart:

(note that this only works on Windows, since we need to call the `msdelta` API)

```python
git clone https://github.com/cd80-ctf/windiff && cd windiff
pip install -r requirements.txt
python windiff.py windows-update.msu
```

## Full API:

Windiff can be called on three different types of files:

1) A raw `.msu` update file: `python windiff.py windows-update.msu`
2) An extracted `.cab` file: `python windiff.py windows-update.cab`. Note that this assumes the matching `.psf` file sits in the same directory as the specified `.cab` file and has the same name. In most cases, it will usually be easier to use option 1.
3) Manually passing a `.psf` file and an XML manifest: `python windiff.py windows-update.psf --manifest_path express.psf.cix.xml`. This assumes you have already extracted the desired XML manifest from the CAB file, or from some other source.

By default, the deltas are extracted a new `deltas` folder in the same directory as the input file. However, this can be changed by passing the `--out_dir` flag.

Furthermore, older `.cab` files can be extracted using `--extract_version 1`.
