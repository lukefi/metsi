from pathlib import Path
from lukefi.metsi.app.app_types import SimResults
from lukefi.metsi.app.file_io import row_writer
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.domain.forestry_types import StandList

def mela_par_file(filepath: Path, stands: StandList):
    content = ['C_VARIABLES']
    reference_stand = next(iter(stands))
    content.extend([ k for k in reference_stand.additional_data.keys() ])
    single_par_row = "#".join(content)
    row_writer(filepath, [single_par_row])
