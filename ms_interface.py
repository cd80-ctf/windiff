from ctypes import (windll, wintypes, c_uint64, cast, POINTER, Union, c_ubyte,
                    LittleEndianStructure, byref, c_size_t)
from rich_utils import error

# types and flags
DELTA_FLAG_TYPE = c_uint64
DELTA_FLAG_NONE = 0x00000000
DELTA_APPLY_FLAG_ALLOW_PA19 = 0x00000001


# structures
class DELTA_INPUT(LittleEndianStructure):
    class U1(Union):
        _fields_ = [('lpcStart', wintypes.LPVOID),
                    ('lpStart', wintypes.LPVOID)]

    _anonymous_ = ('u1',)
    _fields_ = [('u1', U1),
                ('uSize', c_size_t),
                ('Editable', wintypes.BOOL)]


class DELTA_OUTPUT(LittleEndianStructure):
    _fields_ = [('lpStart', wintypes.LPVOID),
                ('uSize', c_size_t)]


# functions
ApplyDeltaB = windll.msdelta.ApplyDeltaB
ApplyDeltaB.argtypes = [DELTA_FLAG_TYPE, DELTA_INPUT, DELTA_INPUT,
                        POINTER(DELTA_OUTPUT)]
ApplyDeltaB.rettype = wintypes.BOOL
DeltaFree = windll.msdelta.DeltaFree
DeltaFree.argtypes = [wintypes.LPVOID]
DeltaFree.rettype = wintypes.BOOL
gle = windll.kernel32.GetLastError


def delta_apply_wrapper(delta_info, delta, output_path):
    source_struct = DELTA_INPUT()
    source_struct.lpcStart = 0
    source_struct.uSize = 0
    source_struct.Editable = False

    delta_struct = DELTA_INPUT()
    delta_struct.lpcStart = cast(delta, wintypes.LPVOID)
    delta_struct.uSize = len(delta)
    delta_struct.Editable = False

    output_struct = DELTA_OUTPUT()
    delta_apply_flags = DELTA_APPLY_FLAG_ALLOW_PA19 if delta_info.filetype == "PA19" else DELTA_FLAG_NONE
    delta_apply_status = ApplyDeltaB(delta_apply_flags, source_struct, delta_struct, byref(output_struct))
    if delta_apply_status == 0:
        error(f"Failed to apply delta to file {delta_info.name} (error: {gle()})")
        return False

    output_bytes = bytes((c_ubyte * output_struct.uSize).from_address(output_struct.lpStart))
    with open(output_path, "wb") as f:
        f.write(output_bytes)

    DeltaFree(output_struct.lpStart)
    return True
