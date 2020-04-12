import os
import shutil
import string
import argparse

CONFIGS = {
    'cnn': {
        'destination': 'output_cnn',
        'presets': {
            'src/dataset.py': 'datasets/dataset_cnn.py',
            'src/viz.py': 'visualizers/viz_cnn.py'
        },
        'substitutions': {
        }
    }
}

def init_pipeline():
    parser = argparse.ArgumentParser(description='PyTorch Project Initializer')

    parser.add_argument('--project', type=str,
                        help='version of the code to generate')

    parser.add_argument('--all', action='store_true', default=False,
                        help='generate all projects')

    parser.add_argument('--output_path', type=str, default='',
                        help='folder to output the project to')

    parser.add_argument('--config_path', type=str, default='',
                        help='filepath to the config.json file')

    parser.add_argument('--visualize', action='store_true', default=True,
                        help='save visualization files')

    return parser.parse_args()


def remove_duplicate_files(destination, filename):
    # Remove file if it already exists.
    full_dest_path = os.path.join(destination, filename)
    if filename in os.listdir(destination):
        if os.path.isdir(full_dest_path):
            shutil.rmtree(full_dest_path)
        else:
            os.remove(full_dest_path)


def copy_file_or_folder(source, destination, filename):
    # If not a template, copy file over.
    full_src_path = os.path.join(source, filename)
    full_dest_path = os.path.join(destination, filename)
    if os.path.isdir(full_src_path):
        shutil.copytree(full_src_path, full_dest_path)
    else:
        shutil.copy(full_src_path, full_dest_path)
        # if any(ext in url_string for ext in extensionsToCheck):


def fill_template_files(destination, config):
    # Fill in template files with entries in config.
    for root, subdirs, files in os.walk(destination):
        if 'data' in root or 'checkpoints' in root or 'cache' in root: # TODO use .gitignore instead
            continue
        for filename in files:
            if '_temp.py' in filename:
                result = ''
                full_src_path = os.path.join(root, filename)
                with open(full_src_path) as in_file:
                    contents = string.Template(in_file.read())
                    result = contents.substitute(config['substitutions'])

                new_dest_path = full_src_path.replace('_temp', '')
                with open(new_dest_path, 'w') as out_file:
                    out_file.write(result)
                os.remove(full_src_path)


def add_config_files(destination, config):
    # Copy additional files specified in config, such as dataset.py
    presets = config['presets']
    for key, src_path in presets.items():
        if os.path.isfile(src_path):
            dest_path = os.path.join(destination, key)
            shutil.copy(src_path, dest_path)
        else:
            print("Path not found.")


def create_project_folder(config):
    source = 'source'
    destination = config['destination']

    # Create destination directory if it doesn't exist
    if not os.path.isdir(destination):
        os.makedirs(destination)

    for filename in os.listdir(source):
        remove_duplicate_files(destination, filename)
        copy_file_or_folder(source, destination, filename)

    fill_template_files(destination, config)
    add_config_files(destination, config)


def main():
    args = init_pipeline()
    if args.all:
        for proj in CONFIGS:
            create_project_folder(CONFIGS[proj])

    elif args.project in CONFIGS:
        if args.output_path == '':
            create_project_folder(CONFIGS[args.project])
        else:
            print("SPECIFY DESTINATION")

    else:
        raise ValueError


if __name__ == '__main__':
    main()
