import struct
from pygame.math import Vector2 as vec2
#Like in C
from data_types import *

class WADReader:
    def __init__(self, wad_path) -> None:
        self.wad_file = open(wad_path, 'rb')
        self.header = self.read_header()
        self.directory = self.read_directory()
        # print("---WAD FILE INFO---",'\n', self.header)
        # print("---DIRECTORY INFO---")
        # [print('\n', i) for i in self.directory]
    
    def read_node(self, offset):
        # 28 bytes = 2 * 12H + 2 * 2H
        node = Node()
        read_2_bytes = self.read_2_bytes

        node.x_partition = read_2_bytes(offset, byteformat='h')
        node.y_partition = read_2_bytes(offset+2, byteformat='h')
        node.dx_partition = read_2_bytes(offset+4, byteformat='h')
        node.dy_partition = read_2_bytes(offset+6, byteformat='h')

        node.bbox['front'].top = read_2_bytes(offset+8, byteformat='h')
        node.bbox['front'].bottom = read_2_bytes(offset+10, byteformat='h')
        node.bbox['front'].left = read_2_bytes(offset+12, byteformat='h')
        node.bbox['front'].right = read_2_bytes(offset+14, byteformat='h')

        node.bbox['back'].top = read_2_bytes(offset+16, byteformat='h')
        node.bbox['back'].bottom = read_2_bytes(offset+18, byteformat='h')
        node.bbox['back'].left = read_2_bytes(offset+20, byteformat='h')
        node.bbox['back'].right = read_2_bytes(offset+22, byteformat='h')

        node.front_child_id = read_2_bytes(offset+24, byteformat='H')
        node.back_child_id = read_2_bytes(offset+26, byteformat='H')
        return node

    def read_sub_sector(self, offset):
        read_2_bytes = self.read_2_bytes
        sub_sector = Subsector()
        sub_sector.seg_count = read_2_bytes(offset, byteformat='h')
        sub_sector.first_seg_id = read_2_bytes(offset, byteformat='h')
        return sub_sector

    def read_segment(self, offset):
        read_2_bytes = self.read_2_bytes
        seg = Seg()
        
        seg.start_vertex_id = read_2_bytes(offset, byteformat='h')
        seg.end_vertex_id = read_2_bytes(offset+2, byteformat='h')
        seg.angle = read_2_bytes(offset+4, byteformat='h')
        seg.linedef_id = read_2_bytes(offset+6, byteformat='h')
        seg.direction =  read_2_bytes(offset+8, byteformat='h')
        seg.offset = read_2_bytes(offset+10, byteformat='h')
        return seg

    def read_thing(self, offset):
        read_2_bytes = self.read_2_bytes
        thing = Thing()
        
        x = read_2_bytes(offset, byteformat='h')
        y = read_2_bytes(offset+2, byteformat='h')
        thing.angle = read_2_bytes(offset+4, byteformat='H')
        thing.type = read_2_bytes(offset+6, byteformat='H')
        thing.flags = read_2_bytes(offset+8, byteformat='H')
        thing.pos = vec2(x,y)
        return thing

    def read_linedef(self, offset):
        #Linedefs are walls beetween vertexes
        self.read_2_bytes
        linedef = Linedef()
        linedef.start_vertex_id = self.read_2_bytes(offset, byteformat='H')
        linedef.end_vertex_id = self.read_2_bytes(offset + 2, byteformat='H')
        linedef.flags = self.read_2_bytes(offset + 4, byteformat='H')
        linedef.line_type = self.read_2_bytes(offset + 6, byteformat='H')
        linedef.sector_tag = self.read_2_bytes(offset + 8, byteformat='H')
        linedef.front_sidedef_id = self.read_2_bytes(offset + 10, byteformat='H')
        linedef.back_sidedef_id = self.read_2_bytes(offset + 12, byteformat='H')
        return linedef

    def  read_header(self):
            return {
                'wad_type':self.read_string(offset=0,num_bytes=4),
                'lump_count':self.read_4_bytes(offset=4),
                'init_offset':self.read_4_bytes(offset=8)
            }
    
    def read_directory(self):
        #Reading 16 bytes for all lumps
        directory = []
        for i in range(self.header['lump_count']):
            offset =self.header['init_offset'] + i * 16
            lump_info = {
                'lump_offset': self.read_4_bytes(offset),
                'lump_size':self.read_4_bytes(offset+4),
                'lump_name':self.read_string(offset+8, num_bytes=8)
            }
            directory.append(lump_info)
        return directory

    def read_vertex(self, offset):
        # 4 bytes = 2h + 2h
        x = self.read_2_bytes(offset, byteformat='h')
        y = self.read_2_bytes(offset + 2, byteformat='h')
        return vec2(x,y)

    def read_1_byte(self, offset, byteformat = 'B'):
        return self.read_bytes(offset=offset, num_bytes = 1, byte_format=byteformat)[0]

    def read_2_bytes(self, offset, byteformat):
        #Vertexes x,y
        #H - uint16, h - int16
        return self.read_bytes(offset=offset, num_bytes=2, byte_format=byteformat)[0]
    
    def read_4_bytes(self, offset, byte_format='i'):
        #I - uint32 without +/- , i - int32
        return self.read_bytes(offset=offset, num_bytes=4, byte_format=byte_format)[0]

    def read_string(self, offset, num_bytes):
        #c - char
        return ''.join(b.decode('ascii') for b in self.read_bytes(offset, num_bytes, byte_format='c'*num_bytes)
                       if ord(b)!= 0).upper() 

    def read_bytes(self, offset, num_bytes, byte_format):
        self.wad_file.seek(offset)
        buffer = self.wad_file.read(num_bytes)
        return struct.unpack(byte_format, buffer)

    def close(self):
        self.wad_file.close()