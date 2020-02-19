
import os
import numpy as np
import pydicom
from rasdapy.models.sinterval import SInterval
from rasdapy.models.minterval import MInterval
from rasdapy.models.ras_storage_layout import BandStorageLayout
from rasdapy.models.ras_gmarray import RasGMArray
from file_storage_layout import FileStorageLayout


def dicom_read_array(filename):
    dataset = pydicom.dcmread(filename)
    return dataset.pixel_array


class RasGMArrayBuilder:

    type_dict = {
        "bool": {
            1: "BoolString",
            2: "BoolImage",
            3: "BoolCube"
        },
        "uint8": {
            1: "GreyString",
            2: "GreyImage",
            3: "GreyCube"
        },
        "int8": {
            1: "OctetString",
            2: "OctetImage",
            3: "OctetCube"
        },
        "int16": {
            1: "ShortString",
            2: "ShortImage",
            3: "ShortCube"
        },
        "uint16": {
            1: "UShortSring",
            2: "UShortImage",
            3: "UShortCube"
        },
        "int32": {
            1: "LongString",
            2: "LongImage",
            3: "LongCube"
        },
        "uint32": {
            1: "ULongString",
            2: "ULongImage",
            3: "ULongCube"
        },

        "float32": {
            1: "FloatString",
            2: "FloatImage",
            3: "FloatCube",
            4: "FloatCube4"
        },
        "double": {
            1: "DoubleString",
            2: "DoubleImage",
            3: "DoubleCube"
        },
        "cint16": {
            1: "CInt16Image"
        },
        "cint32": {
            1: "CInt32Image"
        },
        "cfloat32": {
            1: "Gauss1",
            2: "Gauss1Image"
        },
        "cfloat64": {
            1: "Gauss2",
            2: "Gauss2Image"
        }
    }

    @classmethod
    def get_type_name(cls, dtype, shape):
        if dtype.name not in RasGMArrayBuilder.type_dict.keys():
            raise Exception("this type is not a standard rasdaman type")
        return RasGMArrayBuilder.type_dict[dtype.name][len(shape)]

    @staticmethod
    def from_np_array(array: np.array):
        """
        :param array: the numpy array used to create this new RasGMArray
        :return: a RasGMArray
        """
        gm_array = RasGMArray()
        shape = array.shape
        intervals = []
        for i_max in shape:
            intervals.append(SInterval(0, i_max - 1))

        gm_array.spatial_domain = MInterval(intervals)

        gm_array.type_name = RasGMArrayBuilder.get_type_name(array.dtype, array.shape)
        gm_array.type_length = array.dtype.itemsize

        gm_array.data = bytes(array)

        storage_layout = BandStorageLayout()
        storage_layout.compute_spatial_domain(gm_array)

        gm_array.storage_layout = storage_layout

        return gm_array

    @staticmethod
    def from_dicom_dir(topdir, root_name):

        files = []
        for r, d, f in os.walk(topdir):
            for file in f:
                if root_name in file:
                    files.append(file)

        array = dicom_read_array(os.path.join(topdir, files[0]))

        gm_array = RasGMArray()

        shape = (len(files)-1,) + array.shape
        gm_array.spatial_domain = MInterval.from_shape(shape)

        gm_array.type_name = RasGMArrayBuilder.get_type_name(
            array.dtype,
            gm_array.spatial_domain.shape
        )

        gm_array.type_length = array.dtype.itemsize

        gm_array.data = b''

        storage_layout = FileStorageLayout(topdir, files, dicom_read_array)
        storage_layout.spatial_domain = MInterval.from_shape((1,) + array.shape)
        gm_array.storage_layout = storage_layout

        print(gm_array)
        return gm_array