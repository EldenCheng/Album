import ftplib
from ftplib import FTP_TLS
import os
import random
import shutil
import tempfile
import time
from pathlib import Path

import cv2
import pyguetzli
import mozjpeg_lossless_optimization
from PIL import Image


class CompressImage:

    @staticmethod
    def compress(pic_path: str, target_path: str, chinese=False, method: str = 'g', size: float = 0.5, quality: int = 50):
        """
        使用Google的guetzli库来压缩图片, 注意这个库只支持jpeg并且比较慢
        :param pic_path: 相片的Path对象实例
        :param target_path: 相片的Path对象实例
        :param quality: 图片压缩质量
        :return:
        """
        try:
            print("Reducing pic {0} size...".format(pic_path))
            begin_time = time.time()
            # print("path: ", pic_path)
            if chinese:
                img = Image.open(pic_path)
                (width, height) = img.size
                resize_img = img.resize((int(width * size), int(height * size)))
                resize_img.save(target_path, quality=quality)
            else:
                pic = cv2.imread(pic_path)
                height, width = pic.shape[:2]  # 获取原始分辨率
                resize_pic = cv2.resize(pic, (int(width * size), int(height * size)))  # 缩小图片
                cv2.imwrite(target_path, resize_pic, [int(cv2.IMWRITE_JPEG_QUALITY), quality])  # 按照质量设置保存图片
            # print("Reduce pic by opencv, used: ".format(pic_path), int(time.time() - begin_time))
            if method:  # 设置是否需要额外压缩
                rb = open(str(target_path), 'rb').read()  # 压缩图片需要二进制数据
                if method == "g":  # 使用google pyguetzli压缩, 效果大概可以压缩到原图1/4, 已经缩小并降低质量的图都要1分钟左右

                    optimized_jpeg = pyguetzli.process_jpeg_bytes(rb, quality=quality)  # 将图片压缩后获得新的二进制数据

                elif method == "m":  # mozila的压缩方法压缩率低, 只能大约压缩5%的体积 但快, 基本不用额外时间

                    optimized_jpeg = mozjpeg_lossless_optimization.optimize(rb)

                    # rb.close() 二进制读取不能close
                wb = open(str(target_path), 'wb')
                wb.write(optimized_jpeg)
                # wb.close()
            print("pic {0} totally used: ".format(pic_path), int(time.time() - begin_time))
        except Exception as msg:
            print(msg)
            # raise Exception(msg)


class FtpOp:
    @staticmethod
    def connect(host: str = "localhost", ftps: bool = True, port: int = 21, username: str = '', password: str = ''):
        """
        使用给定的用户名与密码连接FTP
        :param host: 服务器名或者IP, 注意这里要填写不带FTP://的
        :param ftps: FTP服务器是否支持FTP Over TLS
        :param port: FTP端口
        :param username: FTP用户名
        :param password: FTP密码
        :return: FTP连接实例
        """
        try:
            if ftps:
                conn = FTP_TLS()
            else:
                conn = ftplib.FTP()
            conn.connect(host, port=port)
            conn.login(username, password)
            if conn.getwelcome():
                return conn
        except ftplib.error_perm as ftp_fail:
            raise Exception(ftp_fail)

    @staticmethod
    def FTP_upload(pic_path: Path, config: dict):
        """
        上传图片到FTP
        :param pic_path: 图片路径
        :param config: 由于多进程间配置变量不能共存, 所以需要额外传入
        :return: 无
        """
        # print(pic_path)
        try:
            if config['Compress']:  # 如果图形需要压缩
                # tf, tp = CompressImage.compress(pic_path)
                tf = open(str(pic_path), "rb")
            else:
                tf = open(str(pic_path), "rb")

            # 在多进程的环境下不能直接把FTP连接传入, 所以只能为每一个进程重新打开一个FTP连接
            upload_conn = FtpOp.connect(host=config['FTP'], ftps=config['FTPS'], port=21, username=config['User'],
                                        password=config['Password'])
            upload_conn.cwd(config['gallery'])
            print("Uploading pic {0}...".format(pic_path.name))
            upload_conn.encoding = 'utf8'  # 指明使用utf8以支持传输中文命名的文件或者文件夹
            upload_conn.storbinary('STOR ' + pic_path.name, tf, blocksize=1024)
            print("Pic {0} upload done".format(pic_path.name))
            upload_conn.quit()
            tf.close()
        except Exception as upload_fail:
            print(upload_fail)


class GithubOp:
    @staticmethod
    def img_process(pic_path: Path, config: dict):
        """
        将图片复制到git仓库下面的images文件夹
        :param pic_path: 图片路径
        :param config: 由于多进程间配置变量不能共存, 所以需要额外传入
        :return: 无
        """
        try:
            pic_name = pic_path.name
            if config['Compress'] is True:  # 如果图形需要压缩
                pic_path = CompressImage.compress(pic_path, quality=70)
                # pic_file.close()
                # pass
            img_path = Path("./images/{0}".format(pic_name))
            shutil.copy(str(pic_path), str(img_path))
            time.sleep(random.randint(1, 3))
        except Exception as msg:
            print(msg)
            # raise Exception(msg)

    @staticmethod
    def github_upload(gallery: str):
        """
        将已经stage的内容commit与push到github
        :param gallery: 要上传的相册名称
        :return: 无
        """
        cmd = ("git add index.md", "git add ./{0}/index.md".format(gallery),
               "git commit -m '{0}'".format(gallery))
        for c in cmd:
            print("Now executing command: {0}".format(c))
            os.system(c)
            time.sleep(1)
        time.sleep(10)
        print("Now executing command: git push origin master")
        os.system("git push origin master")
