from django.core.files.storage import FileSystemStorage


class FdfsStorage(FileSystemStorage):
    """自定义文件储存:通过管理后台上传文件时,把文件上传到fdfs"""

    def _save(self, name, content):
        """
        通过管理后台上传文件时,会执行此方法保存上传的文件
        :param name: name上传文件的名称
        :param content: 上传文件内容,从此对象中可以取出上传文件内容
        :return:
        """
        path = super().save(name, content)
        print('name=%s, content=%s, path= %s' % (name, type(content), path))

        # 返回文件id, django会自动保存此路径到数据库中
        return path
