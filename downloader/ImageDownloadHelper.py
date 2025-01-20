from concurrent.futures import ThreadPoolExecutor
from typing import List

from downloader.WebDriverManager import WebDriverManager
from downloader.engine.BaiduEngine import BaiduEngine
from downloader.engine.BingEngine import BingEngine
from downloader.engine.GoogleEngine import GoogleEngine

class ImageDownloadHelper:
    """图片下载助手类，提供并发下载和主下载流程控制功能"""
    @staticmethod
    def download_images_concurrently(results: List, manager):
        """并发下载图片
        
        Args:
            results (List): 图片结果列表
            manager: WebDriverManager 实例，用于实际下载操作
        """
        if not results:
            return

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(manager.download_image, result, idx + 1) for idx, result in enumerate(results)]

            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in concurrent download: {e}")

    @staticmethod
    def download(config):
        """主下载方法，处理整个下载流程
        
        Args:
            config: 配置对象，包含下载参数
        """

        engines = ImageDownloadHelper.choose_engines(config.search_engines)
        real_configs = config.parse_config()

        for config in real_configs:
            manager = WebDriverManager(config)
            driver = manager.get(engines)
            results = engines.parse_image(manager)
            ImageDownloadHelper.download_images_concurrently(results, manager)
            manager.quit()
            print("loop end")

    @staticmethod
    def choose_engines(search_engines):
        """根据配置选择合适的搜索引擎实例

        Returns:
            SearchEngines: 返回对应的搜索引擎实例
        """
        if search_engines == 'baidu':
            return BaiduEngine()
        elif search_engines == 'bing':
            return BingEngine()
        elif search_engines == 'google':
            return GoogleEngine()
        else:
            raise ValueError(f"Unsupported engine type: {search_engines}")