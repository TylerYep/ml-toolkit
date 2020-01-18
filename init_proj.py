import os
import shutil
import string
import argparse


RNN_CONFIG = {
    'presets': {
        'datasets': 'dataset_rnn',
    },
    'substitutions': {
        'loss_fn': 'nn.CrossEntropyLoss()',
        'model': 'BasicRNN'
    }
}

CNN_CONFIG = {
    'presets': {
        'datasets': 'dataset_cnn',
    },
    'substitutions': {
        'loss_fn': 'F.nll_loss',
        'model': 'BasicCNN'
    }
}


def init_project(source, destination, config):
    # Create destination directory if it doesn't exist
    if not os.path.isdir(destination):
        os.makedirs(destination)

    # Copy all files over to the destination directory.
    for filename in os.listdir(source):
        if 'data' in filename:
            continue

        full_src_path = os.path.join(source, filename)
        full_dest_path = os.path.join(destination, filename)

        # Remove file if it already exists.
        if filename in os.listdir(destination):
            if os.path.isdir(full_dest_path):
                shutil.rmtree(full_dest_path)
            else:
                os.remove(full_dest_path)

        # Fill in template files with entries in config.
        if '_temp.py' in filename:
            result = ''
            with open(full_src_path) as in_file:
                contents = string.Template(in_file.read())
                result = contents.substitute(config['substitutions'])

            new_dest_path = full_dest_path.replace('_temp', '')
            with open(new_dest_path, 'w') as out_file:
                out_file.write(result)

        # If not a template, copy file over.
        else:
            if os.path.isdir(full_src_path):
                shutil.copytree(full_src_path, full_dest_path)
            else:
                shutil.copy(full_src_path, destination)

    # Copy additional files specified in config, such as dataset.py
    presets = config['presets']
    for key in presets:
        if os.path.isdir(key):
            chosen_file = presets[key]
            if '.py' not in presets[key]:
                chosen_file += '.py'
            key_src_path = os.path.join(key, chosen_file)
            key_dest_path = os.path.join(destination, 'dataset.py')
            shutil.copy(key_src_path, key_dest_path)


def init_pipeline():
    parser = argparse.ArgumentParser(description='PyTorch Project Initializer')

    parser.add_argument('project', type=str,
                        help='version of the code to generate')

    parser.add_argument('--output_path', type=int, default=100, metavar='N',
                        help='folder to output the project to')

    parser.add_argument('--config_path', type=str, default='',
                        help='filepath to the config.json file')

    parser.add_argument('--visualize', action='store_true', default=True,
                        help='save visualization files')

    return parser.parse_args()


def main():
    args = init_pipeline()
    if args.project == 'rnn':
        config = RNN_CONFIG
    elif args.project == 'cnn':
        config = CNN_CONFIG
    else:
        raise ValueError
    
    source = 'src/'
    destination = f'output_{args.project}/'
    init_project(source, destination, config)


if __name__ == '__main__':
    main()
