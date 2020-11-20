from unittest import TestCase
from rasdapy.models.minterval import MInterval
from rasdapy.models.sinterval import SInterval


class TestMInterval(TestCase):

    def test_cell_offset(self):
        minterval = MInterval.from_str("[0:511, 0:511, 0:253]")
        ori = (255, 255, 127)
        offset = minterval.cell_offset(ori)
        ret = minterval.cell_point(offset)
        print(ori, offset, ret)

        ori = (0, 0, 0)
        offset = minterval.cell_offset(ori)
        ret = minterval.cell_point(offset)
        print(ori, offset, ret)

        ori = (1, 0, 0)
        offset = minterval.cell_offset(ori)
        ret = minterval.cell_point(offset)
        print(ori, offset, ret)

        ori = (0, 1, 0)
        offset = minterval.cell_offset(ori)
        ret = minterval.cell_point(offset)
        print(ori, offset, ret)

        ori = (0, 0, 1)
        offset = minterval.cell_offset(ori)
        ret = minterval.cell_point(offset)
        print(ori, offset, ret)

    def test_cartesian_product(self):
        i1 = SInterval(200, 210)
        i2 = SInterval(300, 305)
        i3 = SInterval(400, 400)
        m = MInterval([i1, i2, i3])

        l = m.cartesian_product()
        print(l)