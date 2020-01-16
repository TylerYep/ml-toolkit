import random
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim

import util
from args import init_pipeline
from dataset import load_train_data, INPUT_SHAPE
from metric_tracker import MetricTracker, Mode
from models import $model as Model
from verify import verify_model
from viz import visualize, visualize_trained

if torch.cuda.is_available():
    from tqdm import tqdm_notebook as tqdm
else:
    from tqdm import tqdm


# Adding metrics here will automatically search the metrics/ folder for an implementation.
METRIC_NAMES = ['Loss', 'Accuracy']


def train_and_validate(model, loader, optimizer, criterion, device, metrics, mode) -> float:
    if mode == Mode.TRAIN:
        model.train()
        torch.set_grad_enabled(True)
    else:
        model.eval()
        torch.set_grad_enabled(False)

    metrics.set_num_examples(len(loader))
    with tqdm(desc=str(mode), total=len(loader), ncols=120) as pbar:
        for i, (data, target) in enumerate(loader):
            data, target = data.to(device), target.to(device)

            if mode == Mode.TRAIN:
                optimizer.zero_grad()

            output = model(data)
            loss = criterion(output, target)

            if mode == Mode.TRAIN:
                loss.backward()
                optimizer.step()

            tqdm_dict = metrics.batch_update(i, data, loss, output, target, mode)
            pbar.set_postfix(tqdm_dict)
            pbar.update()

    return metrics.get_epoch_results(mode)


def main():
    args, device, checkpoint = init_pipeline()
    criterion = $loss_fn
    train_loader, val_loader, class_labels, init_params = load_train_data(args)
    model = Model(*init_params).to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    verify_model(model, train_loader, optimizer, device, criterion)
    util.load_state_dict(checkpoint, model, optimizer)

    run_name = checkpoint.get('run_name', util.get_run_name(args))
    metric_checkpoint = checkpoint.get('metric_obj', {})
    metrics = MetricTracker(METRIC_NAMES, run_name, args.log_interval, **metric_checkpoint)
    metrics.add_network(model, train_loader, device)
    visualize(model, train_loader, class_labels, device, run_name)

    util.set_rng_state(checkpoint)
    start_epoch = metrics.epoch + 1
    for epoch in range(start_epoch, start_epoch + args.epochs):
        print(f'Epoch [{epoch}/{start_epoch + args.epochs - 1}]')
        metrics.next_epoch()
        train_loss = train_and_validate(model, train_loader, optimizer, criterion,
                                        device, metrics, Mode.TRAIN)
        val_loss = train_and_validate(model, val_loader, optimizer, criterion,
                                      device, metrics, Mode.VAL)

        is_best = metrics.update_best_metric(val_loss)
        util.save_checkpoint({
            'model_init': init_params,
            'state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'rng_state': random.getstate(),
            'np_rng_state': np.random.get_state(),
            'torch_rng_state': torch.get_rng_state(),
            'run_name': run_name,
            'metric_obj': metrics.json_repr()
        }, run_name, is_best)

    visualize_trained(model, train_loader, class_labels, device, run_name)


if __name__ == '__main__':
    main()
