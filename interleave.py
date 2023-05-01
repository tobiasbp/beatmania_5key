"""
Weave data from a number of ROM together in a single file.
"""

import numpy as np

from PIL import Image

width = 1

first_byte = 0
last_byte = 10

# Sprites
rom_files = [
    #"825-EA-A-A03.19a",
    #"825-EA-A-A04.20a",
    "825-EA-A-A05.22a",
    "825-EA-A-A06.24a"
]

def bits_to_int(bits):
    """
    Convert a list of bit values to an integer.
    Last bit in list is least significant.
    """
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    return value


def interleave(rom_files, no_of_bytes_to_read=None, bytes_pr_read=1):
    # List of bytes in the ROM files
    rom_bytes = []

    # Read bytes from the ROM files
    for file in rom_files:
        rom_bytes.append(np.fromfile(file, dtype=np.uint8))

    interleaved_bytes = []

    for byte_no in range(no_of_bytes_to_read):
        for rom_no in range(len(rom_bytes)):
            interleaved_bytes.append(rom_bytes[rom_no][byte_no])

    return np.array(interleaved_bytes)


def get_graphic(bytes,width=16, height=16, bits_pr_pixel=4, normalize=True):
    """
    12
    34
    """

    # Convert the bytes to a list of bits
    bits = np.unpackbits(bytes)
    
    assert len(bits) >= width*height*bits_pr_pixel, f"Not enough bits ({len(bits)}) to create graphic" 

    #x_offsets = (4, 0, 12, 8, 20, 16, 28, 24)
    x_offsets = (4, 0, 12, 8, 20, 16, 28, 24, 4+256, 0+256, 12+256, 8+256, 20+256, 16+256, 28+256, 24+256)
    #y_offsets = (0*32, 1*32, 2*32, 3*32, 4*32, 5*32, 6*32, 7*32)
    y_offsets = (0*32, 1*32, 2*32, 3*32, 4*32, 5*32, 6*32, 7*32, 0*32+512, 1*32+512, 2*32+512, 3*32+512, 4*32+512, 5*32+512, 6*32+512, 7*32+512)
    pixel_values = []
    for y in range(len(y_offsets)):
        row = []
        for x in range(len(x_offsets)):
            start_bit = y_offsets[y] + x_offsets[x]
            v = bits_to_int(bits[start_bit:start_bit + bits_pr_pixel])
            pixel_values.append(v << 4 ) # Use most significant 4 bits (scale to range 255-0)

            #row.append(bits[first_bit:last_bit])
            #print("First bit:", first_bit)
        #print(row)
    #print(pixel_values)
    """
    # Convert the bits to a list of pixel values
    pixels = []
    for pixel_start_bit in range(0, width*height*bits_pr_pixel,bits_pr_pixel):
        #print("Pixel start bit:", pixel_start_bit, pixel_start_bit+bits_pr_pixel)
        v = bits_to_int(bits[pixel_start_bit:pixel_start_bit+bits_pr_pixel])
        pixels.append(v << 4 ) # Use most significant 4 bits (scale to range 255-0)
        #for i in

    
    # The order of the pixel values needs to be swapped around.
    # A row consists of the values in this order: 1, 0, 3, 2, 5, 4, 7, 6
    order_index = [1, 0, 3, 2, 5, 4, 7, 6]
    """
    assert len(pixel_values) == width * height, "Length of pixel list must match no of pixels in graphic"   
    
    # return pixels
    return Image.frombytes("L", (width, height), np.array(pixel_values, dtype=np.uint8), "raw")

assert bits_to_int([1,1]) == 3
assert bits_to_int([1,0]) == 2
assert bits_to_int([1,0,0,0]) == 8
assert bits_to_int([1,1,1,1]) == 15
assert bits_to_int([1,0,0,0,1]) == 17


# Read interleaved ROMs
rom_bytes = interleave(rom_files,90000)



sheet_width = 32
sheet_height = 32
bytes_pr_tile = int(16*16/2)


sheet = Image.new("L", (sheet_width*16, sheet_height*16))

for y in range(sheet_height):
    for x in range(sheet_width):
        image = get_graphic(rom_bytes[:bytes_pr_tile])
        # The rest of the bytes
        rom_bytes = rom_bytes[bytes_pr_tile:]
        sheet.paste(image, (x * 16, y * 16))
        #print("x:", x_pos, "y:", y_pos)
sheet.show()
