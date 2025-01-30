class ObjectManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObjectManager, cls).__new__(cls)
            cls._instance.objects = {}
        return cls._instance

    def register(self, name, obj):
        """注册一个对象"""
        self.objects[name] = obj

    def get(self, name):
        """获取一个对象"""
        return self.objects.get(name)

    def remove(self, name):
        """移除一个对象"""
        if name in self.objects:
            del self.objects[name]

    def clear(self):
        """清除所有对象"""
        self.objects.clear()

    def list_objects(self):
        """列出所有已注册的对象"""
        return list(self.objects.keys())


if __name__ == "__main__":
    # 创建一些模拟的模块对象
    class Logger:
        def log(self, message):
            print(f"Logging: {message}")

    class Crawler:
        def crawl(self, url):
            print(f"Crawling: {url}")

    # 使用 ObjectManager
    manager = ObjectManager()

    # 注册对象
    logger = Logger()
    crawler = Crawler()

    manager.register("logger", logger)
    manager.register("crawler", crawler)

    # 获取并使用对象
    log_obj = manager.get("logger")
    log_obj.log("This is a test message")

    crawl_obj = manager.get("crawler")
    crawl_obj.crawl("http://example.com")

    # 列出所有注册的对象
    print(manager.list_objects())  # 输出: ['logger', 'crawler']

    # 移除一个对象
    manager.remove("logger")
    print(manager.list_objects())  # 输出: ['crawler']

    # 清除所有对象
    manager.clear()
    print(manager.list_objects())  # 输出: []
