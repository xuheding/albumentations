import cv2
import pytest
import itertools
import numpy as np

import albumentations as A
import albumentations.pytorch as ATorch

import albumentations.augmentations.functional as F
import albumentations.pytorch.augmentations.image_only.functional as FTorch

from torch.testing import assert_allclose

from ..utils import set_seed, to_tensor, from_tensor


@pytest.mark.parametrize(
    ["image", "augs"],
    itertools.product(
        [np.random.randint(0, 256, (128, 323, 3), np.uint8), np.random.random([256, 111, 3]).astype(np.float32)],
        [[A.Normalize(p=1), ATorch.NormalizeTorch(p=1)], [A.CoarseDropout(p=1), ATorch.CoarseDropoutTorch(p=1)]],
    ),
)
def test_image_transforms_rgb(image, augs):
    image_torch = to_tensor(image)

    aug_cpu = A.Compose([augs[0]])
    aug_torch = A.Compose([augs[1]])

    set_seed(0)
    image_cpu = aug_cpu(image=image)["image"]
    set_seed(0)
    image_torch = aug_torch(image=image_torch)["image"]

    image_torch = from_tensor(image_torch)
    assert_allclose(image_cpu, image_torch)


@pytest.mark.parametrize(
    ["image", "augs"],
    itertools.product(
        [np.random.randint(0, 256, (128, 323), np.uint8), np.random.random([256, 111]).astype(np.float32)],
        [
            [A.Normalize(mean=0.5, std=0.1, p=1), ATorch.NormalizeTorch(mean=0.5, std=0.1, p=1)],
            [A.CoarseDropout(p=1), ATorch.CoarseDropoutTorch(p=1)],
        ],
    ),
)
def test_image_transforms_grayscale(image, augs):
    aug_cpu = A.Compose([augs[0]])
    aug_torch = A.Compose([augs[1]])

    image_torch = to_tensor(image)

    set_seed(0)
    image_cpu = aug_cpu(image=image)["image"]
    set_seed(0)
    image_torch = aug_torch(image=image_torch)["image"]

    image_torch = from_tensor(image_torch)
    assert_allclose(image_cpu, image_torch)


def test_rgb_to_hls_float():
    image = np.random.random([1000, 1000, 3]).astype(np.float32)
    torch_img = to_tensor(image)

    cv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
    torch_img = FTorch.rgb_to_hls(torch_img)

    torch_img = from_tensor(torch_img)
    assert_allclose(cv_img, torch_img)


def test_rgb_to_hls_uint8():
    image = np.random.randint(0, 256, [1000, 1000, 3], np.uint8)
    torch_img = to_tensor(image)

    cv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
    torch_img = FTorch.rgb_to_hls(torch_img)

    torch_img = from_tensor(torch_img)
    assert np.abs(cv_img.astype(int) == torch_img.astype(int)).max() <= 1


def test_hls_to_rgb_float():
    image = np.random.random([1000, 1000, 3]).astype(np.float32)
    image[..., 0] *= 360

    torch_img = to_tensor(image)

    cv_img = cv2.cvtColor(image, cv2.COLOR_HLS2RGB)
    torch_img = FTorch.hls_to_rgb(torch_img)

    torch_img = from_tensor(torch_img)
    assert_allclose(cv_img, torch_img)


def test_hls_to_rgb_uint8():
    image = np.random.randint(0, 256, [1000, 1000, 3], np.uint8)

    torch_img = to_tensor(image)

    cv_img = cv2.cvtColor(image, cv2.COLOR_HLS2RGB)
    torch_img = FTorch.hls_to_rgb(torch_img)

    torch_img = from_tensor(torch_img)
    assert np.all(cv_img == torch_img)