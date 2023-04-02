import os
import os.path
import subprocess


import constants as c
from ms_interface import delta_apply_wrapper
from rich_utils import error, info, warning


def extract_windows_archive(archive_file):
    archive_full_path = os.path.abspath(archive_file)

    out_dir = os.path.join(os.path.dirname(archive_full_path), f"extracted_{os.path.splitext(os.path.basename(archive_full_path))[0]}")

    if os.path.exists(out_dir):
        warning(f"Extracted archive at {out_dir} already exists. We will overwrite it.")
    else:
        os.mkdir(out_dir)

    subprocess.run(["expand", "-F:*", archive_full_path, out_dir])
    return out_dir


def extract_manifest_from_cab(cab_file):
    psf_file = cab_file[:-3] + "psf"
    if not os.path.exists(psf_file):
        error(f"Could not find PSF file corresponding to CAB file (expected at {psf_file})")
        return None

    extracted_cab = extract_windows_archive(cab_file)
    manifest_file = os.path.join(extracted_cab, c.MANIFEST_FILE)
    if not os.path.exists(manifest_file):
        error(f"Could not find manifest file in extracted CAB at {extracted_cab}")
        return None

    return manifest_file, psf_file


def extract_deltas(psf_file, delta_info_list, output_root_dir):
    with open(psf_file, "rb") as f:
        for delta_info in delta_info_list:
            f.seek(delta_info.offset)
            delta = f.read(delta_info.length)

            output_filepath = os.path.join(output_root_dir, delta_info.name)
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            if delta_info.filetype in ["PA19", "PA30"]:
                if not delta_apply_wrapper(delta_info, delta, output_filepath):
                    return False
            else:
                with open(output_filepath, "wb") as delta_file:
                    delta_file.write(delta)

            info(f"Extracted delta to {delta_info.name}")

    return True
