from common.objManager import g_managere
from common.logger import g_spider_logger,g_main_logger
from crawler.spider_haowallpaper import SPhaowallpaer


LOGGER_SPIDER ="spider_logger"
LOGGER_MAIN ="main_logger"

SPIDER_HAOWALLPAER = "spider_haowallpaper"

def objRegs():
    g_managere.register(LOGGER_SPIDER, g_spider_logger)
    g_managere.register(LOGGER_MAIN, g_main_logger)

    spider_haowallpaper = SPhaowallpaer()
    g_managere.register(SPIDER_HAOWALLPAER, spider_haowallpaper)

def main():
    objRegs()
    spider_obj = g_managere.get(SPIDER_HAOWALLPAER)
    spider_obj.crawl()




if __name__ == '__main__':
    main()