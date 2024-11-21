import os

def get_file_name(file_path):
    file_name = os.path.basename(file_path).split('/')[-1]
    file_tuple = os.path.splitext(file_name)
    return file_name, file_name[0]