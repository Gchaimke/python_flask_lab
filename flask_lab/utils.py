
import os
from flask_lab import const


def chunk_list(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def get_images(folder=const.POWER_SUPPLIES_FOLDER, formats=('.jpg', '.jpeg', '.png'), page=0, per_page=18):
    data = []
    next = None
    for file in os.listdir(f'{const.PUBLIC_IMAGES_FOLDER}/{folder}'):
        if file.lower().endswith(formats):
            data.append((file, f'{folder}/{file}'))
    total_pages = len(data) // per_page
    if chunked := chunk_list(data, per_page):
        if page + 1 < len(chunked):
            next = page + 1
        if page > len(chunked) - 1:
            page = len(chunked) - 1
        return {'total_pages': total_pages, 'next_page': next, 'images': chunked[page]} 
    return {'total_pages': total_pages, 'next_page': None, 'images': data}
