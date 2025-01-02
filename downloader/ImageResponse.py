class ImageResponse:
    def __init__(self, url=None, image=None, height=-1, width=-1):
        self.url = url
        self.image = image  # 类似于 Java 中的 BufferedImage
        self.height = height
        self.width = width
        self.index = 0  # 初始化 index 为 0

    @staticmethod
    def empty():
        """返回一个空的 ImageResponse 对象"""
        return ImageResponse()

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def get_url(self):
        return self.url

    def set_url(self, url):
        self.url = url

    def get_image(self):
        return self.image

    def set_image(self, image):
        self.image = image

    def get_height(self):
        return self.height

    def set_height(self, height):
        self.height = height

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width

    def is_save(self, base_width, base_height):
        """
        检查图片是否符合保存条件，即宽高是否达到指定值。
        :param base_width: 基准宽度
        :param base_height: 基准高度
        :return: 是否符合保存条件
        """
        if self.is_empty():
            return False
        return self.width >= base_width and self.height >= base_height

    def is_empty(self):
        """
        检查是否是一个空的 ImageResponse 对象
        :return: 是否为空
        """
        return self.image is None

    def combine(self, high, low):
        """
        将高位和低位合并成一个整数。
        :param high: 高位值
        :param low: 低位值
        :return: 合并后的整数
        """
        # 确定低位的位数（14 位足够表示 10000 以内的数字）
        low_bit_size = 14

        # 检查低位是否在范围内
        if low >= (1 << low_bit_size):  # 2^14 = 16384
            raise ValueError(f"Low part must be less than {1 << low_bit_size}")

        # 将高位左移 14 位，并与低位合并
        return (high << low_bit_size) | low

    def split(self):
        """
        将 `index` 拆分为高位和低位。
        :return: 高位和低位的列表 [high, low]
        """
        # 确定低位的位数（14 位）
        low_bit_size = 14

        # 提取低位
        low = self.index & ((1 << low_bit_size) - 1)  # 获取低 14 位
        # 提取高位
        high = self.index >> low_bit_size  # 无符号右移 14 位

        return [high, low]

    def update_index(self, index, i):
        """
        更新 `index`，将高位和低位合并。
        :param index: 高位
        :param i: 低位
        """
        self.index = self.combine(index, i)
