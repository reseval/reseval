from pathlib import Path

import torch
import torchvision
from torchvision.datasets import MNIST


dataset = MNIST(root='data/', download=True)
test_dataset = MNIST(root='data/', train=False)

data, targets = test_dataset.data, test_dataset.targets

results = {}
for datum, target in zip(data, targets):
    target = int(target)
    if target < 5:
        if target in results and len(results[target]) < 5:
            results[target].append(datum)
        elif target not in results:
            results[target] = [datum]

directory = Path('mnist')
for key, values in results.items():
    for i, value in enumerate(values):
        file = directory / f'{i}/{key}.png'
        file.parent.mkdir(exist_ok=True, parents=True)
        torchvision.utils.save_image(value.float() / 255, file)
