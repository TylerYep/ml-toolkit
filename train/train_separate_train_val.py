import os
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
import torchsummary
if torch.cuda.is_available():
    from tqdm import tqdm_notebook as tqdm
else:
    from tqdm import tqdm

import util
from util import Metrics, Mode
from args import init_pipeline
from dataset import load_train_data, INPUT_SHAPE
from models import BasicCNN as Model
from viz import visualize


def main():
    args, device = init_pipeline()
    criterion = F.nll_loss
    model = Model().to(device)
    torchsummary.summary(model, INPUT_SHAPE)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    checkpoint = util.load_checkpoint(args.checkpoint, model, optimizer) if args.checkpoint else None
    run_name = checkpoint['run_name'] if checkpoint else util.get_run_name()
    start_epoch = checkpoint['epoch'] if checkpoint else 1


    def train_model(train_loader, metrics):  # , model, device, criterion, run_name, optimizer):
        model.train()
        metrics.set_num_examples(len(train_loader))
        with tqdm(desc='Train', total=len(train_loader), ncols=120) as pbar:
            for i, (data, target) in enumerate(train_loader):
                data, target = data.to(device), target.to(device)
                optimizer.zero_grad()
                if i == 0 and metrics.epoch == 1:
                    visualize(data, target, run_name)
                output = model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                update_metrics(metrics, pbar, i, loss, output, target, Mode.TRAIN)
        return get_results(metrics, Mode.TRAIN)


    def validate_model(val_loader, metrics):  # , model, device, criterion, run_name):
        model.eval()
        metrics.set_num_examples(len(val_loader))
        with torch.no_grad():
            with tqdm(desc='Val', total=len(val_loader), ncols=120) as pbar:
                for i, (data, target) in enumerate(val_loader):
                    data, target = data.to(device), target.to(device)
                    output = model(data)
                    loss = criterion(output, target)
                    update_metrics(metrics, i, pbar, loss, output, target, Mode.VAL)
        return get_results(metrics, Mode.VAL)


    metric_names = ('epoch_loss', 'running_loss', 'epoch_acc', 'running_acc')
    metrics = Metrics(SummaryWriter(run_name), metric_names, args.log_interval)
    train_loader, val_loader = load_train_data(args)

    best_loss = np.inf
    for epoch in range(start_epoch, args.epochs + 1):
        print(f'Epoch [{epoch}/{args.epochs}]')
        metrics.set_epoch(epoch)
        train_loss = train_and_validate(train_loader, metrics, Mode.TRAIN)
        val_loss = train_and_validate(val_loader, metrics, Mode.VAL)

        is_best = val_loss < best_loss
        best_loss = min(val_loss, best_loss)
        util.save_checkpoint({
            'state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'rng_state': torch.get_rng_state(),
            'run_name': run_name,
            'epoch': epoch
        }, run_name, is_best)


def update_metrics(metrics, pbar, i, loss, output, target, mode):
    accuracy = (output.argmax(1) == target).float().mean()
    metrics.update('epoch_loss', loss.item())
    metrics.update('running_loss', loss.item())
    metrics.update('epoch_acc', accuracy.item())
    metrics.update('running_acc', accuracy.item())

    if i % metrics.log_interval == 0:
        num_steps = (metrics.epoch-1) * metrics.num_examples + i
        metrics.write(f'{mode} Loss', metrics.running_loss / metrics.log_interval, num_steps)
        metrics.write(f'{mode} Accuracy', metrics.running_acc / metrics.log_interval, num_steps)
        metrics.reset(['running_loss', 'running_acc'])

    pbar.set_postfix({'Loss': f'{loss.item():.5f}', 'Accuracy': accuracy.item()})
    pbar.update()


def get_results(metrics, mode):
    total_loss = metrics.epoch_loss / metrics.num_examples
    total_acc = 100. * metrics.epoch_acc / metrics.num_examples
    print(f'{mode} Loss: {total_loss:.4f} Accuracy: {total_acc:.2f}%')
    metrics.write(f'{mode} Epoch Loss', total_loss, metrics.epoch)
    metrics.write(f'{mode} Epoch Accuracy', total_acc, metrics.epoch)
    metrics.reset()
    return total_loss



if __name__ == '__main__':
    main()