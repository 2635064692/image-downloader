class ImageParseResult:
    def __init__(self, img_url=None, img_ref_url=None):
        self.img_url = img_url
        self.img_ref_url = img_ref_url

    @staticmethod
    def init():
        return ImageParseResult()

    def has_image_ref(self):
        return self.img_ref_url is not None

    def update(self, img_url, img_ref_url):
        self.img_url = img_url
        self.img_ref_url = img_ref_url

    def is_not_empty(self):
        return self.img_url is not None

    def has_img_ref(self):
        return self.img_ref_url is not None
