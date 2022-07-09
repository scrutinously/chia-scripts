# Copyright (c) 2017 Pieter Wuille
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Based on this specification from Pieter Wuille:
# https://github.com/sipa/bips/blob/bip-bech32m/bip-bech32m.mediawiki

"""Reference implementation for Bech32m and segwit addresses."""
import sys
import argparse
from typing import List, Iterable, Optional, Tuple, SupportsBytes, Type, TypeVar, Union, BinaryIO

from typing_extensions import SupportsIndex

_T_SizedBytes = TypeVar("_T_SizedBytes", bound="SizedBytes")

def hexstr_to_bytes(input_str: str) -> bytes:
    """
    Converts a hex string into bytes, removing the 0x if it's present.
    """
    if input_str.startswith("0x") or input_str.startswith("0X"):
        return bytes.fromhex(input_str[2:])
    return bytes.fromhex(input_str)


class SizedBytes(bytes):
    """A streamable type that subclasses "bytes" but requires instances
    to be a certain, fixed size specified by the `._size` class attribute.
    """

    _size = 0

    # This is just a partial exposure of the underlying int constructor.  Liskov...
    # https://github.com/python/typeshed/blob/f8547a3f3131de90aa47005358eb3394e79cfa13/stdlib/builtins.pyi#L483-L493
    def __init__(self, v: Union[Iterable[SupportsIndex], SupportsBytes]) -> None:
        # v is unused here and that is ok since .__new__() seems to have already
        # processed the parameter when creating the instance of the class.  We have no
        # additional special action to take here beyond verifying that the newly
        # created instance satisfies the length limitation of the particular subclass.
        super().__init__()
        if len(self) != self._size:
            raise ValueError("bad %s initializer %s" % (type(self).__name__, v))

    @classmethod
    def parse(cls: Type[_T_SizedBytes], f: BinaryIO) -> _T_SizedBytes:
        b = f.read(cls._size)
        return cls(b)

    def stream(self, f: BinaryIO) -> None:
        f.write(self)

    @classmethod
    def from_bytes(cls: Type[_T_SizedBytes], blob: bytes) -> _T_SizedBytes:
        return cls(blob)

    @classmethod
    def from_hexstr(cls: Type[_T_SizedBytes], input_str: str) -> _T_SizedBytes:
        if input_str.startswith("0x") or input_str.startswith("0X"):
            return cls.fromhex(input_str[2:])
        return cls.fromhex(input_str)

    def __str__(self) -> str:
        return self.hex()

    def __repr__(self) -> str:
        return "<%s: %s>" % (self.__class__.__name__, str(self))

class bytes32(SizedBytes):
    _size = 32

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32_polymod(values: List[int]) -> int:
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_hrp_expand(hrp: str) -> List[int]:
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


M = 0x2BC830A3


def bech32_verify_checksum(hrp: str, data: List[int]) -> bool:
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == M


def bech32_create_checksum(hrp: str, data: List[int]) -> List[int]:
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ M
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def bech32_encode(hrp: str, data: List[int]) -> str:
    """Compute a Bech32 string given HRP and data values."""
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + "1" + "".join([CHARSET[d] for d in combined])


def bech32_decode(bech: str, max_length: int = 90) -> Tuple[Optional[str], Optional[List[int]]]:
    """Validate a Bech32 string, and determine HRP and data."""
    if (any(ord(x) < 33 or ord(x) > 126 for x in bech)) or (bech.lower() != bech and bech.upper() != bech):
        return (None, None)
    bech = bech.lower()
    pos = bech.rfind("1")
    if pos < 1 or pos + 7 > len(bech) or len(bech) > max_length:
        return (None, None)
    if not all(x in CHARSET for x in bech[pos + 1 :]):
        return (None, None)
    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos + 1 :]]
    if not bech32_verify_checksum(hrp, data):
        return (None, None)
    return hrp, data[:-6]


def convertbits(data: Iterable[int], frombits: int, tobits: int, pad: bool = True) -> List[int]:
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            raise ValueError("Invalid Value")
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        raise ValueError("Invalid bits")
    return ret


def encode_puzzle_hash(puzzle_hash: bytes32, prefix: str) -> str:
    encoded = bech32_encode(prefix, convertbits(puzzle_hash, 8, 5))
    return encoded


def decode_puzzle_hash(address: str) -> bytes32:
    hrpgot, data = bech32_decode(address)
    if data is None:
        raise ValueError("Invalid Address")
    decoded = convertbits(data, 5, 8, False)
    decoded_bytes = bytes32(decoded)
    return decoded_bytes

def main():
    # argparse options
    parser = argparse.ArgumentParser(description="Puzhash: Bech32m puzzlehash to address converter", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""EXAMPLE USAGE:
puzhash.py -i <input hex string> -p <prefix>
puzhash.py -a <address>""")
    parser.add_argument("-i", "--input", type=str, help="Input hex string of hash")
    parser.add_argument("-p", "--prefix", type=str, help="Prefix for address", default="xch")
    parser.add_argument("-a", "--address", type=str, help="Address to decode")
    args = parser.parse_args()

    # Determines if we are encoding or decoding
    if args.input and args.prefix:
        print(encode_puzzle_hash(bytes32.from_hexstr(args.input), args.prefix))
    elif args.address:
        print(decode_puzzle_hash(args.address))

if __name__ == "__main__":
    main()