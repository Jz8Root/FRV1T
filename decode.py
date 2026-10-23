#!/usr/bin/env python3
"""Decode a FRV2 fruit to plain UTF-8 text. Never execute its contents."""
import argparse
from pathlib import Path
import sys
import zlib

LIMIT = 256 * 1024

def decode(text):
    text = text.removesuffix('\n')
    if len(text) < 3 or text[1] != '\ufe0f' or any(c in text for c in '\r\n\ufffd'):
        raise ValueError('Expected one fruit emoji, U+FE0F, then intact variation selectors.')
    values = []
    for character in text[2:]:
        n = ord(character)
        if 0xfe00 <= n <= 0xfe0f:
            values.append(n - 0xfe00)
        elif 0xe0100 <= n <= 0xe01ef:
            values.append(n - 0xe0100 + 16)
        else:
            raise ValueError('Unexpected character; use the readable prompt if copying stripped Unicode.')
    data = bytes(values)
    if not data.startswith(b'FRV2'):
        raise ValueError('Not a current FRV2 fruit. Use its matching readable prompt.')
    stream = zlib.decompressobj(31)
    raw = stream.decompress(data[4:], LIMIT + 1)
    if len(raw) > LIMIT or not stream.eof or stream.unused_data or stream.unconsumed_tail:
        raise ValueError('Invalid, truncated, oversized or trailing compressed data.')
    return raw.decode('utf-8', errors='strict')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fruit', type=Path)
    args = parser.parse_args()
    try:
        content = decode(args.fruit.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError, zlib.error) as error:
        parser.exit(1, f'Decode failed: {error}\n')
    sys.stdout.write(content)
