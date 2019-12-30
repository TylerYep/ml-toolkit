import os
import torch
import matplotlib.pyplot as plt
import numpy as np
from dataset import load_train_data
from args import init_pipeline


def visualize(data, target, run_name=''):
    ''' Data is of shape (B, C, H, W) '''
    NUM_SUBPLOTS = 24
    NUM_ROWS = 4
    plot_num = 0
    fig = plt.figure(figsize=(25, 16))
    for i in range(0, data.shape[0] - NUM_SUBPLOTS, NUM_SUBPLOTS):
        for j in range(NUM_SUBPLOTS):
            # Subplot: a x b, cth subplot
            ax = fig.add_subplot(NUM_ROWS, NUM_SUBPLOTS // NUM_ROWS + 1, j+1, label=plot_num)
            img = data[i+j].permute(1, 2, 0).squeeze()
            # label = int(target[i+j])
            plt.imshow(img)
            ax.axis('off')
            # ax.set_title(label)
            plot_num += 1

    if run_name:
        plt.savefig(os.path.join(run_name, 'input_data.png'))
        plt.clf()
    else:
        plt.show()


def compute_activations(model, inputs, run_name=''):
    plot_num = 0
    fig = plt.figure(figsize=(25, 16))
    _, activations = model.forward_with_activations(inputs)
    NUM_SUBPLOTS = len(activations)
    for i, activation in enumerate(activations):
        activation = torch.abs(activation).mean(dim=1)[0].detach().numpy()
        activation /= activation.max()
        activation = plt.get_cmap('inferno')(activation)
        activation = np.delete(activation, 3, 2)  # deletes 4th channel created by cmap
        ax = fig.add_subplot(1, NUM_SUBPLOTS + 1, i+1, label=plot_num)
        plt.imshow(activation)
        ax.axis('off')
        plot_num += 1

    if run_name:
        plt.savefig(os.path.join(run_name, f'activation_layers.png'))
        plt.clf()
    else:
        plt.show()


def compute_saliency(inputs, run_name=''):
    saliency = inputs.grad.data
    saliency, _ = torch.max(saliency, dim=1)  # dim 1 is the channel dimension
    plt.imshow(saliency.numpy()[0], cmap=plt.cm.gray)
    plt.axis('off')
    # plt.gcf().set_size_inches(12, 5)
    if run_name:
        plt.savefig(os.path.join(run_name, 'saliency.png'))
        plt.clf()
    else:
        plt.show()


def main():
    args, _ = init_pipeline()
    train_loader, _ = load_train_data(args)
    for data, target in train_loader:
        visualize(data, target)


if __name__ == '__main__':
    main()
