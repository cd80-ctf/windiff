import xml.etree.ElementTree as xml_tree


from rich_utils import error


class DeltaInfo:
    def __init__(self, name, time, filetype, offset, length):
        self.name = name.lstrip("\\")
        self.time = time
        self.filetype = filetype
        self.offset = int(offset)
        self.length = int(length)


def uint_from_string(byte_array):
    stop_index = None
    for index, byte in enumerate(byte_array):
        if byte < 0x30 or byte > 0x40:
            stop_index = index
            break

    if stop_index is None:
        return None, None
    return int(byte_array[:stop_index].decode("ascii")), stop_index + 1


# UNTESTED, DON'T KNOW IF THIS WORKS
def get_delta_file_list_v1(manifest):
    with open(manifest, "rb") as f:
        manifest_data = f.readlines()

    current_filename = None
    delta_files = []
    for line in manifest_data:
        if not len(line):
            continue
        elif line[0] == "[":  # expect filenames in the format [filename]
            current_filename = line[1:-1]
        elif current_filename:
            if len(line) > 3 and line[:3] == b"p0=":
                filetype = "PA19"
                data_offset = 3
            elif len(line) > 5 and line[:5] == b"full=":
                filetype = "RAW"
                data_offset = 5
            else:
                error(f"Invalid line found in v1 manifest: {line}")
                return None

            size, new_data_offset = uint_from_string(line[data_offset:])
            if size is None:
                error(f"Unable to parse size for file {current_filename} in v1 manifest")
                return None

            offset, _ = uint_from_string(line[data_offset + new_data_offset:])
            if size is None:
                error(f"Unable to parse size for file {current_filename} in v1 manifest")
                return None

            delta_files.append(DeltaInfo(current_filename, 0, filetype, size, offset))
            current_filename = None

    return delta_files


# implicitly assuming windows update manifests will not contain a billion laughs
def get_delta_file_list_v2(manifest):
    manifest_data = xml_tree.parse(manifest)

    files_root = manifest_data.getroot().find("Files", {'': "urn:ContainerIndex"})
    if files_root is None:
        error(f"Unable to find files root in XML manifest {manifest}")
        return None

    delta_files = []
    for file in files_root.findall("File", {'': "urn:ContainerIndex"}):
        delta = file.find("Delta", {'': "urn:ContainerIndex"})
        if not delta:
            continue

        source = delta.find("Source", {'': "urn:ContainerIndex"})
        if not source:
            continue

        delta_files.append(DeltaInfo(file.get("name"), file.get("time"), source.get("type"), source.get("offset"), source.get("length")))

    return delta_files
