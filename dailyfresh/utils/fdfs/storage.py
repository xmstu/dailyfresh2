from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client


class FdfsStorage(FileSystemStorage):
    """自定义文件储存:通过管理后台上传文件时,把文件上传到fdfs"""

    def _save(self, name, content):
        """
        通过管理后台上传文件时,会执行此方法保存上传的文件
        :param name: name上传文件的名称
        :param content: 上传文件内容,从此对象中可以取出上传文件内容
        :return:
        """
        # 保存文件到fdfs服务器
        client = Fdfs_client('/home/python/PycharmProjects/dailyfresh/utils/fdfs/client.conf')
        try:
            body = content.read()
            my_dict = client.upload_by_buffer(body)
        except Exception as e:
            print(e)
            raise e

        if my_dict.get('Status') == 'Upload successed.':
            path = my_dict.get('Remote file_id')
        else:
            raise Exception('FastDFS上传文件失败,status不正确')

        # path = super().save(name, content)
        print('name=%s, content=%s, path= %s' % (name, type(content), path))

        # 返回文件id, django会自动保存此路径到数据库中
        return path

    def url(self, name):
        # nginx服务器的主机端口
        host = 'http://127.0.0.1:8888/'
        url = host + super().url(name)
        return url