"""LIBRARIES"""

import numpy as np
from readlif.reader import LifFile
from matplotlib import pyplot as plt
from numba import jit

"""LOAD IMAGE FILE"""

new = LifFile('file.lif')

"""SHOW EXAMPLE IMAGES"""

"""for image in new.get_iter_image():
    channel_list = []
    for channel in image.get_iter_c():
        arr = np.array(channel)
        arr = arr - arr.min()
        arr = arr / arr.max()
        arr = arr * 255
        channel_list.append(arr)

    plt.subplot(1, 2, 1)
    plt.imshow(channel_list[0])
    plt.subplot(1, 2, 2)
    plt.imshow(channel_list[1])
    plt.show()"""

"""FUNCTIONS"""


def pre_processing(image_array):
    image_array = image_array - image_array.min()
    image_array = image_array / image_array.max()
    image_array = image_array * 255
    return image_array


@jit(nopython=True, parallel=True)  # improves performance of function by compiling loops and so on
def contains(list_test, value):
    for i in list_test:
        if value in i:
            return True
    return False


@jit(nopython=True, parallel=True)
def determine_roi(channel_list):
    roi_list = []
    flat_channel = channel_list[0].flatten()
    for pixel_index, pixel in enumerate(flat_channel):  # loops over all ~4 mio pixels
        if larger_than_threshold(pixel) and not contains(roi_list, pixel_index):  # check if the pixel is over
            # threshold and if it wasnt checked yet
            print("-----------------------------------------------------------")
            print("new cluster:", pixel_index)
            roi_list.append(gen_cluster(pixel_index, flat_channel))  # generates a new cluster and finds all the
            # neighbors belonging to it

    return roi_list


@jit(nopython=True, parallel=True)
def larger_than_threshold(pixel):
    if pixel > 70:
        return True
    else:
        return False


@jit(nopython=True, parallel=True)
def get_adj(pixel):
    y_dim = 2048
    adjacent_pixel_list = [pixel - y_dim,
                           pixel - 1,
                           pixel + 1,
                           pixel + y_dim,
                           pixel - y_dim + 1,
                           pixel - y_dim - 1,
                           pixel + y_dim - 1,
                           pixel + y_dim + 1]

    return adjacent_pixel_list


@jit(nopython=True, parallel=True)
def gen_cluster(first_pixel, channel):
    cluster = []
    cluster_adj_list = [first_pixel]
    i = 0
    running = True

    while running:
        pixel = cluster_adj_list[i]
        if larger_than_threshold(channel[pixel]) and pixel not in cluster:  # check if a pixel is part of the cluster
            cluster.append(pixel)  # add the pixel to the cluster
            pixel_adj_list = get_adj(pixel)  # calculate the neighbors of the pixel

            for adj in pixel_adj_list:
                if adj not in cluster_adj_list and 0 <= adj <= 4194304:  # check if the neighbors should be added to the "to be checked list"
                    cluster_adj_list.append(adj)

        i += 1
        if i >= len(cluster_adj_list):  # check if there are pixels to beck checked left
            running = False

    print("cluster", np.shape(cluster))

    return cluster


def post_processing(list_of_lists):
    for cell_index, cells in enumerate(list_of_lists):
        if len(cells) < 100:
            del list_of_lists[cell_index]
    return list_of_lists


"""ANALYSIS"""

for image in new.get_iter_image():
    channel_list = []
    for channel in image.get_iter_c():
        arr = np.array(channel)
        arr = pre_processing(arr)
        channel_list.append(arr)

    roi_array = determine_roi(channel_list)
    print("number of cells ", len(roi_array))

    roi_array = post_processing(roi_array)

    print("number of cells ", len(roi_array))

    roi_image = np.zeros(np.shape(channel_list[0]))

    for roi in roi_array:
        for pixel_index in roi:
            y = pixel_index // 2048
            x = pixel_index % 2048
            roi_image[y, x] = 255

    plt.subplot(1, 2, 1)
    plt.imshow(roi_image)
    plt.subplot(1, 2, 2)
    plt.imshow(channel_list[0])
    plt.show()
