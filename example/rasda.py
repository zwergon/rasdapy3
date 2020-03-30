
import numpy as np
import os
import matplotlib.pyplot as plt

from rasdapy.query_executor import QueryExecutor
from rasdapy.cores.remote_procedures import *
from rasdapy.db_connector import DBConnector
from rasdapy.cores.utils import *
from rasdapy import ras_oqlquery
from rasdapy.models.ras_gmarray_builder import RasGMArrayBuilder
from rasdapy.query_result import QueryResult
from rasdapy.models.ras_storage_layout import  RasStorageLayOut


def dicom_read_array(filename):
    dataset = None # pydicom.dcmread(filename)
    return dataset.pixel_array


def create_files(topdir, root_name):
    files = []
    for r, d, f in os.walk(topdir):
        for file in f:
            if root_name in file:
                files.append(os.path.join(topdir, file))
    return files


def create_uint8_array(nx, ny, nz, with_scaling=True):
    a = np.arange(nx*ny*nz, dtype=np.uint8).reshape((nx, ny, nz))
    if with_scaling:
        a = a * 127 / (nx*ny*nz)

    print(a.dtype.byteorder)
    return RasGMArrayBuilder.from_np_array(a.astype(np.uint8))


def create_3d_array(nx, ny, nz):
    array = np.zeros(shape=(nx, ny, nz), dtype=np.dtype('f'))
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


def import_png( query_executor, png_filename ):
    q_result = query_executor.execute_update_from_file("insert into mr values decode($1)", png_filename)
    if not q_result.error():
        elts = q_result.get_elements()
        print(elts)
        return elts[0]
    else:
        print(q_result.error_message())

png_flag = True
array_uint8 = True
array_type_flag = True
drop_flag = True
mongo_flag = True
dicom_flag = False

if __name__ == '__main__':

    RasStorageLayOut.DEFAULT_TILE_SIZE = 100 * 1024 * 1024
    db_connector = DBConnector("localhost", 7001, "rasadmin", "rasadmin")
    query_executor = QueryExecutor(db_connector)
    db_connector.open()

    if array_type_flag:
        list_type = query_executor.execute_read("select c from RAS_MARRAY_TYPES as c")
        print(f"retrieves {list_type.size} types from rasdaman")
        for t in list_type:
            print(t)

    query_executor.execute_write("create collection gs1 GreySet1")

    if png_flag:
        query_executor.execute_write("create collection mr GreySet")
        oid = import_png(query_executor, "../data/mr_1.png")
        result = query_executor.execute_read(f"select a from mr as a where oid(a)={oid}")
        array = result.to_array()
        plt.imshow(array)
        plt.show()

    if drop_flag:
        query_executor.execute_write("create collection test GreySet1")
        list_collection = query_executor.execute_read("select c from RAS_COLLECTIONNAMES as c")
        for t in list_collection:
            print(t)

        query_executor.execute_write("drop collection test")
        list_collection = query_executor.execute_read("select c from RAS_COLLECTIONNAMES as c")
        for t in list_collection:
            print(t)

    if array_uint8:
        ras_array = create_uint8_array(4, 3, 2, False)
        print(ras_array)
        print(ras_array.data)
        query_executor.execute_write("create collection greycube GreySet3")
        q_result = query_executor.execute_query("insert into greycube values $1", ras_array)
        if not q_result.error():
            elts = q_result.get_elements()
            print(elts)
            oid = elts[0]

            result = query_executor.execute_read(f"select a[1,*:*,*:*]  from greycube as a where oid(a)={oid}")
            array = result.to_array()
            print(array)
            print(array.shape)

    if mongo_flag:

        ras_array = create_3d_array(182, 180, 60)
        query_executor.execute_write("create collection floatcube FloatSet3")
        q_result = query_executor.execute_query("insert into floatcube values $1", ras_array)
        if not q_result.error():
            elts = q_result.get_elements()
            print(elts)
            oid = elts[0]

            result = query_executor.execute_read(f"select a[150,*:*,*:*]  from floatcube as a where oid(a)={oid}")
            array = result.to_array()
            plt.imshow(array[:, :])
            plt.show()

        else:
            print(q_result.error_message())

    if dicom_flag:
        files = create_files("D:\\lecomtje\\Datas\\drp4ml\\serie1", "6804_002")
        ras_array = RasGMArrayBuilder.from_files(files, dicom_read_array)
        mdd_itr = ras_array.storage_layout.decompose_mdd(ras_array)
        q_result = query_executor.execute_query("insert into scube values $1", ras_array)
        if not q_result.error():
            elts = q_result.get_elements()
            print(elts)
            oid = elts[0]

            result = query_executor.execute_read(f"select a[128,*:*,*:*]  from scube as a where oid(a)={oid}")
            array = result.to_array()
            plt.imshow(array[:, :])
            plt.show()

        else:
            print(q_result.error_message())


    db_connector.close()

