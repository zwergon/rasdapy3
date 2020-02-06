
import numpy as np

from struct import *


def create_raw_data():
    array = np.array([0, 1, 127, 245], dtype=np.uint8)
    return bytes(array)


if __name__ == '__main__':

    r_data = b'\x02\x01set<long>\x00\x01\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00"\x01'
    by = unpack(">l", b'\000\000\036\001')
    by = unpack(">l", b'\000\004\000\000')
    print(by)

    raw_data = create_raw_data()
    print(raw_data)

    raw2 = pack('hhl', 1, 2, 3)
    print(raw2)
    for c in bytearray(raw2):
        print(c)


    with open("a1d_4_u8.raw", 'wb') as f:
        f.write(raw_data)