import struct,unittest
from validate_loader import validate

def fixture():
    image=bytearray(0x4000)
    flags=0x10003;magic=0x1badb002
    struct.pack_into('<8I',image,0x900,magic,flags,(-magic-flags)&0xffffffff,0x200900,0x200000,0,0,0x201000)
    image[0x800:0x802]=b'MZ';struct.pack_into('<I',image,0x83c,0x40)
    image[0x840:0x844]=b'PE\0\0';struct.pack_into('<H',image,0x844,0x14c)
    struct.pack_into('<H',image,0x858,0x10b);struct.pack_into('<I',image,0x890,0x5000)
    return image

class LoaderConstraints(unittest.TestCase):
    def test_valid_layout(self): self.assertEqual(validate(fixture())['relocated_pe_end'],'0x15000')
    def test_invalid_checksum(self):
        data=fixture();data[0x908]^=1
        with self.assertRaises(ValueError): validate(data)
    def test_oversized_loader(self):
        with self.assertRaises(ValueError): validate(fixture()+bytearray(0x80000))
    def test_entry_outside_loaded_image(self):
        data=fixture();struct.pack_into('<I',data,0x91c,0x300000)
        with self.assertRaises(ValueError): validate(data)
    def test_wrong_cpu_architecture(self):
        data=fixture();struct.pack_into('<H',data,0x844,0x8664)
        with self.assertRaises(ValueError): validate(data)
    def test_low_memory_overflow(self):
        data=fixture();struct.pack_into('<I',data,0x890,0xa0000)
        with self.assertRaises(ValueError): validate(data)
    def test_header_outside_search_window(self):
        data=fixture();data[0x3000:0x3020]=data[0x900:0x920];data[0x900:0x920]=bytes(32)
        with self.assertRaises(ValueError): validate(data)

if __name__=='__main__': unittest.main()
