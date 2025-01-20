import json
import time
from urllib.parse import parse_qs, urlparse, unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from downloader.WebDriverManager import WebDriverManager
from downloader import ImageParseResult


class BingEngine:
    BASE_URL = "https://bing.com/images/search?qft=+filterui:photo-photo&q="

    def build_search_url(self, keyword):
        """
        构建 Google 图片搜索的 URL。
        :param keyword: 搜索关键字
        :return: 完整搜索 URL
        """
        if not keyword:
            raise ValueError("Keyword cannot be empty for building search URL.")
        return f"{self.BASE_URL}{keyword}"

    def parse_image(self, manager:WebDriverManager):
        """
        使用 Selenium WebDriver 解析 Google 图片搜索结果。
        :param manager: WebDriverManager 对象
        :return: 包含 ImageParseResult 的列表
        """
        max_images = manager.get_limit()
        driver = manager.driver

        image_results = []
        seen_urls = set()
        scroll_pause_time = 1  # 滚动的间隔时间 (秒)
        last_height = driver.execute_script("return document.body.scrollHeight")

        img_box_index = 0  # 初始化解析的起始索引

        while len(image_results) < max_images:
            # 找到所有图片容器
            a_elements = driver.find_elements(By.CSS_SELECTOR, "a[aria-label]")

            # 检查是否还有未解析的图片容器
            if img_box_index >= len(a_elements):
                # 如果没有未解析的图片容器，滚动页面加载更多
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # 如果页面高度没有变化，可能已经加载完所有图片
                    break
                last_height = new_height
                continue  # 重新获取 img_div_boxs

            # 从上次解析的索引开始，处理图片容器
            current_batch = a_elements[img_box_index:img_box_index + (max_images - len(image_results))]

            # 更新 img_box_index
            img_box_index += len(current_batch)

            # 提取当前 batch 的图片 URL
            batch_results = self.fetch_image_urls_batch(current_batch, driver)
            for result in batch_results:
                if result.img_url not in seen_urls:
                    seen_urls.add(result.img_url)
                    image_results.append(result)

        return list(image_results)[:max_images]

    def fetch_image_urls_batch(self, img_div_boxes, driver):
        """
        批量处理图片容器并提取 URL。
        :param img_div_boxes: 图片容器 WebElement 列表
        :param driver: Selenium WebDriver 对象
        :return: ImageParseResult 列表
        """
        results = []
        for img_box in img_div_boxes:
            parse_result = self.fetch_image_urls(img_box, driver)
            if parse_result.is_not_empty():
                results.append(parse_result)
        return results

    def fetch_image_urls(self, img_box, driver):
        """
        从单个图片容器中提取图片 URL 和参考 URL。
        :param img_box: 图片容器 WebElement
        :param driver: Selenium WebDriver 对象
        :return: ImageParseResult 对象
        """
        result = ImageParseResult.init()

        try:
            m_json = img_box.get_attribute("m")
            if m_json:
                m_data = json.loads(m_json)
                img_url = m_data.get("murl")
                img_ref_url = m_data.get("purl")
                result.update(img_url, img_ref_url)
        except Exception as e:
            print(f"Error fetching image URLs: {e}")
        return result

    @staticmethod
    def find_sub_a_tag(img_box):
        """
        查找图片容器中的 <a> 子标签。
        :param img_box: 图片容器 WebElement
        :return: <a> 标签 WebElement
        """
        return img_box.find_element(By.XPATH, "./a")

    @staticmethod
    def parse_query_params(href):
        """
        解析 URL 查询参数。
        :param href: URL 字符串
        :return: 查询参数的字典
        """
        query = urlparse(href).query
        return {key: value[0] for key, value in parse_qs(query).items()}