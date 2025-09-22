# UPP
Ultimate Packer for Python

Tool for packing .pyc files!

Before using read disclaimer [In English](/DISCLAIMER_EN.md) or [На Русском](/DISCLAIMER_RU.md).

Using for packing malware is prohibited and useless because its intended to give you max packed size with correct packing, so not intended to "crypt" your malware and can be easily unpacked.

args:
```
UPP.py:
  filename

  -bz2, --bz2           Use bz2
  -gzip, --gzip         Use gzip
  -lzma, --lzma         Use lzma
  -zlib, --zlib         Use zlib (default)
  -cl COMPRESSION_LEVEL, --compression-level COMPRESSION_LEVEL
                        Choose compression level
  -b, --brute           Making benchmarks so chooses the
                        best compression method
  -be, --brute-extreme  Making benchmarks more extreme so
                        testes even compression levels
                        (requires -b)
  -e EXCLUDE, --exclude EXCLUDE
                        Exclude compression methods
  -d, --decompress      Decompress packed file

```
