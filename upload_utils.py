import ftplib
import os
import random
import shutil
import tempfile
import time
from pathlib import Path

# import pyguetzli


# class CompressImage:
#
#     @staticmethod
#     def compress(pic_path: Path, quality: int = 85):
#         """
#         使用Google的guetzli库来压缩图片, 注意这个库只支持jpeg并且比较慢
#         :param pic_path: 相片的Path对象实例
#         :param quality: 图片压缩质量
#         :return: 压缩后的相片的二进制文件内容与相片的路径
#         """
#         try:
#             fb = open(str(pic_path), 'rb').read()  # 压缩图片需要二进制数据
#             if pic_path.suffix.lower() == ".jpg":  # 只支持jpeg
#                 print("Reducing pic {0} size...".format(pic_path.name))
#                 optimized_jpeg = pyguetzli.process_jpeg_bytes(fb, quality=quality)  # 将图片压缩后获得新的二进制数据
#             else:
#                 optimized_jpeg = fb
#             temp = tempfile.mktemp()  # 为了不影响原相片, 压缩后的相片会先放在临时文件
#             tf = open(temp, "wb+")
#             tf.write(optimized_jpeg)  # 将压缩后的二进制数据写入临时文件
#             tf.close()
#             tf = open(temp, "rb")  # 由于缓存机制的原因, 先保存再读取才能读取到更新后的内容
#             return tf, temp  # 由于FTP需要文件内容本身, 而上传github只需要文件的路径, 所以这里返回两部分内容
#         except Exception as msg:
#             print(msg)
#             # raise Exception(msg)


class FtpOp:
    @staticmethod
    def connect(host: str = "localhost", port: int = 21, username: str = None, password: str = None):
        """
        使用给定的用户名与密码连接FTP
        :param host: 服务器名或者IP, 注意这里要填写不带FTP://的
        :param port: FTP端口
        :param username: FTP用户名
        :param password: FTP密码
        :return: FTP连接实例
        """
        try:
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
            if config['Compress'] is True:  # 如果图形需要压缩
                tf, tp = CompressImage.compress(pic_path)
            else:
                tf = open(str(pic_path), "rb")

            # 在多进程的环境下不能直接把FTP连接传入, 所以只能为每一个进程重新打开一个FTP连接
            upload_conn = FtpOp.connect(host=config['FTP'], port=21, username=config['User'],
                                        password=config['Password'])
            upload_conn.cwd(config['gallery'])
            print("Uploading pic {0}...".format(pic_path.name))
            upload_conn.encoding = 'utf8'
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
                pic_file, pic_path = CompressImage.compress(pic_path, quality=70)
                pic_file.close()
            img_path = Path("./images/{0}".format(pic_name))
            shutil.copy(str(pic_path), str(img_path))
            time.sleep(random.randint(1, 3))
        except Exception as msg:
            print(msg)
            # raise Exception(msg)

    @staticmethod
    def github_upload(gallery: str):
        """
        将已经stage人内容commit与push到github
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
