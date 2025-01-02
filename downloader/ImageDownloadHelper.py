from concurrent.futures import ThreadPoolExecutor
from typing import List

from WebDriverManager import WebDriverManager
from engine.GoogleEngine import GoogleEngine

class ImageDownloadHelper:
    @staticmethod
    def download_images_concurrently(results: List, manager):
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
        engines = GoogleEngine()
        real_configs = config.parse_config()

        for config in real_configs:
            manager = WebDriverManager(config)
            driver = manager.get(engines)
            results = engines.parse_image(manager)
            ImageDownloadHelper.download_images_concurrently(results, manager)
            manager.quit()
            print("loop end")