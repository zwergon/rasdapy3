
from rasdapy.models.ras_gmarray import RasGMArray
import numpy as np
from rasdapy.models.sinterval import SInterval
from rasdapy.models.minterval import MInterval
from rasdapy.cores.utils import get_tiling_domain
from rasdapy.models.ras_storage_layout import RasStorageLayOut


class NumpyGMArray(RasGMArray):



    def __init__(self, array: np.array, tile_size=RasStorageLayOut.DEFAULT_TILE_SIZE):
        shape = array.shape
        intervals = []
        for i_max in shape:
            intervals.append(SInterval(0, i_max-1))

        self.spatial_domain = MInterval(intervals)

        dtype = array.dtype
        if dtype.name not in self.type_dict.keys():
            raise Exception("this type is not a standard rasdaman type")
        self.type_name = self.type_dict[dtype.name][len(shape)]
        self.type_length = dtype.itemsize

        self.data = bytes(array)

        tile_domain = get_tiling_domain(self.spatial_domain.cardinality, self.type_length, tile_size)
        self.storage_layout = RasStorageLayOut(tile_domain, tile_size)


if __name__ == '__main__':
    a = np.arange(12).reshape((4, 3))
    numpy_array = NumpyGMArray(a)


