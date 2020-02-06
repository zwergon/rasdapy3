from mcube.mongo_io import MongoIO
from mcube.header import Header
from time import time


class DRPHeader(Header):
    columns = ["plug", "energy"]

    def __init__(self, plug, energy, **kwargs):
        Header.__init__(self, plug=plug, energy=energy, **kwargs)


def read_drp(
        plug=4232,
        energy='100kV'):

    with MongoIO(db_name="drp4ml") as img_io:
        header = DRPHeader(plug=plug, energy=energy)
        print(f".read ({header.plug}, {header.energy}) cube")
        t1 = time()
        img = img_io.read(header)
        t2 = time()
        print('.. %f seconds for reading' % (t2 - t1))

    return img