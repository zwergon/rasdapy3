
import os
from rasdapy.models.ras_storage_layout import RasStorageLayOut
from rasdapy.models.ras_gmarray import RasGMArray, MInterval
from rasdapy.models.sinterval import SInterval


class FileStorageLayout(RasStorageLayOut):

    def __init__(self, topdir, files, reader):
        RasStorageLayOut.__init__(self)
        self.topdir = topdir
        self.files = files
        self.reader = reader

    def decompose_mdd(self, gm_array):
        return FilesMDDIterator(gm_array, self)


class FilesMDDIterator:

    def __init__(self, gm_array, layout):
        self.layout = layout
        self.gm_array = gm_array
        self.storage_intervals =layout.spatial_domain.intervals

    def __iter__(self):
        for z, file in enumerate(self.layout.files):
            array = self.layout.reader(os.path.join(self.layout.topdir, file))
            byte_size = array.size*self.gm_array.type_length
            if byte_size > RasStorageLayOut.DEFAULT_TILE_SIZE:
                raise Exception(f"tile size {byte_size} is bigger than maximum {RasStorageLayOut.DEFAULT_TILE_SIZE} size")

            ras_array = RasGMArray()
            interval = SInterval(z, z)
            ras_array.spatial_domain = MInterval([interval, self.storage_intervals[1], self.storage_intervals[2]])
            ras_array.storage_layout = RasStorageLayOut(self.gm_array.type_length, ras_array.spatial_domain)
            ras_array.type_name = self.gm_array.type_name
            ras_array.type_length = self.gm_array.type_length
            ras_array.data = bytes(array)
            yield ras_array




