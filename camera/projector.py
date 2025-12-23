#! /usr/bin/env python3
"""
    Distort image considering the projector distortion to project perfect
    rectangular grid for camera calibration

    Pairs of point coordinates hato be given (source and target position) and
    a distorted image as input

    use projector.py --help to see parameters
"""
from os import path
import argparse
import numpy as np
import cv2
import skimage as ski
class Projector:
    """ class to distort image before projection to get perfect (undistorted)
        image on canvas

        :param src: numpy array (n, 2) with source (measured) coordinates
        :param dst: numpy array (n, 2) with perfect coordinates
    """

    def __init__(self, src, dst):
        """ initialize """
        self.src = src.astype(np.float32)
        self.dst = dst.astype(np.float32)

    @property
    def nump(self) -> int:
        """ returns the number of points """
        if self.src is not None and self.dst is not None:
            n = self.src.shape[0]
            m = self.dst.shape[0]
            return min(n, m)
        return 0

    def homography(self, img):
        """ calculate homography transformation parameters
            no projector distortion supposed
 
            :param img: image to distort
        """
        if self.nump < 4:
            raise ValueError("Few points for transformation")
        tps = ski.transform.ProjectiveTransform.from_estimate(self.dst, self.src)
        corrected_img = ski.transform.warp(img, tps)
        # Scale to 0-255 and convert to uint8
        img_uint8 = (255 * corrected_img).astype(np.uint8)
        return img_uint8

    def inverse_camera(self, img):
        """ radial and tangential distortions supposed
        """
        if self.nump < 6:
            raise ValueError("Few points for transformation")
        # add z to object points
        obj_pnts = np.hstack([self.src, np.zeros((self.nump, 1), dtype=np.float32)])
        ret, K, dist, rvecs, tvecs = cv2.calibrateCamera([obj_pnts], [self.dst],
                                                         (img.shape[1], img.shape[0]),
                                                         None, None,
                                                         flags=cv2.CALIB_ZERO_TANGENT_DIST)
        corrected_img = cv2.undistort(img, K, dist)
        return corrected_img

    def thin_plate(self, img):
        """ use thin plate spline warp
            useful for homology and radial/tangential transformation
        """
        if self.nump < 9:
            raise ValueError("Few points for transformation")
        tps = ski.transform.ThinPlateSplineTransform.from_estimate(self.src, self.dst)
        corrected_img = ski.transform.warp(img, tps)
        # Scale to 0-255 and convert to uint8
        img_uint8 = (255 * corrected_img).astype(np.uint8)
        return img_uint8

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--points', type=str, required=True,
                        help='input coordinate file (n, 4)')
    parser.add_argument('-i', '--image', type=str, required=True,
                        help='image file to distort')
    parser.add_argument('-t', '--trans', type=str, required=True,
                        help='Transformation type 1/2/3 or h/r/t - homology/radial-tangential/thin plate spline, more value can be specified')
    args = parser.parse_args()
    coords = np.loadtxt(args.points)    # space separated input
    img = cv2.imread(args.image)

    base_name, ext = path.splitext(args.image)
    proj = Projector(coords[:,:2], coords[:,2:])    # source, destination

    if '1' in args.trans or 'h' in args.trans:
        img_hom = proj.homography(img)
        cv2.imwrite(base_name + '_hom' + ext, img_hom)
    if '2' in args.trans or 'r' in args.trans:
        img_inv = proj.inverse_camera(img)
        cv2.imwrite(base_name + '_inv' + ext, img_inv)
    if '3' in args.trans or 't' in args.trans:
        img_thn = proj.thin_plate(img)
        cv2.imwrite(base_name + '_thn' + ext, img_thn)
