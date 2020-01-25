import sys
import torch
import torchsummary

from src import util
from src.dataset import INPUT_SHAPE

if 'google.colab' in sys.modules:
    from tqdm import tqdm_notebook as tqdm
else:
    from tqdm import tqdm


def verify_model(model, train_loader, optimizer, device, criterion):
    """
    Performs all necessary validation on your model to ensure correctness.
    You may need to change the batch_size or max_iters in overfit_example
    in order to overfit the batch.
    """
    torchsummary.summary(model, INPUT_SHAPE)
    check_batch_dimension(model, train_loader, optimizer, device)
    overfit_example(model, train_loader, optimizer, device, criterion)
    print('Verification complete - all tests passed!')


def overfit_example(model, loader, optimizer, device, criterion, batch_size=5, max_iters=50):
    """
    Verifies that the provided model can overfit a single batch or example.
    """
    model.eval()
    torch.set_grad_enabled(True)
    data, target = util.get_data_example(loader, device)
    data, target = data[:batch_size], target[:batch_size]
    with tqdm(desc='Verify Model', total=max_iters, ncols=120) as pbar:
        for _ in range(max_iters):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            if torch.allclose(loss, torch.tensor(0.)):
                break
            loss.backward()
            optimizer.step()
            pbar.set_postfix({'Loss': loss.item()})
            pbar.update()

    assert torch.allclose(loss, torch.tensor(0.))


def check_batch_dimension(model, loader, optimizer, device, test_val=2):
    """
    Verifies that the provided model loads the data correctly. We do this by setting the
    loss to be something trivial (e.g. the sum of all outputs of example i), running the
    backward pass all the way to the input, and ensuring that we only get a non-zero gradient
    on the i-th input.
    See details at http://karpathy.github.io/2019/04/25/recipe/.
    """
    model.eval()
    torch.set_grad_enabled(True)
    data, _ = util.get_data_example(loader, device)
    optimizer.zero_grad()
    data.requires_grad_()

    output = model(data)
    loss = output[test_val].sum()
    loss.backward()

    assert loss.data != 0
    assert (data.grad[test_val] != 0).any()
    assert (data.grad[:test_val] == 0.).all() and (data.grad[test_val+1:] == 0.).all()