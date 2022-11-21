from scipy.fftpack import fft, fftfreq, fftshift, ifft
from skimage.util import compare_images
import matplotlib.pyplot as plt
import scipy.signal as signal
from skimage import filters
from scipy import ndimage
import numpy as np
import cv2

class ImageFilter:
    def __init__(self, image):
        self.image = image
        
    def ImageCenterCrop(self, image, scale):
        height, width = image.shape
        cropped_image = image[int(height*scale):int(height*(1-scale)), int(width*scale):int(width*(1-scale))]
        return cropped_image

    def ImageResize_Grayscale(self, image, scale):
        image = cv2.resize(image, (0,0), fx=scale, fy=scale)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def FourierTransform(self, image):
        f = fft(image)
        fshift = fftshift(f)
        magnitude_spectrum = 20*np.log(np.abs(fshift))
        return magnitude_spectrum

    def InverseFourierTransform(self, image):
        fshift = fftshift(image)
        f_ishift = np.fft.ifftshift(fshift)
        img_back = np.fft.ifft(f_ishift)
        img_back = np.abs(img_back)
        return img_back

    # fftfreq
    def fftfreq(self, n, d=1.0):
        val = 1.0/(n*d)
        results = np.empty(n, int)
        N = (n-1)//2 + 1
        p1 = np.arange(0, N, dtype=int)
        results[:N] = p1
        p2 = np.arange(-(n//2), 0, dtype=int)
        results[N:] = p2
        return results * val

    def ImageShow(self, image, title):
        plt.imshow(image, cmap='gray')
        plt.title(title)
        plt.show()

    def GaussianFilter(self, image, sigma=1):
        h = self.gaussian_filter(image.shape, sigma)
        filtered_image = signal.convolve2d(image, h, mode='same', boundary='symm')
        return filtered_image

    def gaussian_filter(self, shape, sigma=1):
        m, n = [(ss-1.)/2. for ss in shape]
        y, x = np.ogrid[-m:m+1,-n:n+1]
        h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
        h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
        hsum = np.sum(h)
        if hsum != 0:
            h /= hsum
        return h

    def LaplacianOfGaussianFilter(self, image, sigma=1): # Edge detection
        h = self.laplacian_of_gaussian_filter(image.shape, sigma)
        filtered_image = signal.convolve2d(image, h, mode='same', boundary='symm')
        return filtered_image

    def laplacian_of_gaussian_filter(self, shape, sigma=1): 
        m, n = [(ss-1.)/2. for ss in shape]
        y, x = np.ogrid[-m:m+1,-n:n+1]
        h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
        h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
        h = -h * (x*x + y*y - 2*sigma*sigma) / (sigma*sigma*sigma*sigma)
        hsum = np.sum(h)
        if hsum != 0:
            h /= hsum
        return h

    def SharpeningHighPass(self, image, sigma):
        h = self.laplacian_of_gaussian_filter(image.shape, sigma)
        filtered_image = signal.convolve2d(image, h, mode='same', boundary='symm')
        filtered_image = image + filtered_image
        return filtered_image

    def HighPassFilter(self, image, sigma=1):
        h = self.gaussian_filter(image.shape, sigma)
        filtered_image = image - h
        return filtered_image

    def LowPassFilter(self, image, sigma=1):
        h = self.gaussian_filter(image.shape, sigma)
        filtered_image = signal.convolve2d(image, h, mode='same', boundary='symm')
        return filtered_image

    def MedianFilter(self, image, size=3):
        filtered_image = ndimage.median_filter(image, size=size)
        return filtered_image

    def MeanFilter(self, image, size=3):
        filtered_image = ndimage.uniform_filter(image, size=size)
        return filtered_image

    def CannyEdgeDetection(self, image, sigma=1):
        h = self.gaussian_filter(image.shape, sigma)
        filtered_image = signal.convolve2d(image, h, mode='same', boundary='symm')
        edges = cv2.Canny(np.uint8(filtered_image), 100, 200)
        return edges

    def LaplacianEdgeDetection(self, image, sigma=1):
        h = self.laplacian_of_gaussian_filter(image.shape, sigma)
        filtered_image = signal.convolve2d(image, h, mode='same', boundary='symm')
        return filtered_image

    def SobelFilter(self, image):
        filtered_image = ndimage.sobel(image)
        return filtered_image

    def PrewittFilter(self, image):
        filtered_image = ndimage.prewitt(image)
        return filtered_image

    def denoise(self, image, weight):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = np.float32(image)
        image = cv2.GaussianBlur(image, (3, 3), 0)
        dst = cv2.fastNlMeansDenoising(image, None, weight, 7, 21)
        return dst