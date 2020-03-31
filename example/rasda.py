
import numpy as np
import os
import matplotlib.pyplot as plt

from rasdapy.query_executor import QueryExecutor
from rasdapy.db_connector import DBConnector
from rasdapy.models.ras_gmarray_builder import RasGMArrayBuilder
from rasdapy.models.ras_storage_layout import  RasStorageLayOut

# RasStorageLayOut.DEFAULT_TILE_SIZE = 100 * 1024 * 1024
ras_host = "localhost"
ras_port = 7001

png_flag = True
array_uint8 = True
array_float = True
files_flag = True
array_type_flag = True
drop_flag = True
update_flag = True


def read_tif_file(filename):
    return plt.imread(filename)


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


if __name__ == '__main__':

    data_dir = os.path.join(os.path.curdir, "../data")
    print(data_dir)

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
        oid = import_png(query_executor, os.path.join(data_dir, "mr_1.png"))
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

    if array_float:

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

    if files_flag:
        files = create_files(data_dir, "slice")
        print(files)
        query_executor.execute_write("create collection u16s3 UShortSet3")
        ras_array = RasGMArrayBuilder.from_files(files, read_tif_file)
        q_result = query_executor.execute_query(f"insert into u16s3 values $1", ras_array)
        if not q_result.error():
            elts = q_result.get_elements()
            oid = elts[0]
            print(f"stored oid :{oid}")

        result = query_executor.execute_read(f"select a[1,*:*,*:*]  from u16s3 as a where oid(a)={oid}")
        array = result.to_array()
        plt.imshow(array[:, :])
        plt.show()

    if update_flag:
        query_executor.execute_write("create collection u16s3 UShortSet3")
        q_result = query_executor.execute_query("insert into u16s3 values marray it in [0:0,0:0,0:0] values 0us", None)
        if not q_result.error():
            elts = q_result.get_elements()
            oid = elts[0]
            print(f"stored oid :{oid}")
        res = query_executor.execute_read(f"select sdom(c) from u16s3 as c where oid(c)={oid}")
        for i in res:
            print(i)
        query_executor.execute_update_from_file(
            f"update u16s3 as c set c[0,*:*,*:*] assign inv_tiff($1) where oid(c)={oid}",
            os.path.join(data_dir, "slice00000.tif"))
        query_executor.execute_update_from_file(
            f"update u16s3 as c set c[1,*:*,*:*] assign inv_tiff($1) where oid(c)={oid}",
            os.path.join(data_dir, "slice00001.tif"))
        res = query_executor.execute_read(f"select sdom(c) from u16s3 as c where oid(c)={oid}")
        for i in res:
            print(i)

    query_executor.execute_write("drop collection gs1")
    query_executor.execute_write("drop collection u16s3")
    query_executor.execute_write("drop collection greycube")
    query_executor.execute_write("drop collection mr")
    query_executor.execute_write("drop collection floatcube")

    db_connector.close()

