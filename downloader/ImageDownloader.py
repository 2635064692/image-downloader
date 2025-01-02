import argparse

from downloader.Config import Config
from downloader.ImageDownloadHelper import ImageDownloadHelper

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Downloader")
    parser.add_argument("-dp", "--driver_path", help="Browser driver path",required=False)
    parser.add_argument("-k", "--keyword", help="Image keyword",required=True)
    parser.add_argument("-px", "--proxy", help="Request proxy",required=False)
    parser.add_argument("-plt", "--page_load_timeout", type=int, help="Page load timeout",required=False)
    parser.add_argument("-l", "--limit", type=int, help="delimited list input", default=10,required=False)
    parser.add_argument("-o", "--output_directory", help="Output directory",required=False)
    parser.add_argument('-kf', '--keywords_from_file', help='extract list of keywords from a text file', type=str, required=False)

    args = parser.parse_args()
    config = Config(
        proxy=args.proxy,
        keyword=args.keyword,
        page_load_timeout=args.page_load_timeout,
        browser_driver_path=args.driver_path,
        limit=args.limit,
        output_directory=args.output_directory,
        keywords_from_file=args.keywords_from_file
    )

    print("Starting image download...")
    ImageDownloadHelper.download(config)