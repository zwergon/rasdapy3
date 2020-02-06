from rasdapy.db_connector import DBConnector
from rasdapy.query_executor import QueryExecutor
import numpy as np
from rasdapy.cores.remote_procedures import *
import matplotlib.pyplot as plt
from rasdapy.cores.utils import *
from rasdapy import ras_oqlquery
from rasdapy.models.np_gmarray import  NumpyGMArray
from rasdapy.models.ras_gmarray import RasGMArray

from read_mongo import read_drp
from query_result import  QueryResult

def import_raw(db_connector):
    tx = db_connector.db.transaction(rw=True)
    database = db_connector.db

    command_id = 11  # ras_oqlquery.RasOQLQuery.__COMMAND_QUERY_EXEC
    big_endian = ras_oqlquery.RasOQLQuery.BIG_ENDIAN

    bin_data = bytes(np.array([0, 12, 127, 245], dtype=np.int8))
    query = "insert into gs1 values #MDD1#"
    mdd_data = [
        int_to_bytes(1),
        str_to_encoded_bytes("GreyString"),
        str_to_encoded_bytes(""),
        int_to_bytes(1),
        str_to_encoded_bytes("[0:3]"),
        str_to_encoded_bytes("[0:127999]"),
        str_to_encoded_bytes("||0.0"),
        int_to_bytes(4)]
    mdd_bytes = b''.join(mdd_data) + bin_data

    request_query = "Command={}&ClientID={}&QueryString={}&Endianess={}" \
                    "&NumberOfQueryParameters={}&BinDataSize={}&BinData=".format(
        command_id, database.connection.session.clientId, query,
        big_endian, 1, len(mdd_bytes))

    raw = request_query.encode() + mdd_bytes

    print(raw)

    reply = rassrvr_begin_streamed_http_query(
        database.stub,
        database.connection.session.clientUUID,
        raw)

    tx.commit()

    q_result = QueryResult()
    q_result.from_streamed_response(reply)
    if not q_result.error():
        elts = q_result.get_elements()
        print(elts)
    else:
        print(q_result.error_message())


def create_uint8_array(nx, ny):
    a = np.arange(nx*ny).reshape((nx, ny))
    a = a * 127 / (nx*ny)

    return a.astype(np.uint8)

def create_3D_array(nx, ny, nz):
    array = np.zeros(shape=(nx, ny, nz), dtype=np.float32)
    print(array.strides)
    value = 0.
    increment = 255. / (nx * ny * nz)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            for k in range(array.shape[2]):
                array[i, j, k] = value
                value += increment
    ras_array = RasGMArray()
    ras_array.from_np_array(array)

    return ras_array


def import_png( query_executor, png_filename ):
    q_result = query_executor.execute_update_from_file("insert into mr values decode($1)", png_filename)
    if not q_result.error():
        elts = q_result.get_elements()
        print(elts)
        return elts[0]
    else:
        print(q_result.error_message())

raw_flag = False
png_flag = False
array_type_flag = False
drop_flag = False
mongo_flag = True

if __name__ == '__main__':
    db_connector = DBConnector("irlinv-rrbound", 7001, "rasadmin", "rasadmin")
    query_executor = QueryExecutor(db_connector)
    db_connector.open()

    if array_type_flag:
        list_type = query_executor.execute_read("select c from RAS_MARRAY_TYPES as c")
        print(f"retrieves {list_type.size} types from rasdaman")
        for t in list_type:
            print(t.decode())

    if raw_flag:
        import_raw(db_connector)

    if png_flag:
        oid = import_png(query_executor, "data/mr_1.png")
        result = query_executor.execute_read(f"select a from mr as a where oid(a)={oid}")
        array = result.to_array()
        plt.imshow(array)
        plt.show()

    if drop_flag:
        query_executor.execute_write("create collection test GreySet1")
        list_collection = query_executor.execute_read("select c from RAS_COLLECTIONNAMES as c")
        for t in list_collection:
            print(t.decode())

        query_executor.execute_write("drop collection test")
        list_collection = query_executor.execute_read("select c from RAS_COLLECTIONNAMES as c")
        for t in list_collection:
            print(t.decode())

    if mongo_flag:
        img = read_drp()
        ras_array = RasGMArray()
        ras_array.from_np_array(img.cube.astype(np.float32))
        q_result = query_executor.execute_insert("insert into scanner values $1", ras_array)
        if not q_result.error():
            elts = q_result.get_elements()
            print(elts)
            oid = elts[0]

            result = query_executor.execute_read(f"select a[*:*,*:*,50]  from scanner as a where oid(a)={oid}")
            array = result.to_array()
            plt.imshow(array[:, :])
            plt.show()

        else:
            print(q_result.error_message())

    # ras_array = create_3D_array(180, 180, 60)
    # print(ras_array.spatial_domain, ras_array.storage_layout.spatial_domain)
    # # ras_array.decompose_mdd()
    # q_result = query_executor.execute_insert("insert into scanner values $1", ras_array)
    # if not q_result.error():
    #     elts = q_result.get_elements()
    #     print(elts)
    #     oid = elts[0]
    # else:
    #     print(q_result.error_message())



    db_connector.close()

