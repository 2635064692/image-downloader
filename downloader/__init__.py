#!/usr/bin/env python
from __future__ import absolute_import


# 从内部模块导入需要对外公开的内容
from .common.ImageParseResult import ImageParseResult
from .common.ImageResponse import ImageResponse

def main():
    import downloader.ImageDownloader

if __name__ == '__main__':
    main()