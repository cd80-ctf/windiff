import glob
import os
import os.path

import typer


from delta_utils import get_delta_file_list_v1, get_delta_file_list_v2
from extract_utils import extract_deltas, extract_manifest_from_cab, extract_windows_archive
from rich_utils import error


def main(archive_filepath: str, manifest_path: str = None, out_dir: str = None, extract_version: int = 2):
    if len(archive_filepath) < 4:
        error("Archive filepath is too short!")
        return

    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(archive_filepath), "deltas")

    # Step 1: Get the manifest file, either directly or by extracting some archives
    if archive_filepath[-4:] == ".msu":
        extracted_msu = extract_windows_archive(archive_filepath)
        psf_files = glob.glob(os.path.join(extracted_msu, "*.psf"))
        if len(psf_files) != 1:
            error("Found unexpected number of PSF files in extracted MSU!")
            error(f"PSF files found: {psf_files}")
            return
        psf_file = psf_files[0]

        manifest_path, psf_file = extract_manifest_from_cab(psf_file[:-3] + "cab")
        if not manifest_path:
            error(f"Failed to extract manifest from CAB at {manifest_path}")
            return
    elif archive_filepath[-4:] == ".cab":
        manifest_path, psf_file = extract_manifest_from_cab(archive_filepath)
        if not os.path.exists(manifest_path):
            error(f"Failed to extract manifest from CAB file at {archive_filepath}")
            return
    elif archive_filepath[-4:] == ".psf":
        if manifest_path is None:
            error("Must manually specify manifest with PSF file!")
            return
        elif not os.path.exists(manifest_path):
            error(f"Could not find specified manifest {manifest_path}")
            return

        psf_file = archive_filepath
    else:
        error(f"Unrecognized file type {archive_filepath} (must be msu, cab, or psf)")
        return

    # Step 2: Get the list of file deltas from the manifest
    if extract_version == 1:
        delta_file_list = get_delta_file_list_v1(manifest_path)
    elif extract_version:
        delta_file_list = get_delta_file_list_v2(manifest_path)
    else:
        error(f"Unsupported extract version {extract_version}! (supported: 1, 2 | default: 2)")
        return

    extract_deltas(psf_file, delta_file_list, out_dir)


if __name__ == '__main__':
    typer.run(main)
