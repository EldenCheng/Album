import json
from multiprocessing import Pool

from upload_utils import *

if __name__ == "__main__":
    total_time = time.time()
    with open("config.json", "r", encoding='utf-8') as f:
        config = json.loads(f.read())
        f.close()
    # print(config)

    allimgfiles = list(Path(config['pic_source']).rglob('*.*'))
    # print(allimgfiles)

    # 在本地建立gallery目录与index.md文件
    gallery_path = Path('./' + config['gallery'])
    if not gallery_path.is_dir():
        gallery_path.mkdir()
    gallery_index = Path("./index.md")
    gallery_index = gallery_path / gallery_index
    gallery_index.touch()

    # 写入gallery index.md文件的标题
    gallery_index_file = open(str(gallery_index), 'w', encoding='utf-8')
    gallery_content = "### [<-返回首页]({0}index.md) \n  \n## {1}  \n  \n".format(config['ServerURL'], config['title'])

    new_content = ''

    p = Pool(config['Pool size'])  # 打开进程池
    # 将图片的URL写入到gallery的index.md文件中
    for pic in allimgfiles:
        # 写入URL
        gallery_content = gallery_content + f"### {pic.name}  \n![{pic.name}]({config['PicURL']}{config['gallery']}/{pic.name})  \n  \n"
        if config['Compress']:
            p.apply_async(CompressImage.compress, (pic.absolute(), config['pic_target'] + "/" + pic.name, config['Compress Method'], config['Resize ratio'], config['Compress quality']), )  # 多进程入
            # CompressImage.compress(pic.absolute(), config['pic_target'] + "/" + pic.name, config['Compress Method'], config['Resize ratio'], config['Compress quality'])

    p.close()
    p.join()

    # if config['Upload_Place'].lower() == "ftp":
        # conn = FtpOp.connect(host=config['FTP'], port=21, username=config['User'], password=config['Password'])
        # current_folder = conn.pwd()

        # # 测试是否成功连接FTP与当前目录是否是相册根目录
        # if current_folder == "/":
        #     # 在FTP上建立对应目录并进入, 如果建立不成功,尝试直接进入
        #     # 如果能进入不报错, 代表FTP上已经存在该目录
        #     try:
        #         conn.mkd(config['gallery'])
        #     except ftplib.error_perm as ftp_error:
        #         print(ftp_error)
        #     conn.cwd(config['gallery'])
        #     conn.quit()



        # p = Pool(3)  # 打开进程池

        # 将图片的URL写入到gallery的index.md文件中
        # 再使用多进程上传图片到FTP上
        # for pic in allimgfiles:
        #     # 写入URL
        #     gallery_content = gallery_content + "### {0}  \n![{0}]({1}{2}/{0})  \n  \n".format \
        #         (pic.name, config['PicURL'], config['gallery'])
            # FTP_upload(pic, config)

            # if config['Compress']:
            #     p.apply_async(GithubOp.img_process, (pic, config), )  # 多进程入口
        #     p.apply_async(CompressImage.compress, (pic, desc_file, 'm', size / 100, quality), )  # 多进程入
        #
        # p.close()
        # p.join()

        # new_content = "### [{0}]({1}{2}/index.md) <- 点击文字打开  \n".format(config['title'], config['ServerURL'], config['gallery']) \
        #               + "  \n" + "![{0}]({1}{2}/{0})".format(allimgfiles[-1].name, config['PicURL'],
        #                                                      config['gallery']) + "  \n  \n"

    # elif config['Upload_Place'].lower() == "gitee":
    #     p = Pool(8)  # 打开进程池

    #     # 拼接好相片的URL
    #     # 再将对应的相片复制到git仓库里的images文件下
    #     for pic in allimgfiles:
    #         # 写入URL
    #         gallery_content = gallery_content + \
    #                           "### {0}  \n![{0}]({1}/{0})  \n  \n".format(pic.name, config['URL3'])
    #         # GithubOp.img_process(pic, config)
    #         p.apply_async(GithubOp.img_process, (pic, config), )  # 多进程入口
    #     p.close()
    #     p.join()

    #     for pic in allimgfiles:  # 由于有可能需要多进程去压缩图片, 而git对多进程支持不好,所以处理好图片之后再stage它们
    #         cmd = "git add ./images/{0}".format(pic.name)
    #         print("Now executing command: {0}".format(cmd))
    #         os.system(cmd)

    #     new_content = "### [{0}]({1}{2}/) <- 点击文字打开  \n".format(config['title'], config['URL1'], config['gallery']) \
    #                   + "  \n" + "![{0}]({1}/{0})".format(allimgfiles[-1].name, config['URL3']) + "  \n  \n"

    # 将相册的相片连接写入相册的index.md
    new_content = f"### [{config['title']}]({config['ServerURL']}{config['gallery']}/index.md) <- 点击文字打开  \n" + "  \n" + f"![{allimgfiles[-1].name}]({config['PicURL']}{config['gallery']}/{allimgfiles[-1].name})" + "  \n  \n"
    gallery_index_file.write(gallery_content)
    gallery_index_file.close()

    # 将新相册的URL写入首页的index.md
    photobook_index = './index.md'
    photobook_index_file = open(str(photobook_index), 'r+', encoding='utf-8')
    old_content = photobook_index_file.read()
    photobook_index_file.seek(0, 0)  # 读取之后指针会指向文件的最后, 需要复位到文件的最开始位置

    # 将新相册的内容放到相册中的第一位
    content = old_content[:9] + "  \n" + new_content + old_content[9:]
    photobook_index_file.write(content)
    photobook_index_file.close()

    # GithubOp.github_upload(config['gallery'])  # 最后将编辑完成的文件commit与push到github上
    print("Totally used: ", int(time.time() - total_time))
