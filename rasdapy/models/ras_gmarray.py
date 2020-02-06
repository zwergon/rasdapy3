"""
 *
 * This file is part of rasdaman community.
 *
 * Rasdaman community is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Rasdaman community is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU  General Public License for more details.
 *
 * You should have received a copy of the GNU  General Public License
 * along with rasdaman community.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Copyright 2003 - 2016 Peter Baumann / rasdaman GmbH.
 *
 * For more information please see <http://www.rasdaman.org>
 * or contact Peter Baumann via <baumann@rasdaman.com>.
 *
"""

import math
import numpy as np
from rasdapy.models.sinterval import SInterval
from rasdapy.models.minterval import MInterval
from rasdapy.cores.utils import get_tiling_domain
from rasdapy.models.ras_storage_layout import RasStorageLayOut
from rasdapy.models.mdd_types import rDataFormat


class RasGMArray(object):

    type_dict = {
        "bool" : {
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
        "uint16" : {
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

    """
    This class represents a generic MDD in the sense that it
    is independent of the cell base type. The only information
    available is the length in bytes of the base type.
    """
    DEFAULT_MDD_TYPE = "GreyString"

    # if type_length is not specified, consider it is char (1 byte)
    DEFAULT_TYPE_LENGTH = 1

    # this size is related to max size that can be sent via gRPC
    MAX_MDD_SIZE = 524288

    def __init__(self, spatial_domain=None, type_name=None, type_length=DEFAULT_TYPE_LENGTH, data=None, storage_layout=None):
        """
        :param MInterval spatial_domain: the domain of this array
        :param str type_name: the name of array's type
        :param int type_length: length of the cell base type in bytes (e.g: char: 1 byte, short: 2 bytes, long: 4 bytes)
        :param long tile_size: the current tile size in bytes (optional)
        :param byte[] data: the binary data in 1D array
        :param RasStorageLayout: storage layout object to store the tile domain, tile size
        """
        # e.g: "insert into test_grey3D values $1" -f "/home/rasdaman/tmp/50k.bin" --mdddomain [0:99,0:99,0:4] --mddtype GreyCube
        # mdddomain (spatial_domain): the domain of inserting marray (e.g: [0:99,0:99,0:4])
        # mddtype (type_name): the type of inserting marray (e.g: GreyCube)
        self.spatial_domain = spatial_domain
        self.type_name = type_name
        self.type_length = type_length
        self.format = rDataFormat.r_Array
        self.data = data
        self.storage_layout = storage_layout

    @property
    def data_length(self):
        return len(self.data)

    def from_np_array(self, array : np.array):
        shape = array.shape
        intervals = []
        for i_max in shape:
            intervals.append(SInterval(0, i_max - 1))

        self.spatial_domain = MInterval(intervals)

        dtype = array.dtype
        if dtype.name not in self.type_dict.keys():
            raise Exception("this type is not a standard rasdaman type")
        self.type_name = self.type_dict[dtype.name][len(shape)]
        self.type_length = dtype.itemsize

        self.data = bytes(array)

        tile_domain = self._get_tiling_domain(self.MAX_MDD_SIZE)
        self.storage_layout = RasStorageLayOut(tile_domain, self.MAX_MDD_SIZE)

    def decompose_mdd(self):
        storage_intervals = MInterval.from_str(self.storage_layout.spatial_domain).intervals
        bytes_incr = self._get_hyper_plane_bytesize()

        barray = bytearray(self.data)
        bytes_size = storage_intervals[0].width*bytes_incr

        offset = 0

        print(f"full size {self.data_length}")
        ras_array_list = []
        i_interval = SInterval(storage_intervals[0].lo, storage_intervals[0].hi)
        while offset + bytes_size <= self.data_length:
            print(f"get buffer from {offset} to {offset+bytes_size-1} with {i_interval}")
            ras_array = RasGMArray()
            ras_array.spatial_domain = MInterval([i_interval, storage_intervals[1], storage_intervals[2]])
            ras_array.storage_layout = self.storage_layout
            ras_array.type_name = self.type_name
            ras_array.type_length = self.type_length
            ras_array.data = bytes(barray[offset:offset+bytes_size-1])
            ras_array_list.append(ras_array)
            offset += bytes_size
            i_interval = SInterval(
                i_interval.lo + storage_intervals[0].width,
                i_interval.hi + storage_intervals[0].width
            )

        remaining_size = self.data_length - offset
        #TODO handle remaining bytes
        print( f"remaining_size {remaining_size}")

        return ras_array_list

    def _get_hyper_plane_bytesize(self):
        mintervals = self.spatial_domain.intervals

        bytes_incr = self.type_length
        for i in range(1, len(mintervals)):
            bytes_incr *= mintervals[i].width
        return bytes_incr

    def _get_tiling_domain(self,  max_size):
        dim = len(self.data)

        # Size is small enough, no need to split domain, use spatial domain.
        if dim <= max_size:
            return str(self.spatial_domain)

        mintervals = self.spatial_domain.intervals

        bytes_incr = self._get_hyper_plane_bytesize()

        if bytes_incr > self.MAX_MDD_SIZE:
            raise Exception(f"one plane is bigger than maximum {self.MAX_MDD_SIZE} size")

        i_dim = int(self.MAX_MDD_SIZE/bytes_incr)

        i_interval = mintervals[0]
        tile_domain = "0:" + str(i_dim - 1)
        for i in range(1, len(mintervals)):
            hi_value = mintervals[i].hi
            tile_domain = tile_domain + ",0:" + str(hi_value)
        tile_domain = "[" + tile_domain + "]"

        return tile_domain


