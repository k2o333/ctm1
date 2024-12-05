import os
import zipfile
import rarfile
import tarfile
import py7zr
import json
import sys

def is_text_file(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(4)
        if header.startswith(b'\x89\x50\x4e\x47') or header.startswith(b'\xff\xd8\xff\xe0'):
            return False
        else:
            try:
                f.read().decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False

def convert_file_to_markdown(file_path, file_name, level):
    if is_text_file(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            if file_name.endswith('.json'):
                content = json.dumps(json.loads(content), indent=4)
            return '  ' * level + '# ' + file_name + '\n' + '  ' * level + '\n' + '```\n' + content + '\n' + '  ' * level + '```\n'
    else:
        return '  ' * level + '# ' + file_name + '\n'

def convert_dir_to_markdown(dir_path, dir_name, level):
    markdown_content = '  ' * level + '# ' + dir_name + '\n'
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            markdown_content += convert_file_to_markdown(file_path, file_name, level + 1)
        elif os.path.isdir(file_path):
            markdown_content += convert_dir_to_markdown(file_path, file_name, level + 1)
    return markdown_content

def extract_archive(archive_path):
    output_dir = os.path.dirname(os.path.abspath(archive_path))
    markdown_content = ''

    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_file:
            for file_name in zip_file.namelist():
                file_path = zip_file.extract(file_name)
                if os.path.isfile(file_path):
                    markdown_content += convert_file_to_markdown(file_path, file_name, 1)
                elif os.path.isdir(file_path):
                    markdown_content += convert_dir_to_markdown(file_path, file_name, 1)

    elif archive_path.endswith('.rar'):
        with rarfile.RarFile(archive_path, 'r') as rar_file:
            for file_name in rar_file.namelist():
                file_path = rar_file.extract(file_name)
                if os.path.isfile(file_path):
                    markdown_content += convert_file_to_markdown(file_path, file_name, 1)
                elif os.path.isdir(file_path):
                    markdown_content += convert_dir_to_markdown(file_path, file_name, 1)

    elif archive_path.endswith(('.tar', '.tar.gz', '.tar.bz2')):
        with tarfile.open(archive_path, 'r:*') as tar_file:
            tar_file.extractall(output_dir)
            for file_name in tar_file.getnames():
                file_path = os.path.join(output_dir, file_name)
                if os.path.isfile(file_path):
                    markdown_content += convert_file_to_markdown(file_path, file_name, 1)
                elif os.path.isdir(file_path):
                    markdown_content += convert_dir_to_markdown(file_path, file_name, 1)

    elif archive_path.endswith('.7z'):
        with py7zr.SevenZipFile(archive_path, 'r') as sz_file:
            sz_file.extractall(output_dir)
            for file_name in sz_file.getnames():
                file_path = os.path.join(output_dir, file_name)
                if os.path.isfile(file_path):
                    markdown_content += convert_file_to_markdown(file_path, file_name, 1)
                elif os.path.isdir(file_path):
                    markdown_content += convert_dir_to_markdown(file_path, file_name, 1)

    else:
        raise ValueError('不支持的压缩文件格式')

    return markdown_content

def main():
    archive_path = input('请输入压缩文件的路径：')
    output_dir = os.path.dirname(os.path.abspath(archive_path))
    output_file = os.path.join(output_dir, 'output.md')
    
    try:
        markdown_content = extract_archive(archive_path)
        with open(output_file, 'w') as f:
            f.write(markdown_content)
        print(f'转换完成，输出文件为{output_file}')
    except Exception as e:
        print(f'发生错误: {str(e)}')

if __name__ == '__main__':
    main()
