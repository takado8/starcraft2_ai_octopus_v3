import os
import shutil
from distutils.dir_util import copy_tree
octopus = 'OctopusV3'
aaaaaaa = 'aaaaaaa'

zip_file_name = octopus
destination_dir_name = zip_file_name # could be different, is the same usually
zip_dir = r"C:\Users\korne\Desktop\sc2 AI"

destination_dir = os.path.join(zip_dir, destination_dir_name)
source_dir = os.path.join(zip_dir, 'starcraft2_ai_octopus_v3')

ignored_names = {'.git', '.gitattributes', '.gitignore', '.idea', 'packit.py', 'README.md', 'venv', '__pycache__'}

all_files = os.listdir(source_dir)

for name in ignored_names:
    try:
        all_files.remove(name)
    except ValueError:
        print('name {} not found'.format(name))

for name in all_files:
    source_path = os.path.join(source_dir, name)
    destination_path = os.path.join(destination_dir, name)
    print('copying {} to {}'.format(source_path, destination_path))
    if os.path.isfile(source_path):
        shutil.copy(source_path, destination_path)
    elif os.path.isdir(source_path):
        copy_tree(source_path, destination_path)

zip_file_path = os.path.join(zip_dir, zip_file_name)
zip_file_path_ext = zip_file_path + '.zip'
zip_destination_path = os.path.join(destination_dir, zip_file_name + '.zip')
try:
    os.remove(zip_file_path_ext)
except FileNotFoundError:
    print('no file at {}'.format(zip_file_path_ext))

name = shutil.make_archive(base_name=zip_file_path, format='zip', root_dir=destination_dir)
print('archive made at {}'.format(name))

if __name__ == '__main__':
    print(all_files)
