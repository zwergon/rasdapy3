import os
from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np

from rasdapy.db_connector import DBConnector
from rasdapy.models.ras_gmarray_builder import RasGMArrayBuilder
from rasdapy.query_executor import QueryExecutor


class TestQueryExecutor(TestCase):

    def import_png(self, png_filename):
        q_result = self.query_executor.execute_update_from_file("insert into mr values decode($1)", png_filename)
        if not q_result.error():
            elts = q_result.get_elements()
            print(elts)
            return elts[0]
        else:
            print(q_result.error_message())

    @staticmethod
    def create_uint8_array(nx, ny, nz, with_scaling=True):
        a = np.arange(nx * ny * nz, dtype=np.uint8).reshape((nx, ny, nz))
        if with_scaling:
            a = a * 127 / (nx * ny * nz)

        print(a.dtype.byteorder)
        return RasGMArrayBuilder.from_np_array(a.astype(np.uint8))

    @staticmethod
    def create_3d_array(nx, ny, nz):
        array = np.zeros(shape=(nx, ny, nz), dtype=np.dtype('f4'))
        print(array.strides)
        value = 0.
        increment = 255. / (nx * ny * nz)
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                for k in range(array.shape[2]):
                    array[i, j, k] = value
                    value += increment

        print(array.dtype.byteorder)
        plt.imshow(array[100, :, :])
        plt.show()

        return RasGMArrayBuilder.from_np_array(array)

    def __init__(self, *args, **kwargs):
        super(TestQueryExecutor, self).__init__(*args, **kwargs)
        self.host = 'irlinv-dvbacr16'
        self.db_connector = DBConnector(self.host, 7001, "rasadmin", "rasadmin")
        self.query_executor = QueryExecutor(self.db_connector)
        self.db_connector.open()

    def test_png(self):
        self.query_executor.execute_write("create collection mr GreySet")
        oid = self.import_png(os.path.join("../data", "mr_1.png"))
        result = self.query_executor.execute_read(f"select a from mr as a where oid(a)={oid}")
        array = result.to_array()
        plt.imshow(array)
        plt.show()
        self.query_executor.execute_write("drop collection mr")

    def test_array_uint8(self):
        ras_array = self.create_uint8_array(4, 3, 2, False)
        print(ras_array)
        print(ras_array.data)
        self.query_executor.execute_write("create collection greycube GreySet3")
        q_result = self.query_executor.execute_query("insert into greycube values $1", ras_array)
        if not q_result.error():
            elts = q_result.get_elements()
            print(elts)
            oid = elts[0]

            result = self.query_executor.execute_read(f"select a[1,*:*,*:*]  from greycube as a where oid(a)={oid}")
            array = result.to_array()
            print(array)
            print(array.shape)
        self.query_executor.execute_write("drop collection greycube")

    def test_array_float(self):
        ras_array = self.create_3d_array(182, 180, 60)
        self.query_executor.execute_write("create collection floatcube FloatSet3")
        q_result = self.query_executor.execute_query("insert into floatcube values $1", ras_array)
        if not q_result.error():
            elts = q_result.get_elements()
            print(elts)
            oid = elts[0]

            result = self.query_executor.execute_read(f"select a[150,*:*,*:*]  from floatcube as a where oid(a)={oid}")
            array = result.to_array()
            plt.imshow(array[:, :])
            plt.show()
        self.query_executor.execute_write("drop collection floatcube")