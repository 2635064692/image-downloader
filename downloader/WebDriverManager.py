import os

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService

from Config import Config
from ImageResponse import ImageResponse
from downloader import ImageParseResult


class WebDriverManager:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    CONNECT_TIMEOUT = 5

    def __init__(self, config: Config):
        """
        初始化 WebDriverManager
        """
        self.config = config
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        """
        初始化 Chrome WebDriver，并配置启动参数。
        """
        options = Options()
        # 开启调试模式，显示弹出浏览器
        # options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--headless")  # 无头模式
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")
        options.add_argument(f"--user-agent={self.USER_AGENT}")
        options.add_argument("--disable-extensions")
        options.add_argument("--incognito")
        if self.config.proxy:
            options.add_argument(f"--proxy-server={self.config.proxy}")

        if self.config.browser_driver_path:
            # 设置 Chrome 驱动路径
            driver = webdriver.Chrome(service=ChromeService(self.config.browser_driver_path), options=options)
        else:
            driver = webdriver.Chrome(options=options)

        # if self.config.page_load_timeout:
        #     driver.set_page_load_timeout(self.config.page_load_timeout)
        return driver

    def get(self, engines):
        """
        加载搜索引擎的搜索 URL。
        """
        try:
            url = engines.build_search_url(self.config.keyword)
            self.driver.get(url)
        except Exception as e:
            print(f"Error navigating to URL: {e}")

    def quit(self):
        """
        关闭 WebDriver。
        """
        self.driver.quit()

    def download_image(self, parse_result: ImageParseResult, index):
        """
        下载图片并保存到本地。
        """
        download_url = parse_result.img_url
        try:
            image_response = self.image_net_request(download_url)
            image_response.update_index(index, 0)
            self.save(image_response)
        except Exception as e:
            print(f"Failed to download image {index} from URL: {download_url}, error: {e}")
            return

        if parse_result.has_img_ref():
            self.parse_ref_page_image(parse_result.img_ref_url, image_response.width, image_response.height, index)

    def save(self, image_response: ImageResponse):
        """
        保存图片到指定目录，并根据文件扩展名命名。
        """
        if image_response.is_empty():
            return
        output_dir = self.config.output_directory
        os.makedirs(output_dir, exist_ok=True)

        save_dir = os.path.join(output_dir , self.config.sub_folder)
        os.makedirs(save_dir, exist_ok=True)

        url = image_response.url
        combine_indexes = image_response.split()
        # 获取文件扩展名
        ext = os.path.splitext(url)[1].split('?')[0]
        if ext not in [".jpg", ".jpeg", ".png", ".bmp"]:
            ext = ".jpg"  # 默认使用 JPG

        if combine_indexes[1] == 0:
            filename = f"image_{combine_indexes[0]:04d}{ext}"
        else:
            filename = f"image_{combine_indexes[0]:04d}_{combine_indexes[1]:02d}{ext}"
        # 保存文件

        filepath = os.path.join(str(save_dir), filename)
        image = image_response.image
        image.save(filepath, format=image.format)  # 将图片保存为文件，自动匹配格式

    def get_full_host_from_url(self, url):
        # 查找协议的结束位置
        if "://" in url:
            protocol_end_index = url.index("://") + 3  # 协议部分结束位置
        else:
            protocol_end_index = 0  # 如果没有协议，指向开头

        # 查找路径的开始位置
        host_end_index = url.find('/', protocol_end_index)  # 从协议结束后开始查找

        if host_end_index == -1:  # 如果没有找到路径，主机到结尾
            host_end_index = len(url)

        # 提取并返回完整的主机部分
        return url[:host_end_index]  # 返回包含协议和主机部分

    def parse_ref_page_image(self, img_ref_url, base_width, base_height, index, proxy=None):
        """
        解析图片引用页面，下载符合条件的图片。
        """
        tmp_img_urls = set()
        # 设置代理
        proxies = {"http": proxy, "https": proxy} if proxy else None

        try:
            response = requests.get(img_ref_url, headers={"User-Agent": self.USER_AGENT}, proxies=proxies,
                                    timeout=self.CONNECT_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 提取图片标签
            images = soup.find_all("img")
            for i, img in enumerate(images):
                img_url = img.get("src")
                if img_url and img_url not in tmp_img_urls:
                    if img_url.startswith("/"):
                        img_url = self.get_full_host_from_url(img_ref_url) + img_url

                    tmp_img_urls.add(img_url)
        except Exception as e:
            # 捕获连接错误，如果有代理可尝试切换
            if proxy is None and self.config.has_proxy():
                print(f"parse_ref_page_image Retrying with new proxy...")
                return self.parse_ref_page_image(img_ref_url, base_width, base_height, index, proxy=self.config.proxy)
            print(f"Error parsing reference page: {e}")
        i = 1
        for tmp_url in tmp_img_urls:
            # 获取文件扩展名
            ext = os.path.splitext(tmp_url)[1].split('?')[0]
            if ext in [".svg"]:
                return  # SVG 不支持
            response = self.image_net_request(tmp_url)
            if response.is_save(base_width, base_height):
                response.update_index(index, i)
                self.save(response)
            i += 1

    def image_net_request(self, image_url, proxy=None) -> ImageResponse:
        # 设置代理
        proxies = {"http": proxy, "https": proxy} if proxy else None

        # 发起 HTTP 请求
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(image_url, headers=headers, proxies=proxies, timeout=self.CONNECT_TIMEOUT)

        # 检查响应状态码
        if response.status_code == 200:
            # 尝试解析图片
            try:
                image = Image.open(BytesIO(response.content))
                width, height = image.size
                return ImageResponse(image_url, image, height, width)
            except Exception as e:
                print(f"Failed to read image from URL: {image_url}, Error: {e}")
                return ImageResponse.empty()
        else:
            # 捕获连接错误，如果有代理可尝试切换            if proxy is None and self.config.has_proxy():
            if proxy is None and self.config.has_proxy():
                print(f"image_net_request Retrying with new proxy...")
                new_proxy = self.config.proxy  # 假设有一个函数获取新的代理
                return self.image_net_request(image_url, proxy=new_proxy)
            print(f"Failed to connect. HTTP Response Code: {response.status_code}")
            return ImageResponse.empty()

    def get_limit(self):
        return self.config.limit
