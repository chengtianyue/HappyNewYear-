from PIL import Image
import os
import numpy as np
from tqdm import tqdm


class Config:
    corp_size = 40
    filter_size = 20
    num = 100


class PicMerge:

    def __init__(self, pic_path, mode='RGB', pic_folder='wechat'):
        if mode.upper() not in ('RGB', 'L'):
            raise ValueError('Only accept "RGB" or "L" MODE, but we received "{}".'.format(self.mode))
        else:
            self.mode = mode.upper()
        print('Coding for every picture in folder "{}".'.format(pic_folder))
        self.mapping_table, self.pictures = self.mapping_table(pic_folder)
        self.picture = self.resize_pic(pic_path).convert(self.mode)

    @staticmethod
    def resize_pic(pic_path):
        picture = Image.open(pic_path)
        width, height = picture.size
        to_width = Config.corp_size * Config.num
        to_height = ((to_width / width) * height // Config.corp_size) * Config.corp_size
        picture = picture.resize((int(to_width), int(to_height)), Image.ANTIALIAS)
        return picture

    def merge(self):
        width, height = self.picture.size
        w_times, h_times = int(width / Config.corp_size), int(height / Config.corp_size)
        picture = np.array(self.picture)
        print('Corp & Merge...')
        for i in tqdm(range(w_times), desc='CORP'):
            for j in range(h_times):
                if self.mode == 'L':
                    section = picture[j * Config.corp_size:(j + 1) * Config.corp_size,
                                      i * Config.corp_size:(i + 1) * Config.corp_size]
                    section_mean = section.mean()
                    candidate = sorted([(key_, abs(np.array(value_).mean() - section_mean))
                                        for key_, value_ in self.pictures.items()],
                                       key=lambda item: item[1])[:Config.filter_size]
                    most_similar = self.structure_similarity(section, candidate)
                    picture[j * Config.corp_size:(j + 1) * Config.corp_size,
                            i * Config.corp_size:(i + 1) * Config.corp_size] = most_similar
                elif self.mode == 'RGB':
                    section = picture[j * Config.corp_size:(j + 1) * Config.corp_size,
                                      i * Config.corp_size:(i + 1) * Config.corp_size, :]
                    candidate = self.color_similarity(section)
                    most_similar = self.structure_similarity(section, candidate)
                    picture[j * Config.corp_size:(j + 1) * Config.corp_size,
                            i * Config.corp_size:(i + 1) * Config.corp_size, :] = most_similar

        picture = Image.fromarray(picture)
        picture.show()
        picture.save('result.jpg')
        print('Work Done...')

    def structure_similarity(self, section, candidate):
        section = Image.fromarray(section).convert('L')
        one_hot = self.pic_code(np.array(section.resize((8, 8), Image.ANTIALIAS)))
        candidate = [(key_, np.equal(one_hot, self.mapping_table[key_]).mean()) for key_, _ in candidate]
        most_similar = max(candidate, key=lambda item: item[1])
        return self.pictures[most_similar[0]]

    def color_similarity(self, pic_slice, top_n=Config.filter_size):
        slice_mean = self.rgb_mean(pic_slice)
        diff_list = [(key_, np.linalg.norm(slice_mean - self.rgb_mean(value_)))
                     for key_, value_ in self.pictures.items()]
        filter_ = sorted(diff_list, key=lambda item: item[1])[:top_n]
        return filter_

    @staticmethod
    def rgb_mean(rgb_pic):
        """
        if picture is RGB channel, calculate average [R, G, B].
        """
        r_mean = np.mean(rgb_pic[:, :, 0])
        g_mean = np.mean(rgb_pic[:, :, 1])
        b_mean = np.mean(rgb_pic[:, :, 2])
        val = np.array([r_mean, g_mean, b_mean])
        return val

    def mapping_table(self, pic_folder):
        """
        What this function do?
        1. transverse every image in PIC_FOLDER;
        2. resize every image in (8, 8) and covert into GREY;
        3. CODE for every image, CODE like [1, 0, 1, 1, 0....1]
        4. build a dict to gather all image and its CODE.
        :param pic_folder: path of pictures folder.
        :return: a dict
        """
        suffix = ['jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG']
        if not os.path.isdir(pic_folder):
            raise OSError('Folder [{}] is not exist, please check.'.format(pic_folder))

        pic_list = os.listdir(pic_folder)
        results = {}
        pic_dic = {}
        for idx, pic in tqdm(enumerate(pic_list), desc='CODE'):
            if pic.split('.')[-1] in suffix:
                path = os.path.join(pic_folder, pic)
                try:
                    img = Image.open(path).resize((Config.corp_size, Config.corp_size), Image.ANTIALIAS)
                    results[idx] = self.pic_code(np.array(img.convert('L').resize((8, 8), Image.ANTIALIAS)))
                    if self.mode == 'RGB':
                        pic_dic[idx] = np.array(img.convert(self.mode))
                    else:
                        pic_dic[idx] = np.array(img.convert(self.mode))
                except OSError:
                    pass
        return results, pic_dic

    @staticmethod
    def pic_code(image: np.ndarray):
        """
        To make a one-hot code for IMAGE.
        AVG is mean of the array(IMAGE).
        Traverse every pixel of IMAGE, if the pixel value is more then AVG, make it 1, else 0.
        :param image: an array of picture
        :return: A sparse list with length [picture's width * picture's height].
        """
        width, height = image.shape
        avg = image.mean()
        one_hot = np.array([1 if image[i, j] > avg else 0 for i in range(width) for j in range(height)])
        return one_hot


if __name__ == "__main__":
    P = PicMerge(pic_path='11.jpg', mode='RGB')
    P.merge()