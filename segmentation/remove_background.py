import os
import glob
import cv2
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import argparse

from utils import load_dataset_images, get_sam_model

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", required=True, help="Directory containing images we have masks for. ex: /User/micheller/images")
    parser.add_argument("--masks", required=True, help="Directory containing masks for images. ex: /User/micheller/masks")
    return parser.parse_args()

def remove_background_color_based(image, mask):
    # Create an image with white background
    white_background = np.full(image.shape, 255, dtype=np.uint8)

    # Apply the mask to the white background, where mask is not zero, we will fill it with the image's color
    masked_foreground = cv2.bitwise_and(image, image, mask=mask) #mask=255-mask #wings
    background = cv2.bitwise_and(white_background, white_background, mask=mask)
    background = 255 - background

    # Combine the masked foreground with the background
    final_image = cv2.add(masked_foreground, background)

    return final_image

def main():
    args = parse_args()

    # load in our images
    image_dataset_folder = args.images + '/*'
    dataset_images, image_filepaths = load_dataset_images(image_dataset_folder, 1)
    main_folder_name = args.images.split('/')[-1]

    #load in our masks
    mask_dataset_folder = args.masks + '/*'
    dataset_masks, mask_filepaths = load_dataset_images(mask_dataset_folder)
    
    errors = []
    for (image, mask), fp in zip(zip(dataset_images, dataset_masks), image_filepaths): 
        #remove background from color image and replace it with a WHITE background
        img_removed_background = remove_background_color_based(image, mask) 

        #save the image with the removed background under its own folder
        bck_img_path = fp.replace(main_folder_name, f'{main_folder_name}_removed_background_WHITE')
        fn = "/" + bck_img_path.split('/')[-1]
        background_folder = bck_img_path.replace(fn, "")
        os.makedirs(background_folder, exist_ok=True)

        #save the resized cropped wings to their path
        try:
            cv2.imwrite(bck_img_path, cv2.cvtColor(img_removed_background, cv2.COLOR_RGB2BGR))
        except FileNotFoundError:
            errors.append(bck_img_path)
            
    print('The following images could encountered errors during background removal:', errors)
    return


if __name__ == "__main__":
    main()