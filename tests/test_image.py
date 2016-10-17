# Copyright (c) 2012-2016 by the GalSim developers team on GitHub
# https://github.com/GalSim-developers
#
# This file is part of GalSim: The modular galaxy image simulation toolkit.
# https://github.com/GalSim-developers/GalSim
#
# GalSim is free software: redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions, and the disclaimer given in the accompanying LICENSE
#    file.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, and the disclaimer given in the documentation
#    and/or other materials provided with the distribution.
#

"""Unit tests for the Image class.

These tests use four externally generated (IDL + astrolib FITS writing tools) reference images for
the Image unit tests.  These are in tests/data/.

Each image is 5x7 pixels^2 and if each pixel is labelled (x, y) then each pixel value is 10*x + y.
The array thus has values:

15 25 35 45 55 65 75
14 24 34 44 54 64 74
13 23 33 43 53 63 73  ^
12 22 32 42 52 62 72  |
11 21 31 41 51 61 71  y

x ->

With array directions as indicated. This hopefully will make it easy enough to perform sub-image
checks, etc.

Images are in S, I, F, D, and C flavours.

There are also four FITS cubes, and four FITS multi-extension files for testing.  Each is 12
images deep, with the first image being the reference above and each subsequent being the same
incremented by one.

"""

from __future__ import print_function
import os
import sys
import numpy as np

from galsim_test_helpers import *

try:
    import galsim
except ImportError:
    path, filename = os.path.split(__file__)
    sys.path.append(os.path.abspath(os.path.join(path, "..")))
    import galsim

from galsim._pyfits import pyfits

# Setup info for tests, not likely to change
ntypes = 5  # Note: Most tests below only run through the first 5 types.
            # test_Image_basic tests all 7 types including the aliases.
types = [np.int16, np.int32, np.float32, np.float64, np.complex128, int, float, complex]
simple_types = [int, int, float, float, complex, int, float, complex]
np_types = [np.int16, np.int32, np.float32, np.float64, np.complex128,
            np.int32, np.float64, np.complex128]
tchar = ['S', 'I', 'F', 'D', 'C', 'I', 'D', 'C']

ncol = 7
nrow = 5
test_shape = (ncol, nrow)  # shape of image arrays for all tests
ref_array = np.array([
    [11, 21, 31, 41, 51, 61, 71],
    [12, 22, 32, 42, 52, 62, 72],
    [13, 23, 33, 43, 53, 63, 73],
    [14, 24, 34, 44, 54, 64, 74],
    [15, 25, 35, 45, 55, 65, 75] ]).astype(np.int16)
large_array = np.zeros((ref_array.shape[0]*3, ref_array.shape[1]*2), dtype=np.int16)
large_array[::3,::2] = ref_array

# Depth of FITS datacubes and multi-extension FITS files
if __name__ == "__main__":
    nimages = 12
else:
    # There really are 12, but testing the first 3 should be plenty as a unit test, and
    # it helps speed things up.
    nimages = 3

datadir = os.path.join(".", "Image_comparison_images")


@timer
def test_Image_basic():
    """Test that all supported types perform basic Image operations correctly
    """
    # Do all 8 types here, rather than just the 5 numpy types.  i.e. Test the aliases.
    for i in range(len(types)):

        # Check basic constructor from ncol, nrow
        array_type = types[i]
        np_array_type = np_types[i]
        print('array_type = ',array_type)
        print('np_array_type = ',np_array_type)

        # Check basic constructor from ncol, nrow
        im1 = galsim.Image(ncol,nrow,dtype=array_type)

        # Check basic features of array built by ImageAlloc constructor
        np.testing.assert_array_equal(im1.array, 0.)
        assert im1.array.shape == (nrow,ncol)
        assert im1.array.dtype.type == np_array_type
        assert im1.array.flags.writeable == True
        assert im1.array.flags.c_contiguous == True

        im1.fill(23)
        np.testing.assert_array_equal(im1.array, 23.)

        bounds = galsim.BoundsI(1,ncol,1,nrow)
        assert im1.getXMin() == 1
        assert im1.getXMax() == ncol
        assert im1.getYMin() == 1
        assert im1.getYMax() == nrow
        assert im1.getBounds() == bounds
        assert im1.bounds == bounds

        # Adding on xmin, ymin allows you to set an origin other than (1,1)
        im1a = galsim.Image(ncol, nrow, dtype=array_type, xmin=4, ymin=7)
        im1b = galsim.Image(ncol, nrow, dtype=array_type, xmin=0, ymin=0)
        assert im1a.getXMin() == 4
        assert im1a.getXMax() == ncol+3
        assert im1a.getYMin() == 7
        assert im1a.getYMax() == nrow+6
        assert im1a.bounds == galsim.BoundsI(4,ncol+3,7,nrow+6)
        assert im1b.getXMin() == 0
        assert im1b.getXMax() == ncol-1
        assert im1b.getYMin() == 0
        assert im1b.getYMax() == nrow-1
        assert im1b.bounds == galsim.BoundsI(0,ncol-1,0,nrow-1)

        # Also test alternate name of image type: ImageD, ImageF, etc.
        image_type = eval("galsim.Image"+tchar[i]) # Use handy eval() mimics use of ImageSIFD
        im2 = image_type(bounds, init_value=23)
        im2_view = im2.view()
        im2_cview = im2.view(make_const=True)
        im2_conj = im2.conjugate()

        assert im2_view.getXMin() == 1
        assert im2_view.getXMax() == ncol
        assert im2_view.getYMin() == 1
        assert im2_view.getYMax() == nrow
        assert im2_view.bounds == bounds
        assert im2_view.array.dtype.type == np_array_type

        assert im2_cview.getXMin() == 1
        assert im2_cview.getXMax() == ncol
        assert im2_cview.getYMin() == 1
        assert im2_cview.getYMax() == nrow
        assert im2_cview.bounds == bounds
        assert im2_cview.array.dtype.type == np_array_type

        assert im1.real.bounds == bounds
        assert im1.imag.bounds == bounds
        assert im2.real.bounds == bounds
        assert im2.imag.bounds == bounds
        assert im2_view.real.bounds == bounds
        assert im2_view.imag.bounds == bounds
        assert im2_cview.real.bounds == bounds
        assert im2_cview.imag.bounds == bounds
        if tchar[i] == 'C':
            assert im1.real.array.dtype.type == np.float64
            assert im1.imag.array.dtype.type == np.float64
        else:
            assert im1.real.array.dtype.type == np_array_type
            assert im1.imag.array.dtype.type == np_array_type

        # Check various ways to set and get values
        for y in range(1,nrow+1):
            for x in range(1,ncol+1):
                im1.setValue(x,y, 100 + 10*x + y)
                im1a.setValue(x+3,y+6, 100 + 10*x + y)
                im1b.setValue(x-1,y-1, 100 + 10*x + y)
                im2_view.setValue(x,y, 100 + 10*x + y)

        for y in range(1,nrow+1):
            for x in range(1,ncol+1):
                value = 100 + 10*x + y
                assert im1(x,y) == value
                assert im1(galsim.PositionI(x,y)) == value
                assert im1a(x+3,y+6) == value
                assert im1b(x-1,y-1) == value
                assert im1.view()(x,y) == value
                assert im1.view()(galsim.PositionI(x,y)) == value
                assert im1.view(make_const=True)(x,y) == value
                assert im2(x,y) == value
                assert im2_view(x,y) == value
                assert im2_cview(x,y) == value
                assert im1.conjugate()(x,y) == value
                if tchar[i] == 'C':
                    # complex conjugate is not a view into the original.
                    assert im2_conj(x,y) == 23
                    assert im2.conjugate()(x,y) == value
                else:
                    assert im2_conj(x,y) == value

                value2 = 53 + 12*x - 19*y
                im1[x,y] = value2
                im2_view[galsim.PositionI(x,y)] = value2
                assert im1.getValue(x,y) == value2
                assert im1.view().getValue(x,y) == value2
                assert im1.view(make_const=True).getValue(x,y) == value2
                assert im2.getValue(x,y) == value2
                assert im2_view.getValue(x,y) == value2
                assert im2_cview.getValue(x,y) == value2

                assert im1.real(x,y) == value2
                assert im1.view().real(x,y) == value2
                assert im1.view(make_const=True).real(x,y) == value2.real
                assert im2.real(x,y) == value2.real
                assert im2_view.real(x,y) == value2.real
                assert im2_cview.real(x,y) == value2.real
                assert im1.imag(x,y) == 0
                assert im1.view().imag(x,y) == 0
                assert im1.view(make_const=True).imag(x,y) == 0
                assert im2.imag(x,y) == 0
                assert im2_view.imag(x,y) == 0
                assert im2_cview.imag(x,y) == 0

                value3 = 10*x + y
                im1.addValue(x,y, value3-value2)
                im2_view[x,y] += value3-value2
                assert im1[galsim.PositionI(x,y)] == value3
                assert im1.view()[x,y] == value3
                assert im1.view(make_const=True)[galsim.PositionI(x,y)] == value3
                assert im2[x,y] == value3
                assert im2_view[galsim.PositionI(x,y)] == value3
                assert im2_cview[x,y] == value3

        try:
            # Setting or getting the value outside the bounds should throw an exception.
            np.testing.assert_raises(RuntimeError,im1.setValue,0,0,1)
            np.testing.assert_raises(RuntimeError,im1.__call__,0,0)
            np.testing.assert_raises(RuntimeError,im1.__getitem__,0,0)
            np.testing.assert_raises(RuntimeError,im1.__setitem__,0,0,1)
            np.testing.assert_raises(RuntimeError,im1.view().setValue,0,0,1)
            np.testing.assert_raises(RuntimeError,im1.view().__call__,0,0)
            np.testing.assert_raises(RuntimeError,im1.view().__getitem__,0,0)
            np.testing.assert_raises(RuntimeError,im1.view().__setitem__,0,0,1)

            np.testing.assert_raises(RuntimeError,im1.setValue,ncol+1,0,1)
            np.testing.assert_raises(RuntimeError,im1.__call__,ncol+1,0)
            np.testing.assert_raises(RuntimeError,im1.view().setValue,ncol+1,0,1)
            np.testing.assert_raises(RuntimeError,im1.view().__call__,ncol+1,0)

            np.testing.assert_raises(RuntimeError,im1.setValue,0,nrow+1,1)
            np.testing.assert_raises(RuntimeError,im1.__call__,0,nrow+1)
            np.testing.assert_raises(RuntimeError,im1.view().setValue,0,nrow+1,1)
            np.testing.assert_raises(RuntimeError,im1.view().__call__,0,nrow+1)

            np.testing.assert_raises(RuntimeError,im1.setValue,ncol+1,nrow+1,1)
            np.testing.assert_raises(RuntimeError,im1.__call__,ncol+1,nrow+1)
            np.testing.assert_raises(RuntimeError,im1.view().setValue,ncol+1,nrow+1,1)
            np.testing.assert_raises(RuntimeError,im1.view().__call__,ncol+1,nrow+1)

            # Also, setting values in something that should be const
            np.testing.assert_raises(ValueError,im1.view(make_const=True).setValue,1,1,1)
            np.testing.assert_raises(ValueError,im1.view(make_const=True).real.setValue,1,1,1)
            np.testing.assert_raises(ValueError,im1.view(make_const=True).imag.setValue,1,1,1)
            if tchar[i] != 'C':
                np.testing.assert_raises(ValueError,im1.imag.setValue,1,1,1)

            # Finally check for the wrong number of arguments in get/setitem
            np.testing.assert_raises(TypeError,im1.__getitem__,1)
            np.testing.assert_raises(TypeError,im1.__setitem__,1,1)
            np.testing.assert_raises(TypeError,im1.__getitem__,1,2,3)
            np.testing.assert_raises(TypeError,im1.__setitem__,1,2,3,4)

        except ImportError:
            print('The assert_raises tests require nose')

        # Check view of given data
        im3_view = galsim.Image(ref_array.astype(np_array_type))
        slice_array = large_array.astype(np_array_type)[::3,::2]
        im4_view = galsim.Image(slice_array)
        im5_view = galsim.Image(ref_array.astype(np_array_type).tolist(), dtype=array_type)
        im6_view = galsim.Image(ref_array.astype(np_array_type), xmin=4, ymin=7)
        im7_view = galsim.Image(ref_array.astype(np_array_type), xmin=0, ymin=0)
        for y in range(1,nrow+1):
            for x in range(1,ncol+1):
                value3 = 10*x+y
                assert im3_view(x,y) == value3
                assert im4_view(x,y) == value3
                assert im5_view(x,y) == value3
                assert im6_view(x+3,y+6) == value3
                assert im7_view(x-1,y-1) == value3

        # Check shift ops
        im1_view = im1.view() # View with old bounds
        dx = 31
        dy = 16
        im1.shift(dx,dy)
        im2_view.setOrigin( 1+dx , 1+dy )
        im3_view.setCenter( (ncol+1)/2+dx , (nrow+1)/2+dy )
        shifted_bounds = galsim.BoundsI(1+dx, ncol+dx, 1+dy, nrow+dy)

        assert im1.bounds == shifted_bounds
        assert im2_view.bounds == shifted_bounds
        assert im3_view.bounds == shifted_bounds
        # Others shouldn't have changed
        assert im1_view.bounds == bounds
        assert im2.bounds == bounds
        for y in range(1,nrow+1):
            for x in range(1,ncol+1):
                value3 = 10*x+y
                assert im1(x+dx,y+dy) == value3
                assert im1_view(x,y) == value3
                assert im2(x,y) == value3
                assert im2_view(x+dx,y+dy) == value3
                assert im3_view(x+dx,y+dy) == value3

        # Check picklability
        do_pickle(im1)
        do_pickle(im1_view)
        do_pickle(im2)
        do_pickle(im2_view)
        do_pickle(im3_view)
        do_pickle(im4_view)

    # Also check picklability of Bounds, Position here.
    do_pickle(galsim.PositionI(2,3))
    do_pickle(galsim.PositionD(2.2,3.3))
    do_pickle(galsim.BoundsI(2,3,7,8))
    do_pickle(galsim.BoundsD(2.1, 4.3, 6.5, 9.1))

@timer
def test_undefined_image():
    """Test an image with undefined bounds
    """
    for i in range(len(types)):
        im = galsim.Image(dtype=types[i])
        assert not im.bounds.isDefined()
        assert im.array.shape == (1,1)
        print('im = ',repr(im))
        print('b = ',repr(im.bounds))
        assert im == im
        try:
            np.testing.assert_raises(RuntimeError,im.setValue,0,0,1)
            np.testing.assert_raises(RuntimeError,im.__call__,0,0)
            np.testing.assert_raises(RuntimeError,im.view().setValue,0,0,1)
            np.testing.assert_raises(RuntimeError,im.view().__call__,0,0)
        except ImportError:
            pass
        do_pickle(im.bounds)
        do_pickle(im)
        do_pickle(im.view())
        do_pickle(im.view(make_const=True))

@timer
def test_Image_FITS_IO():
    """Test that all four FITS reference images are correctly read in by both PyFITS and our Image
    wrappers.
    """
    for i in range(ntypes):
        array_type = types[i]

        if tchar[i] == 'C':
            continue
            ref_image = galsim.Image(ref_array.astype(array_type))
            test_file = os.path.join(datadir, "test"+tchar[i]+".fits")
            ref_image.write(test_file)

        #
        # Test input from a single external FITS image
        #

        # Read the reference image to from an externally-generated fits file
        test_file = os.path.join(datadir, "test"+tchar[i]+".fits")
        # Check pyfits read for sanity
        with pyfits.open(test_file) as fits:
            test_array = fits[0].data
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_array,
                err_msg="PyFITS failing to read reference image.")

        # Then use galsim fits.read function
        # First version: use pyfits HDUList
        with pyfits.open(test_file) as hdu:
            test_image = galsim.fits.read(hdu_list=hdu)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Failed reading from PyFITS PrimaryHDU input.")

        # Second version: use file name
        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" read failed reading from filename input.")

        #
        # Test full I/O on a single internally-generated FITS image
        #

        # Write the reference image to a fits file
        ref_image = galsim.Image(ref_array.astype(array_type))
        test_file = os.path.join(datadir, "test"+tchar[i]+"_internal.fits")
        ref_image.write(test_file)

        # Check pyfits read for sanity
        with pyfits.open(test_file) as fits:
            test_array = fits[0].data
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_array,
                err_msg="Image"+tchar[i]+" write failed.")

        # Then use galsim fits.read function
        # First version: use pyfits HDUList
        with pyfits.open(test_file) as hdu:
            test_image = galsim.fits.read(hdu_list=hdu)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Failed reading from PyFITS PrimaryHDU input.")

        # Second version: use file name
        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" read failed reading from filename input.")

        #
        # Test various compression schemes
        #

        # These tests are a bit slow, so we only bother to run them for the first dtype
        # when doing the regular unit tests.  When running python test_image.py, all of them
        # will run, so when working on the code, it is a good idea to run the tests that way.
        if i > 0 and __name__ != "__main__":
            continue

        # Test full-file gzip
        test_file = os.path.join(datadir, "test"+tchar[i]+".fits.gz")
        test_image = galsim.fits.read(test_file, compression='gzip')
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" read failed for explicit full-file gzip")

        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" read failed for auto full-file gzip")

        test_file = os.path.join(datadir, "test"+tchar[i]+"_internal.fits.gz")
        ref_image.write(test_file, compression='gzip')
        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" write failed for explicit full-file gzip")

        ref_image.write(test_file)
        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" write failed for auto full-file gzip")

        # Test full-file bzip2
        test_file = os.path.join(datadir, "test"+tchar[i]+".fits.bz2")
        test_image = galsim.fits.read(test_file, compression='bzip2')
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" read failed for explicit full-file bzip2")

        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" read failed for auto full-file bzip2")

        test_file = os.path.join(datadir, "test"+tchar[i]+"_internal.fits.bz2")
        ref_image.write(test_file, compression='bzip2')
        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" write failed for explicit full-file bzip2")

        ref_image.write(test_file)
        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" write failed for auto full-file bzip2")

        # Test rice
        test_file = os.path.join(datadir, "test"+tchar[i]+".fits.fz")
        test_image = galsim.fits.read(test_file, compression='rice')
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" read failed for explicit rice")

        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" read failed for auto rice")

        test_file = os.path.join(datadir, "test"+tchar[i]+"_internal.fits.fz")
        ref_image.write(test_file, compression='rice')
        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" write failed for explicit rice")

        ref_image.write(test_file)
        test_image = galsim.fits.read(test_file)
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" write failed for auto rice")

        # Test gzip_tile
        test_file = os.path.join(datadir, "test"+tchar[i]+"_internal.fits.gzt")
        ref_image.write(test_file, compression='gzip_tile')
        test_image = galsim.fits.read(test_file, compression='gzip_tile')
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" write failed for gzip_tile")

        # Test hcompress
        test_file = os.path.join(datadir, "test"+tchar[i]+"_internal.fits.hc")
        ref_image.write(test_file, compression='hcompress')
        test_image = galsim.fits.read(test_file, compression='hcompress')
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                err_msg="Image"+tchar[i]+" write failed for hcompress")

        # Test plio (only valid on positive integer values)
        if tchar[i] in ['S', 'I']:
            test_file = os.path.join(datadir, "test"+tchar[i]+"_internal.fits.plio")
            ref_image.write(test_file, compression='plio')
            test_image = galsim.fits.read(test_file, compression='plio')
            np.testing.assert_array_equal(ref_array.astype(types[i]), test_image.array,
                    err_msg="Image"+tchar[i]+" write failed for plio")


@timer
def test_Image_MultiFITS_IO():
    """Test that all four FITS reference images are correctly read in by both PyFITS and our Image
    wrappers.
    """
    for i in range(ntypes):
        array_type = types[i]

        if tchar[i] == 'C':
            continue
            ref_image = galsim.Image(ref_array.astype(array_type))
            image_list = []
            for k in range(nimages):
                image_list.append(ref_image + k)
            test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+".fits")
            galsim.fits.writeMulti(image_list,test_multi_file)

        #
        # Test input from an external multi-extension fits file
        #

        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+".fits")
        # Check pyfits read for sanity
        with pyfits.open(test_multi_file) as fits:
            test_array = fits[0].data
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_array,
                err_msg="PyFITS failing to read multi file.")

        # Then use galsim fits.readMulti function
        # First version: use pyfits HDUList
        with pyfits.open(test_multi_file) as hdu:
            test_image_list = galsim.fits.readMulti(hdu_list=hdu)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Failed reading from PyFITS PrimaryHDU input.")

        # Second version: use file name
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed reading from filename input.")

        #
        # Test full I/O for an internally-generated multi-extension fits file
        #

        # Build a list of images with different values
        ref_image = galsim.Image(ref_array.astype(array_type))
        image_list = []
        for k in range(nimages):
            image_list.append(ref_image + k)

        # Write the list to a multi-extension fits file
        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+"_internal.fits")
        galsim.fits.writeMulti(image_list,test_multi_file)

        # Check pyfits read for sanity
        with pyfits.open(test_multi_file) as fits:
            test_array = fits[0].data
        np.testing.assert_array_equal(ref_array.astype(types[i]), test_array,
                err_msg="PyFITS failing to read multi file.")

        # Then use galsim fits.readMulti function
        # First version: use pyfits HDUList
        with pyfits.open(test_multi_file) as hdu:
            test_image_list = galsim.fits.readMulti(hdu_list=hdu)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Failed reading from PyFITS PrimaryHDU input.")

        # Second version: use file name
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed reading from filename input.")


        #
        # Test writing to hdu_list directly and then writing to file.
        #

        # Start with empty hdu_list
        hdu_list = pyfits.HDUList()

        # Add each image one at a time
        for k in range(nimages):
            image = ref_image + k
            galsim.fits.write(image, hdu_list=hdu_list)

        # Write it out with writeFile
        galsim.fits.writeFile(test_multi_file, hdu_list)

        # Check that reading it back in gives the same values
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed after using writeFile")

        #
        # Test various compression schemes
        #

        # These tests are a bit slow, so we only bother to run them for the first dtype
        # when doing the regular unit tests.  When running python test_image.py, all of them
        # will run, so when working on the code, it is a good idea to run the tests that way.
        if i > 0 and __name__ != "__main__":
            continue

        # Test full-file gzip
        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+".fits.gz")
        test_image_list = galsim.fits.readMulti(test_multi_file, compression='gzip')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed for explicit full-file gzip")

        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed for auto full-file gzip")

        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+"_internal.fits.gz")
        galsim.fits.writeMulti(image_list,test_multi_file, compression='gzip')
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeMulti failed for explicit full-file gzip")

        galsim.fits.writeMulti(image_list,test_multi_file)
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeMulti failed for auto full-file gzip")

        # Test full-file bzip2
        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+".fits.bz2")
        test_image_list = galsim.fits.readMulti(test_multi_file, compression='bzip2')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed for explicit full-file bzip2")

        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed for auto full-file bzip2")

        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+"_internal.fits.bz2")
        galsim.fits.writeMulti(image_list,test_multi_file, compression='bzip2')
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeMulti failed for explicit full-file bzip2")

        galsim.fits.writeMulti(image_list,test_multi_file)
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeMulti failed for auto full-file bzip2")

        # Test rice
        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+".fits.fz")
        test_image_list = galsim.fits.readMulti(test_multi_file, compression='rice')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed for explicit rice")

        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readMulti failed for auto rice")

        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+"_internal.fits.fz")
        galsim.fits.writeMulti(image_list,test_multi_file, compression='rice')
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeMulti failed for explicit rice")

        galsim.fits.writeMulti(image_list,test_multi_file)
        test_image_list = galsim.fits.readMulti(test_multi_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeMulti failed for auto rice")

        # Test gzip_tile
        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+"_internal.fits.gzt")
        galsim.fits.writeMulti(image_list,test_multi_file, compression='gzip_tile')
        test_image_list = galsim.fits.readMulti(test_multi_file, compression='gzip_tile')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeMulti failed for gzip_tile")

        # Test hcompress
        test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+"_internal.fits.hc")
        galsim.fits.writeMulti(image_list,test_multi_file, compression='hcompress')
        test_image_list = galsim.fits.readMulti(test_multi_file, compression='hcompress')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeMulti failed for hcompress")

        # Test plio (only valid on positive integer values)
        if tchar[i] in ['S', 'I']:
            test_multi_file = os.path.join(datadir, "test_multi"+tchar[i]+"_internal.fits.plio")
            galsim.fits.writeMulti(image_list,test_multi_file, compression='plio')
            test_image_list = galsim.fits.readMulti(test_multi_file, compression='plio')
            for k in range(nimages):
                np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                        test_image_list[k].array,
                        err_msg="Image"+tchar[i]+" writeMulti failed for plio")


@timer
def test_Image_CubeFITS_IO():
    """Test that all four FITS reference images are correctly read in by both PyFITS and our Image
    wrappers.
    """
    for i in range(ntypes):
        array_type = types[i]

        if tchar[i] == 'C':
            continue
            ref_image = galsim.Image(ref_array.astype(array_type))
            image_list = []
            for k in range(nimages):
                image_list.append(ref_image + k)
            test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+".fits")
            galsim.fits.writeCube(image_list,test_cube_file)

        #
        # Test input from an external fits data cube
        #
        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+".fits")
        # Check pyfits read for sanity
        with pyfits.open(test_cube_file) as fits:
            test_array = fits[0].data
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]), test_array[k,:,:],
                    err_msg="PyFITS failing to read cube file.")

        # Then use galsim fits.readCube function
        # First version: use pyfits HDUList
        with pyfits.open(test_cube_file) as hdu:
            test_image_list = galsim.fits.readCube(hdu_list=hdu)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Failed reading from PyFITS PrimaryHDU input.")

        # Second version: use file name
        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readCube failed reading from filename input.")

        #
        # Test full I/O for an internally-generated fits data cube
        #

        # Build a list of images with different values
        ref_image = galsim.Image(ref_array.astype(array_type))
        image_list = []
        for k in range(nimages):
            image_list.append(ref_image + k)

        # Write the list to a fits data cube
        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+"_internal.fits")
        galsim.fits.writeCube(image_list,test_cube_file)

        # Check pyfits read for sanity
        with pyfits.open(test_cube_file) as fits:
            test_array = fits[0].data
        assert test_array.dtype.type == types[i], "%s != %s" % (test_array.dtype.type, types[i])
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]), test_array[k,:,:],
                    err_msg="PyFITS failing to read cube file.")

        # Then use galsim fits.readCube function
        # First version: use pyfits HDUList
        with pyfits.open(test_cube_file) as hdu:
            test_image_list = galsim.fits.readCube(hdu_list=hdu)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Failed reading from PyFITS PrimaryHDU input.")

        # Second version: use file name
        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readCube failed reading from filename input.")

        #
        # Test various compression schemes
        #

        # These tests are a bit slow, so we only bother to run them for the first dtype
        # when doing the regular unit tests.  When running python test_image.py, all of them
        # will run, so when working on the code, it is a good idea to run the tests that way.
        if i > 0 and __name__ != "__main__":
            continue

        # Test full-file gzip
        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+".fits.gz")
        test_image_list = galsim.fits.readCube(test_cube_file, compression='gzip')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readCube failed for explicit full-file gzip")

        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readCube failed for auto full-file gzip")

        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+"_internal.fits.gz")
        galsim.fits.writeCube(image_list,test_cube_file, compression='gzip')
        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeCube failed for explicit full-file gzip")

        galsim.fits.writeCube(image_list,test_cube_file)
        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeCube failed for auto full-file gzip")

        # Test full-file bzip2
        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+".fits.bz2")
        test_image_list = galsim.fits.readCube(test_cube_file, compression='bzip2')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readCube failed for explicit full-file bzip2")

        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readCube failed for auto full-file bzip2")

        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+"_internal.fits.bz2")
        galsim.fits.writeCube(image_list,test_cube_file, compression='bzip2')
        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeCube failed for explicit full-file bzip2")

        galsim.fits.writeCube(image_list,test_cube_file)
        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeCube failed for auto full-file bzip2")

        # Test rice
        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+".fits.fz")
        test_image_list = galsim.fits.readCube(test_cube_file, compression='rice')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readCube failed for explicit rice")

        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" readCube failed for auto rice")

        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+"_internal.fits.fz")
        galsim.fits.writeCube(image_list,test_cube_file, compression='rice')
        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeCube failed for explicit rice")

        galsim.fits.writeCube(image_list,test_cube_file)
        test_image_list = galsim.fits.readCube(test_cube_file)
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeCube failed for auto rice")

        # Test gzip_tile
        test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+"_internal.fits.gzt")
        galsim.fits.writeCube(image_list,test_cube_file, compression='gzip_tile')
        test_image_list = galsim.fits.readCube(test_cube_file, compression='gzip_tile')
        for k in range(nimages):
            np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                    test_image_list[k].array,
                    err_msg="Image"+tchar[i]+" writeCube failed for gzip_tile")

        # Note: hcompress is invalid for data cubes

        # Test plio (only valid on positive integer values)
        if tchar[i] in ['S', 'I']:
            test_cube_file = os.path.join(datadir, "test_cube"+tchar[i]+"_internal.fits.plio")
            galsim.fits.writeCube(image_list,test_cube_file, compression='plio')
            test_image_list = galsim.fits.readCube(test_cube_file, compression='plio')
            for k in range(nimages):
                np.testing.assert_array_equal((ref_array+k).astype(types[i]),
                        test_image_list[k].array,
                        err_msg="Image"+tchar[i]+" writeCube failed for plio")


@timer
def test_Image_array_view():
    """Test that all four types of supported Images correctly provide a view on an input array.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image = galsim.Image(ref_array.astype(types[i]))
        np.testing.assert_array_equal(ref_array.astype(types[i]), image.array,
                err_msg="Array look into Image class does not match input for dtype = "+
                str(types[i]))
        #Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        image = image_init_func(ref_array.astype(types[i]))
        np.testing.assert_array_equal(ref_array.astype(types[i]), image.array,
                err_msg="Array look into Image class does not match input for dtype = "+
                str(types[i]))


@timer
def test_Image_binary_add():
    """Test that all four types of supported Images add correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = galsim.Image((2 * ref_array).astype(types[i]))
        image3 = image1 + image2
        np.testing.assert_array_equal((3 * ref_array).astype(types[i]), image3.array,
                err_msg="Binary add in Image class does not match reference for dtype = "+
                str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((2 * ref_array).astype(types[i]))
        image3 = image1 + image2
        np.testing.assert_array_equal((3 * ref_array).astype(types[i]), image3.array,
                err_msg="Binary add in Image class does not match reference for dtype = "
                +str(types[i]))

        for j in range(ntypes):
            image2_init_func = eval("galsim.Image"+tchar[j])
            image2 = image2_init_func((2 * ref_array).astype(types[j]))
            image3 = image1 + image2
            type3 = image3.array.dtype.type
            np.testing.assert_array_equal((3 * ref_array).astype(type3), image3.array,
                    err_msg="Inplace add in Image class does not match reference for dtypes = "
                    +str(types[i])+" and "+str(types[j]))

        # Check for exceptions if we try to do this operation for images without matching
        # shape.  Note that this test is only included here (not in the unit tests for all
        # other operations) because all operations have the same error-checking code, so it should
        # only be necessary to check once.
        try:
            image1 = galsim.Image(ref_array.astype(types[i]))
            image2 = image1.subImage(galsim.BoundsI(image1.xmin, image1.xmax-1,
                                                    image1.ymin+1, image1.ymax))
            np.testing.assert_raises(ValueError, image1.__add__, image2)
        except ImportError:
            # assert_raises requires nose, which we don't want to force people to install.
            # So if they are running this without nose, we just skip these tests.
            pass


@timer
def test_Image_binary_subtract():
    """Test that all four types of supported Images subtract correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = galsim.Image((2 * ref_array).astype(types[i]))
        image3 = image2 - image1
        np.testing.assert_array_equal(ref_array.astype(types[i]), image3.array,
                err_msg="Binary subtract in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((2 * ref_array).astype(types[i]))
        image3 = image2 - image1
        np.testing.assert_array_equal(ref_array.astype(types[i]), image3.array,
                err_msg="Binary subtract in Image class does not match reference for dtype = "
                +str(types[i]))
        for j in range(ntypes):
            image2_init_func = eval("galsim.Image"+tchar[j])
            image2 = image2_init_func((2 * ref_array).astype(types[j]))
            image3 = image2 - image1
            type3 = image3.array.dtype.type
            np.testing.assert_array_equal(ref_array.astype(type3), image3.array,
                    err_msg="Inplace add in Image class does not match reference for dtypes = "
                    +str(types[i])+" and "+str(types[j]))


@timer
def test_Image_binary_multiply():
    """Test that all four types of supported Images multiply correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = galsim.Image((2 * ref_array).astype(types[i]))
        image3 = image1 * image2
        np.testing.assert_array_equal((2 * ref_array**2).astype(types[i]), image3.array,
                err_msg="Binary multiply in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((2 * ref_array).astype(types[i]))
        image3 = image1 * image2
        np.testing.assert_array_equal((2 * ref_array**2).astype(types[i]), image3.array,
                err_msg="Binary multiply in Image class does not match reference for dtype = "
                +str(types[i]))
        for j in range(ntypes):
            image2_init_func = eval("galsim.Image"+tchar[j])
            image2 = image2_init_func((2 * ref_array).astype(types[j]))
            image3 = image2 * image1
            type3 = image3.array.dtype.type
            np.testing.assert_array_equal((2*ref_array**2).astype(type3), image3.array,
                    err_msg="Inplace add in Image class does not match reference for dtypes = "
                    +str(types[i])+" and "+str(types[j]))


@timer
def test_Image_binary_divide():
    """Test that all four types of supported Images divide correctly.
    """
    # Note: tests here are not precisely equal, since division can have rounding errors for
    # some elements.  In particular when dividing by complex, where there is a bit more to the
    # generic calculation (even though the imaginary parts are zero here).
    # So check that they are *almost* equal to 12 digits of precision.
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        # Note that I am using refarray + 1 to avoid divide-by-zero.
        image1 = galsim.Image((ref_array + 1).astype(types[i]))
        image2 = galsim.Image((3 * (ref_array + 1)**2).astype(types[i]))
        image3 = image2 / image1
        np.testing.assert_almost_equal((3 * (ref_array + 1)).astype(types[i]), image3.array,
                decimal=12,
                err_msg="Binary divide in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = (large_array+1).astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((3 * (ref_array + 1)**2).astype(types[i]))
        image3 = image2 / image1
        np.testing.assert_almost_equal((3 * (ref_array + 1)).astype(types[i]), image3.array,
                decimal=12,
                err_msg="Binary divide in Image class does not match reference for dtype = "
                +str(types[i]))
        for j in range(ntypes):
            image2_init_func = eval("galsim.Image"+tchar[j])
            image2 = image2_init_func((3 * (ref_array+1)**2).astype(types[j]))
            image3 = image2 / image1
            type3 = image3.array.dtype.type
            np.testing.assert_almost_equal((3*(ref_array+1)).astype(type3), image3.array,
                    decimal=12,
                    err_msg="Inplace divide in Image class does not match reference for dtypes = "
                    +str(types[i])+" and "+str(types[j]))


@timer
def test_Image_binary_scalar_add():
    """Test that all four types of supported Images add scalars correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = image1 + 3
        np.testing.assert_array_equal((ref_array + 3).astype(types[i]), image2.array,
                err_msg="Binary add scalar in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        image2 = 3 + image1
        np.testing.assert_array_equal((ref_array + 3).astype(types[i]), image2.array,
                err_msg="Binary radd scalar in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image1 + 3
        np.testing.assert_array_equal((ref_array + 3).astype(types[i]), image2.array,
                err_msg="Binary add scalar in Image class does not match reference for dtype = "
                +str(types[i]))
        image2 = 3 + image1
        np.testing.assert_array_equal((ref_array + 3).astype(types[i]), image2.array,
                err_msg="Binary radd scalar in Image class does not match reference for dtype = "
                +str(types[i]))


@timer
def test_Image_binary_scalar_subtract():
    """Test that all four types of supported Images binary scalar subtract correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = image1 - 3
        np.testing.assert_array_equal((ref_array - 3).astype(types[i]), image2.array,
                err_msg="Binary add scalar in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        image2 = 3 - image1
        np.testing.assert_array_equal((3 - ref_array).astype(types[i]), image2.array,
                err_msg="Binary add scalar in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image1 - 3
        np.testing.assert_array_equal((ref_array - 3).astype(types[i]), image2.array,
                err_msg="Binary add scalar in Image class does not match reference for dtype = "
                +str(types[i]))
        image2 = 3 - image1
        np.testing.assert_array_equal((3 - ref_array).astype(types[i]), image2.array,
                err_msg="Binary add scalar in Image class does not match reference for dtype = "
                +str(types[i]))


@timer
def test_Image_binary_scalar_multiply():
    """Test that all four types of supported Images binary scalar multiply correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = image1 * 3
        np.testing.assert_array_equal((ref_array * 3).astype(types[i]), image2.array,
                err_msg="Binary multiply scalar in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        image2 = 3 * image1
        np.testing.assert_array_equal((ref_array * 3).astype(types[i]), image2.array,
                err_msg="Binary rmultiply scalar in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image1 * 3
        np.testing.assert_array_equal((ref_array * 3).astype(types[i]), image2.array,
                err_msg="Binary multiply scalar in Image class does"
                +" not match reference for dtype = "+str(types[i]))
        image2 = 3 * image1
        np.testing.assert_array_equal((ref_array * 3).astype(types[i]), image2.array,
                err_msg="Binary rmultiply scalar in Image class does"
                +" not match reference for dtype = "+str(types[i]))


@timer
def test_Image_binary_scalar_divide():
    """Test that all four types of supported Images binary scalar divide correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image((3 * ref_array).astype(types[i]))
        image2 = image1 / 3
        np.testing.assert_array_equal(ref_array.astype(types[i]), image2.array,
                err_msg="Binary divide scalar in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = (3*large_array).astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image1 / 3
        np.testing.assert_array_equal(ref_array.astype(types[i]), image2.array,
                err_msg="Binary divide scalar in Image class does"
                +" not match reference for dtype = "+str(types[i]))


@timer
def test_Image_binary_scalar_pow():
    """Test that all four types of supported Images can be raised to a power (scalar) correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = galsim.Image((ref_array**2).astype(types[i]))
        image3 = image1**2
        # Note: unlike for the tests above with multiplication, the test fails if I use
        # assert_array_equal.  I have to use assert_array_almost_equal to avoid failure due to
        # small numerical issues.
        np.testing.assert_array_almost_equal(image3.array, image2.array,
            decimal=4,
            err_msg="Binary pow scalar in Image class (dictionary call) does"
            +" not match reference for dtype = "+str(types[i]))

        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func(ref_array.astype(types[i]))
        image2 **= 2
        image3 = image1**2
        np.testing.assert_array_equal(image3.array, image2.array,
            err_msg="Binary pow scalar in Image class does"
            +" not match reference for dtype = "+str(types[i]))

        # float types can also be taken to a float power
        if types[i] in [np.float32, np.float64]:
            image2 = image_init_func((ref_array**(1/1.3)).astype(types[i]))
            image3 = image2**1.3
            # Note: unlike for the tests above with multiplication/division, the test fails if I use
            # assert_array_equal.  I have to use assert_array_almost_equal to avoid failure due to
            # small numerical issues.
            np.testing.assert_array_almost_equal(ref_array.astype(types[i]), image3.array,
                decimal=4,
                err_msg="Binary pow scalar in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))


@timer
def test_Image_inplace_add():
    """Test that all four types of supported Images inplace add correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = galsim.Image((2 * ref_array).astype(types[i]))
        image1 += image2
        np.testing.assert_array_equal((3 * ref_array).astype(types[i]), image1.array,
                err_msg="Inplace add in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.copy().astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((2 * ref_array).astype(types[i]))
        image1 += image2
        np.testing.assert_array_equal((3 * ref_array).astype(types[i]), image1.array,
                err_msg="Inplace add in Image class does not match reference for dtype = "
                +str(types[i]))
        for j in range(i): # Only add simpler types to this one.
            image2_init_func = eval("galsim.Image"+tchar[j])
            slice_array = large_array.copy().astype(types[i])[::3,::2]
            image1 = image_init_func(slice_array)
            image2 = image2_init_func((2 * ref_array).astype(types[j]))
            image1 += image2
            np.testing.assert_array_equal((3 * ref_array).astype(types[i]), image1.array,
                    err_msg="Inplace add in Image class does not match reference for dtypes = "
                    +str(types[i])+" and "+str(types[j]))


@timer
def test_Image_inplace_subtract():
    """Test that all four types of supported Images inplace subtract correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image((2 * ref_array).astype(types[i]))
        image2 = galsim.Image(ref_array.astype(types[i]))
        image1 -= image2
        np.testing.assert_array_equal(ref_array.astype(types[i]), image1.array,
                err_msg="Inplace subtract in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = (2*large_array).astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func(ref_array.astype(types[i]))
        image1 -= image2
        np.testing.assert_array_equal(ref_array.astype(types[i]), image1.array,
                err_msg="Inplace subtract in Image class does"
                +" not match reference for dtype = "+str(types[i]))
        for j in range(i): # Only subtract simpler types from this one.
            image2_init_func = eval("galsim.Image"+tchar[j])
            slice_array = (2*large_array).astype(types[i])[::3,::2]
            image1 = image_init_func(slice_array)
            image2 = image2_init_func(ref_array.astype(types[j]))
            image1 -= image2
            np.testing.assert_array_equal(ref_array.astype(types[i]), image1.array,
                    err_msg="Inplace subtract in Image class does not match reference for dtypes = "
                    +str(types[i])+" and "+str(types[j]))


@timer
def test_Image_inplace_multiply():
    """Test that all four types of supported Images inplace multiply correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = galsim.Image((2 * ref_array).astype(types[i]))
        image1 *= image2
        np.testing.assert_array_equal((2 * ref_array**2).astype(types[i]), image1.array,
                err_msg="Inplace multiply in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.copy().astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((2 * ref_array).astype(types[i]))
        image1 *= image2
        np.testing.assert_array_equal((2 * ref_array**2).astype(types[i]), image1.array,
                err_msg="Inplace multiply in Image class does not match reference for dtype = "
                +str(types[i]))
        for j in range(i): # Only multiply simpler types to this one.
            image2_init_func = eval("galsim.Image"+tchar[j])
            slice_array = large_array.copy().astype(types[i])[::3,::2]
            image1 = image_init_func(slice_array)
            image2 = image2_init_func((2 * ref_array).astype(types[j]))
            image1 *= image2
            np.testing.assert_array_equal((2 * ref_array**2).astype(types[i]), image1.array,
                    err_msg="Inplace multiply in Image class does not match reference for dtypes = "
                    +str(types[i])+" and "+str(types[j]))


@timer
def test_Image_inplace_divide():
    """Test that all four types of supported Images inplace divide correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image((2 * (ref_array + 1)**2).astype(types[i]))
        image2 = galsim.Image((ref_array + 1).astype(types[i]))
        image1 /= image2
        np.testing.assert_array_equal((2 * (ref_array + 1)).astype(types[i]), image1.array,
                err_msg="Inplace divide in Image class (dictionary call) does"
                +" not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = (2*(large_array+1)**2).astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((ref_array + 1).astype(types[i]))
        image1 /= image2
        np.testing.assert_array_equal((2 * (ref_array + 1)).astype(types[i]), image1.array,
                err_msg="Inplace divide in Image class does not match reference for dtype = "
                +str(types[i]))
        for j in range(i): # Only divide simpler types into this one.
            image2_init_func = eval("galsim.Image"+tchar[j])
            slice_array = (2*(large_array+1)**2).astype(types[i])[::3,::2]
            image1 = image_init_func(slice_array)
            image2 = image2_init_func((ref_array+1).astype(types[j]))
            image1 /= image2
            np.testing.assert_array_equal((2 * (ref_array+1)).astype(types[i]), image1.array,
                    err_msg="Inplace divide in Image class does not match reference for dtypes = "
                    +str(types[i])+" and "+str(types[j]))


@timer
def test_Image_inplace_scalar_add():
    """Test that all four types of supported Images inplace scalar add correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image1 += 1
        np.testing.assert_array_equal((ref_array + 1).astype(types[i]), image1.array,
                err_msg="Inplace scalar add in Image class (dictionary "
                +"call) does not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.copy().astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image1 += 1
        np.testing.assert_array_equal((ref_array + 1).astype(types[i]), image1.array,
                err_msg="Inplace scalar add in Image class does not match reference for dtype = "
                +str(types[i]))


@timer
def test_Image_inplace_scalar_subtract():
    """Test that all four types of supported Images inplace scalar subtract correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image1 -= 1
        np.testing.assert_array_equal((ref_array - 1).astype(types[i]), image1.array,
                err_msg="Inplace scalar subtract in Image class (dictionary "
                +"call) does not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.copy().astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image1 -= 1
        np.testing.assert_array_equal((ref_array - 1).astype(types[i]), image1.array,
                err_msg="Inplace scalar subtract in Image class does"
                +" not match reference for dtype = "+str(types[i]))


@timer
def test_Image_inplace_scalar_multiply():
    """Test that all four types of supported Images inplace scalar multiply correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = galsim.Image((2 * ref_array).astype(types[i]))
        image1 *= 2
        np.testing.assert_array_equal(image1.array, image2.array,
                err_msg="Inplace scalar multiply in Image class (dictionary "
                +"call) does not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.copy().astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((2 * ref_array).astype(types[i]))
        image1 *= 2
        np.testing.assert_array_equal(image1.array, image2.array,
                err_msg="Inplace scalar multiply in Image class does"
                +" not match reference for dtype = "+str(types[i]))


@timer
def test_Image_inplace_scalar_divide():
    """Test that all four types of supported Images inplace scalar divide correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image(ref_array.astype(types[i]))
        image2 = galsim.Image((2 * ref_array).astype(types[i]))
        image2 /= 2
        np.testing.assert_array_equal(image1.array, image2.array,
                err_msg="Inplace scalar divide in Image class (dictionary "
                +"call) does not match reference for dtype = "+str(types[i]))
        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = (2*large_array).astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image1 /= 2
        np.testing.assert_array_equal(ref_array.astype(types[i]), image1.array,
                err_msg="Inplace scalar divide in Image class does"
                +" not match reference for dtype = "+str(types[i]))


@timer
def test_Image_inplace_scalar_pow():
    """Test that all four types of supported Images can be raised (in-place) to a scalar correctly.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image1 = galsim.Image((ref_array**2).astype(types[i]))
        image2 = galsim.Image(ref_array.astype(types[i]))
        image2 **= 2
        np.testing.assert_array_almost_equal(image1.array, image2.array, decimal=4,
            err_msg="Inplace scalar pow in Image class (dictionary "
            +"call) does not match reference for dtype = "+str(types[i]))

        # Then try using the eval command to mimic use via ImageD, ImageF etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        slice_array = large_array.copy().astype(types[i])[::3,::2]
        image1 = image_init_func(slice_array)
        image2 = image_init_func((ref_array.astype(types[i]))**2)
        image1 **= 2
        np.testing.assert_array_equal(image1.array, image2.array,
            err_msg="Inplace scalar pow in Image class does"
            +" not match reference for dtype = "+str(types[i]))

        # float types can also be taken to a float power
        if types[i] in [np.float32, np.float64]:
            # First try using the dictionary-type Image init
            image1 = galsim.Image(ref_array.astype(types[i]))
            image2 = galsim.Image((ref_array**(1./1.3)).astype(types[i]))
            image2 **= 1.3
            np.testing.assert_array_almost_equal(image1.array, image2.array, decimal=4,
                err_msg="Inplace scalar pow in Image class (dictionary "
                +"call) does not match reference for dtype = "+str(types[i]))


@timer
def test_Image_subImage():
    """Test that subImages are accessed and written correctly.
    """
    for i in range(ntypes):
        image = galsim.Image(ref_array.astype(types[i]))
        bounds = galsim.BoundsI(3,4,2,3)
        sub_array = np.array([[32, 42], [33, 43]]).astype(types[i])
        np.testing.assert_array_equal(image.subImage(bounds).array, sub_array,
            err_msg="image.subImage(bounds) does not match reference for dtype = "+str(types[i]))
        np.testing.assert_array_equal(image[bounds].array, sub_array,
            err_msg="image[bounds] does not match reference for dtype = "+str(types[i]))
        image[bounds] = galsim.Image(sub_array+100)
        np.testing.assert_array_equal(image[bounds].array, (sub_array+100),
            err_msg="image[bounds] = im2 does not set correctly for dtype = "+str(types[i]))
        for xpos in range(1,test_shape[0]+1):
            for ypos in range(1,test_shape[1]+1):
                if (xpos >= bounds.getXMin() and xpos <= bounds.getXMax() and
                    ypos >= bounds.getYMin() and ypos <= bounds.getYMax()):
                    value = ref_array[ypos-1,xpos-1] + 100
                else:
                    value = ref_array[ypos-1,xpos-1]
                assert image(xpos,ypos) == value,  \
                    "image[bounds] = im2 set wrong locations for dtype = "+str(types[i])

        image = galsim.Image(ref_array.astype(types[i]))
        image[bounds] += 100
        np.testing.assert_array_equal(image[bounds].array, (sub_array+100),
            err_msg="image[bounds] += 100 does not set correctly for dtype = "+str(types[i]))
        image[bounds] = galsim.Image(sub_array)
        np.testing.assert_array_equal(image.array, ref_array,
            err_msg="image[bounds] += 100 set wrong locations for dtype = "+str(types[i]))

        image = galsim.Image(ref_array.astype(types[i]))
        image[bounds] -= 100
        np.testing.assert_array_equal(image[bounds].array, (sub_array-100),
            err_msg="image[bounds] -= 100 does not set correctly for dtype = "+str(types[i]))
        image[bounds] = galsim.Image(sub_array)
        np.testing.assert_array_equal(image.array, ref_array,
            err_msg="image[bounds] -= 100 set wrong locations for dtype = "+str(types[i]))

        image = galsim.Image(ref_array.astype(types[i]))
        image[bounds] *= 100
        np.testing.assert_array_equal(image[bounds].array, (sub_array*100),
            err_msg="image[bounds] *= 100 does not set correctly for dtype = "+str(types[i]))
        image[bounds] = galsim.Image(sub_array)
        np.testing.assert_array_equal(image.array, ref_array,
            err_msg="image[bounds] *= 100 set wrong locations for dtype = "+str(types[i]))

        image = galsim.Image((100*ref_array).astype(types[i]))
        image[bounds] /= 100
        np.testing.assert_array_equal(image[bounds].array, (sub_array),
            err_msg="image[bounds] /= 100 does not set correctly for dtype = "+str(types[i]))
        image[bounds] = galsim.Image((100*sub_array).astype(types[i]))
        np.testing.assert_array_equal(image.array, (100*ref_array),
            err_msg="image[bounds] /= 100 set wrong locations for dtype = "+str(types[i]))

        im2 = galsim.Image(sub_array)
        image = galsim.Image(ref_array.astype(types[i]))
        image[bounds] += im2
        np.testing.assert_array_equal(image[bounds].array, (2*sub_array),
            err_msg="image[bounds] += im2 does not set correctly for dtype = "+str(types[i]))
        image[bounds] = galsim.Image(sub_array)
        np.testing.assert_array_equal(image.array, ref_array,
            err_msg="image[bounds] += im2 set wrong locations for dtype = "+str(types[i]))

        image = galsim.Image(2*ref_array.astype(types[i]))
        image[bounds] -= im2
        np.testing.assert_array_equal(image[bounds].array, sub_array,
            err_msg="image[bounds] -= im2 does not set correctly for dtype = "+str(types[i]))
        image[bounds] = galsim.Image((2*sub_array).astype(types[i]))
        np.testing.assert_array_equal(image.array, (2*ref_array),
            err_msg="image[bounds] -= im2 set wrong locations for dtype = "+str(types[i]))

        image = galsim.Image(ref_array.astype(types[i]))
        image[bounds] *= im2
        np.testing.assert_array_equal(image[bounds].array, (sub_array**2),
            err_msg="image[bounds] *= im2 does not set correctly for dtype = "+str(types[i]))
        image[bounds] = galsim.Image(sub_array)
        np.testing.assert_array_equal(image.array, ref_array,
            err_msg="image[bounds] *= im2 set wrong locations for dtype = "+str(types[i]))

        image = galsim.Image((2 * ref_array**2).astype(types[i]))
        image[bounds] /= im2
        np.testing.assert_array_equal(image[bounds].array, (2*sub_array),
            err_msg="image[bounds] /= im2 does not set correctly for dtype = "+str(types[i]))
        image[bounds] = galsim.Image((2*sub_array**2).astype(types[i]))
        np.testing.assert_array_equal(image.array, (2*ref_array**2),
            err_msg="image[bounds] /= im2 set wrong locations for dtype = "+str(types[i]))

        do_pickle(image)


@timer
def test_Image_resize():
    """Test that the Image resize function works correctly.
    """
    # Use a random number generator for some values here.
    ud = galsim.UniformDeviate(515324)

    for i in range(ntypes):

        # Resize to a bunch of different shapes (larger and smaller) to test reallocations
        for shape in [ (10,10), (3,20), (21,8), (1,3), (13,30) ]:

            # im1 starts with basic constructor with a given size
            array_type = types[i]
            im1 = galsim.Image(5,5, dtype=array_type)

            # im2 stars with null constructor
            im2 = galsim.Image(dtype=array_type)

            # im3 is a view into a larger image
            im3_full = galsim.Image(10,10, dtype=array_type, init_value=23)
            im3 = im3_full.subImage(galsim.BoundsI(1,6,1,6))

            # Make sure at least one of the _arrays is instantiated.  This isn't required,
            # but we used to have bugs if the array was instantiated before resizing.
            # So test im1 and im3 being instantiated and im2 not instantiated.
            np.testing.assert_array_equal(im1.array, 0, "im1 is not initially all 0.")
            np.testing.assert_array_equal(im3.array, 23, "im3 is not initially all 23.")

            # Have the xmin, ymin value be random numbers from -100..100:
            xmin = int(ud() * 200) - 100
            ymin = int(ud() * 200) - 100
            xmax = xmin + shape[1] - 1
            ymax = ymin + shape[0] - 1
            b = galsim.BoundsI(xmin, xmax, ymin, ymax)
            im1.resize(b)
            im2.resize(b)
            im3.resize(b)

            np.testing.assert_equal(
                b, im1.bounds, err_msg="im1 has wrong bounds after resize to b = %s"%b)
            np.testing.assert_equal(
                b, im2.bounds, err_msg="im2 has wrong bounds after resize to b = %s"%b)
            np.testing.assert_equal(
                b, im3.bounds, err_msg="im3 has wrong bounds after resize to b = %s"%b)
            np.testing.assert_array_equal(
                im1.array.shape, shape, err_msg="im1.array.shape wrong after resize")
            np.testing.assert_array_equal(
                im2.array.shape, shape, err_msg="im2.array.shape wrong after resize")
            np.testing.assert_array_equal(
                im3.array.shape, shape, err_msg="im3.array.shape wrong after resize")

            # Fill the images with random numbers
            for x in range(xmin,xmax+1):
                for y in range(ymin,ymax+1):
                    val = simple_types[i](ud()*500)
                    im1.setValue(x,y,val)
                    im2.setValue(x,y,val)
                    im3.setValue(x,y,val)

            # They should be equal now.  This doesn't completely guarantee that nothing is
            # wrong, but hopefully if we are misallocating memory here, something will be
            # clobbered or we will get a seg fault.
            np.testing.assert_array_equal(
                im1.array, im2.array, err_msg="im1 != im2 after resize to b = %s"%b)
            np.testing.assert_array_equal(
                im1.array, im3.array, err_msg="im1 != im3 after resize to b = %s"%b)
            np.testing.assert_array_equal(
                im2.array, im3.array, err_msg="im2 != im3 after resize to b = %s"%b)

            # Also, since the view was resized, it should no longer be coupled to the original.
            np.testing.assert_array_equal(
                im3_full.array, 23, err_msg="im3_full changed")

            do_pickle(im1)
            do_pickle(im2)
            do_pickle(im3)


@timer
def test_ConstImage_array_constness():
    """Test that Image instances with make_const=True cannot be modified via their .array
    attributes, and that if this is attempted a RuntimeError is raised.
    """
    for i in range(ntypes):
        # First try using the dictionary-type Image init
        image = galsim.Image(ref_array.astype(types[i]), make_const=True)
        try:
            image.array[1, 2] = 666
        # Apparently older numpy versions might raise a RuntimeError, a ValueError, or a TypeError
        # when trying to write to arrays that have writeable=False.
        # From the numpy 1.7.0 release notes:
        #     Attempting to write to a read-only array (one with
        #     ``arr.flags.writeable`` set to ``False``) used to raise either a
        #     RuntimeError, ValueError, or TypeError inconsistently, depending on
        #     which code path was taken. It now consistently raises a ValueError.
        except (RuntimeError, ValueError, TypeError):
            pass
        except:
            assert False, "Unexpected error: "+str(sys.exc_info()[0])

        # Then try using the eval command to mimic use via ImageD, etc.
        image_init_func = eval("galsim.Image"+tchar[i])
        image = image_init_func(ref_array.astype(types[i]), make_const=True)
        try:
            image.array[1, 2] = 666
        except (RuntimeError, ValueError, TypeError):
            pass
        except:
            assert False, "Unexpected error: "+str(sys.exc_info()[0])

        do_pickle(image)


@timer
def test_BoundsI_init_with_non_pure_ints():
    """Test that BoundsI converts its input args to int variables on input.
    """
    ref_bound_vals = (5, 35, 1, 48)
    xmin_test, xmax_test, ymin_test, ymax_test = ref_bound_vals
    ref_bounds = galsim.BoundsI(xmin_test, xmax_test, ymin_test, ymax_test)
    bound_arr_int = np.asarray(ref_bound_vals, dtype=int)
    bound_arr_flt = np.asarray(ref_bound_vals, dtype=float)
    bound_arr_flt_nonint = bound_arr_flt + 0.3

    # Check kwarg initialization:
    assert ref_bounds == galsim.BoundsI(
        xmin=bound_arr_int[0], xmax=bound_arr_int[1],
        ymin=bound_arr_int[2], ymax=bound_arr_int[3]), \
        "Cannot initialize a BoundI with int array elements"
    assert ref_bounds == galsim.BoundsI(
        xmin=bound_arr_flt[0], xmax=bound_arr_flt[1],
        ymin=bound_arr_flt[2], ymax=bound_arr_flt[3]), \
        "Cannot initialize a BoundI with float array elements"

    # Check arg initialization:
    assert ref_bounds == galsim.BoundsI(*bound_arr_int), \
        "Cannot initialize a BoundI with int array elements"
    assert ref_bounds == galsim.BoundsI(*bound_arr_flt), \
        "Cannot initialize a BoundI with float array elements"

    # Using non-integers should raise a ValueError
    try:
        np.testing.assert_raises(ValueError,galsim.BoundsI,*bound_arr_flt_nonint)
        np.testing.assert_raises(ValueError,galsim.BoundsI,
                                 xmin=bound_arr_flt_nonint[0], xmax=bound_arr_flt_nonint[1],
                                 ymin=bound_arr_flt_nonint[2], ymax=bound_arr_flt_nonint[3])
    except ImportError:
        print('The assert_raises tests require nose')


@timer
def test_Image_constructor():
    """Check that the Image constructor that takes NumPy array does not mangle input.
    """
    from sys import byteorder
    native_byteorder = {'big': '>', 'little': '<'}[byteorder]

    # Loop over types.
    for i in range(ntypes):

        array_dtype = np.dtype(types[i])

        # Make a NumPy array directly, with non-trivially interesting values.
        test_arr = np.ones((3,4), dtype=types[i])
        test_arr[1,3] = -5
        test_arr[2,2] = 7
        # Initialize the Image from it.
        test_im = galsim.Image(test_arr)
        # Check that the image.array attribute matches the original.
        np.testing.assert_array_equal(
            test_arr, test_im.array,
            err_msg="Image constructor mangled input NumPy array.")

        # Now make an opposite-endian Numpy array, to initialize the Image.
        new_type = array_dtype.newbyteorder('S')
        test_arr = np.ones((3,4), dtype=new_type)
        test_arr[1,3] = -5
        test_arr[2,2] = 7
        # Initialize the Image from it.
        test_im = galsim.Image(test_arr)
        # Check that the image.array attribute matches the original.
        np.testing.assert_array_equal(
            test_arr, test_im.array,
            err_msg="Image constructor mangled input NumPy array (endian issues).")

        do_pickle(test_im)


@timer
def test_Image_view():
    """Test the functionality of image.view(...)
    """
    im = galsim.ImageI(25,25, wcs=galsim.AffineTransform(0.23,0.01,-0.02,0.22,
                       galsim.PositionI(13,13)))
    im.fill(17)
    assert im.wcs == galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(13,13))
    assert im.bounds == galsim.BoundsI(1,25,1,25)
    assert im(11,19) == 17  # I'll keep editing this pixel to new values.
    do_pickle(im)

    # Test view with no arguments
    imv = im.view()
    assert imv.wcs == im.wcs
    assert imv.bounds == im.bounds
    imv.setValue(11,19, 20)
    assert imv(11,19) == 20
    assert im(11,19) == 20
    do_pickle(im)
    do_pickle(imv)

    # Test view with new origin
    imv = im.view(origin=(0,0))
    assert im.wcs == galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(13,13))
    assert imv.wcs == galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(12,12))
    assert im.bounds == galsim.BoundsI(1,25,1,25)
    assert imv.bounds == galsim.BoundsI(0,24,0,24)
    imv.setValue(10,18, 30)
    assert imv(10,18) == 30
    assert im(11,19) == 30
    imv2 = im.view()
    imv2.setOrigin(0,0)
    assert imv.bounds == imv2.bounds
    assert imv.wcs == imv2.wcs
    do_pickle(imv)
    do_pickle(imv2)

    # Test view with new center
    imv = im.view(center=(0,0))
    assert im.wcs == galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(13,13))
    assert imv.wcs == galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(0,0))
    assert im.bounds == galsim.BoundsI(1,25,1,25)
    assert imv.bounds == galsim.BoundsI(-12,12,-12,12)
    imv.setValue(-2,6, 40)
    assert imv(-2,6) == 40
    assert im(11,19) == 40
    imv2 = im.view()
    imv2.setCenter(0,0)
    assert imv.bounds == imv2.bounds
    assert imv.wcs == imv2.wcs
    do_pickle(imv)
    do_pickle(imv2)

    # Test view with new scale
    imv = im.view(scale=0.17)
    assert im.wcs == galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(13,13))
    assert imv.wcs == galsim.PixelScale(0.17)
    assert imv.bounds == im.bounds
    imv.setValue(11,19, 50)
    assert imv(11,19) == 50
    assert im(11,19) == 50
    imv2 = im.view()
    imv2.wcs = None
    imv2.scale = 0.17
    assert imv.bounds == imv2.bounds
    assert imv.wcs == imv2.wcs
    do_pickle(imv)
    do_pickle(imv2)

    # Test view with new wcs
    imv = im.view(wcs=galsim.JacobianWCS(0., 0.23, -0.23, 0.))
    assert im.wcs == galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(13,13))
    assert imv.wcs == galsim.JacobianWCS(0., 0.23, -0.23, 0.)
    assert imv.bounds == im.bounds
    imv.setValue(11,19, 60)
    assert imv(11,19) == 60
    assert im(11,19) == 60
    imv2 = im.view()
    imv2.wcs = galsim.JacobianWCS(0.,0.23,-0.23,0.)
    assert imv.bounds == imv2.bounds
    assert imv.wcs == imv2.wcs
    do_pickle(imv)
    do_pickle(imv2)

    # Go back to original value for that pixel and make sure all are still equal to 17
    im.setValue(11,19, 17)
    assert im.array.min() == 17
    assert im.array.max() == 17


@timer
def test_Image_writeheader():
    """Test the functionality of image.write(...) for images that have header attributes
    """
    # First check: if we have an image.header attribute, it gets written to file.
    im_test = galsim.Image(10, 10)
    key_name = 'test_key'
    im_test.header = galsim.FitsHeader(header={key_name : 'test_val'})
    test_file = os.path.join(datadir, "test_header.fits")
    im_test.write(test_file)
    new_header = galsim.FitsHeader(test_file)
    assert key_name.upper() in new_header.keys()

    # Second check: if we have an image.header attribute that modifies some keywords used by the
    # WCS, then make sure it doesn't overwrite the WCS.
    im_test.wcs = galsim.JacobianWCS(0., 0.23, -0.23, 0.)
    im_test.header = galsim.FitsHeader(header={'CD1_1' : 10., key_name : 'test_val'})
    im_test.write(test_file)
    new_header = galsim.FitsHeader(test_file)
    assert key_name.upper() in new_header.keys()
    assert new_header['CD1_1'] == 0.0


@timer
def test_ne():
    """ Check that inequality works as expected."""
    array1 = np.arange(32*32).reshape(32, 32).astype(float)
    array2 = array1.copy()
    array2[15, 15] += 2

    objs = [galsim.ImageD(array1),
            galsim.ImageD(array2),
            galsim.ImageD(array2, make_const=True),
            galsim.ImageD(array1, wcs=galsim.PixelScale(0.2)),
            galsim.ImageD(array1, xmin=2)]
    all_obj_diff(objs)


@timer
def test_copy():
    """Test different ways to copy an Image.
    """
    wcs=galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(13,13))
    im = galsim.Image(25,25, wcs=wcs)
    gn = galsim.GaussianNoise(sigma=1.7)
    im.addNoise(gn)

    assert im.wcs == galsim.AffineTransform(0.23,0.01,-0.02,0.22, galsim.PositionI(13,13))
    assert im.bounds == galsim.BoundsI(1,25,1,25)

    # Simplest way to copy is copy()
    im2 = im.copy()
    assert im2.wcs == im.wcs
    assert im2.bounds == im.bounds
    np.testing.assert_array_equal(im2.array, im.array)

    # Make sure it actually copied the array, not just made a view of it.
    im2.setValue(3,8,11.)
    assert im(3,8) != 11.

    # Can also use constructor to "copy", although this doesn't copy the numpy array.
    im3 = galsim.Image(im)
    assert im3.wcs == im.wcs
    assert im3.bounds == im.bounds
    np.testing.assert_array_equal(im3.array, im.array)
    im3.setValue(3,8,11.)
    assert im(3,8) == 11.   # im value changes when im3 value changes.

    # Constructor can change the wcs, but keep the array.
    im4 = galsim.Image(im, scale=0.6)
    assert im4.wcs != im.wcs            # wcs is not equal this time.
    assert im4.bounds == im.bounds
    np.testing.assert_array_equal(im4.array, im.array)
    im4.setValue(3,8,13.)
    assert im(3,8) == 13.

    im5 = galsim.Image(im, wcs=galsim.PixelScale(1.4))
    assert im5.wcs != im.wcs            # wcs is not equal this time.
    assert im5.bounds == im.bounds
    np.testing.assert_array_equal(im5.array, im.array)
    im5.setValue(3,8,15.)
    assert im(3,8) == 15.

    im6 = galsim.Image(im, wcs=wcs)
    assert im6.wcs == im.wcs            # This is the same wcs now.
    assert im6.bounds == im.bounds
    np.testing.assert_array_equal(im6.array, im.array)
    im6.setValue(3,8,17.)
    assert im(3,8) == 17.

    # With dtype different from the original, then should actually copy.
    im7 = galsim.Image(im, dtype=float)
    assert im7.wcs == im.wcs
    assert im7.bounds == im.bounds
    np.testing.assert_array_equal(im7.array, im.array)
    im7.setValue(3,8,11.)
    assert im(3,8) != 11.

    im8 = galsim.Image(im, wcs=wcs, dtype=float)
    assert im8.wcs == im.wcs            # This is the same wcs now.
    assert im8.bounds == im.bounds
    np.testing.assert_array_equal(im8.array, im.array)
    im8.setValue(3,8,11.)
    assert im(3,8) != 11.

    # Check that a slice image copies correctly
    slice_array = large_array.astype(complex)[::3,::2]
    im_slice = galsim.Image(slice_array, wcs=wcs)
    im9 = im_slice.copy()
    assert im9.wcs == im_slice.wcs
    assert im9.bounds == im_slice.bounds
    np.testing.assert_array_equal(im9.array, im_slice.array)
    im9.setValue(2,3,11.)
    assert im9(2,3) == 11.
    assert im_slice(2,3) != 11.


@timer
def test_complex_image():
    """Additional tests that are relevant for complex Image types
    """

    # Some complex modifications to tests in test_Image_basic
    im1 = galsim.Image(ncol, nrow, dtype=complex)
    im1_view = im1.view()
    im1_cview = im1.view(make_const=True)
    im2 = galsim.ImageC(ncol, nrow, init_value=23)
    im2_view = im2.view()
    im2_cview = im2.view(make_const=True)
    im2_conj = im2.conjugate()

    # Check various ways to set and get values
    for y in range(1,nrow+1):
        for x in range(1,ncol+1):
            im1.setValue(x,y, 100 + 10*x + y + 13j*x + 23j*y)
            im2_view.setValue(x,y, 100 + 10*x + y + 13j*x + 23j*y)

    for y in range(1,nrow+1):
        for x in range(1,ncol+1):
            value = 100 + 10*x + y + 13j*x + 23j*y
            assert im1(x,y) == value
            assert im1.view()(x,y) == value
            assert im1.view(make_const=True)(x,y) == value
            assert im2(x,y) == value
            assert im2_view(x,y) == value
            assert im2_cview(x,y) == value
            assert im1.conjugate()(x,y) == np.conjugate(value)

            # complex conjugate is not a view into the original.
            assert im2_conj(x,y) == 23
            assert im2.conjugate()(x,y) == np.conjugate(value)

            value2 = 10*x + y + 20j*x + 2j*y
            im1.setValue(x,y, value2)
            im2_view.setValue(x,y, value2)
            assert im1(x,y) == value2
            assert im1.view()(x,y) == value2
            assert im1.view(make_const=True)(x,y) == value2
            assert im2(x,y) == value2
            assert im2_view(x,y) == value2
            assert im2_cview(x,y) == value2

            assert im1.real(x,y) == value2.real
            assert im1.view().real(x,y) == value2.real
            assert im1.view(make_const=True).real(x,y) == value2.real
            assert im2.real(x,y) == value2.real
            assert im2_view.real(x,y) == value2.real
            assert im2_cview.real(x,y) == value2.real
            assert im1.imag(x,y) == value2.imag
            assert im1.view().imag(x,y) == value2.imag
            assert im1.view(make_const=True).imag(x,y) == value2.imag
            assert im2.imag(x,y) == value2.imag
            assert im2_view.imag(x,y) == value2.imag
            assert im2_cview.imag(x,y) == value2.imag
            assert im1.conjugate()(x,y) == np.conjugate(value2)
            assert im2.conjugate()(x,y) == np.conjugate(value2)

            rvalue3 = 12*x + y
            ivalue3 = x + 21*y
            value3 = rvalue3 + 1j * ivalue3
            im1.real.setValue(x,y, rvalue3)
            im1.imag.setValue(x,y, ivalue3)
            im2_view.real.setValue(x,y, rvalue3)
            im2_view.imag.setValue(x,y, ivalue3)
            assert im1(x,y) == value3
            assert im1.view()(x,y) == value3
            assert im1.view(make_const=True)(x,y) == value3
            assert im2(x,y) == value3
            assert im2_view(x,y) == value3
            assert im2_cview(x,y) == value3
            assert im1.conjugate()(x,y) == np.conjugate(value3)
            assert im2.conjugate()(x,y) == np.conjugate(value3)

    # Check view of given data
    im3_view = galsim.Image((1+2j)*ref_array.astype(complex))
    slice_array = (large_array * (1+2j)).astype(complex)[::3,::2]
    im4_view = galsim.Image(slice_array)
    for y in range(1,nrow+1):
        for x in range(1,ncol+1):
            assert im3_view(x,y) == 10*x + y + 20j*x + 2j*y
            assert im4_view(x,y) == 10*x + y + 20j*x + 2j*y

    # Check picklability
    do_pickle(im1)
    do_pickle(im1_view)
    do_pickle(im2)
    do_pickle(im2_view)
    do_pickle(im3_view)
    do_pickle(im4_view)

@timer
def test_complex_image_arith():
    """Additional arithmetic tests that are relevant for complex Image types
    """
    image1 = galsim.ImageD(ref_array)

    # Binary ImageD op complex scalar
    image2 = image1 + (2+5j)
    np.testing.assert_array_equal(image2.array, ref_array + (2+5j),
            err_msg="ImageD + complex is not correct")
    image2 = image1 - (2+5j)
    np.testing.assert_array_equal(image2.array, ref_array - (2+5j),
            err_msg="ImageD - complex is not correct")
    image2 = image1 * (2+5j)
    np.testing.assert_array_equal(image2.array, ref_array * (2+5j),
            err_msg="ImageD * complex is not correct")
    image2 = image1 / (2+5j)
    np.testing.assert_array_equal(image2.array, ref_array / (2+5j),
            err_msg="ImageD / complex is not correct")

    # Binary complex scalar op ImageD
    image2 = (2+5j) + image1
    np.testing.assert_array_equal(image2.array, ref_array + (2+5j),
            err_msg="complex + ImageD is not correct")
    image2 = (2+5j) - image1
    np.testing.assert_array_equal(image2.array, -ref_array + (2+5j),
            err_msg="complex - ImageD is not correct")
    image2 = (2+5j) * image1
    np.testing.assert_array_equal(image2.array, ref_array * (2+5j),
            err_msg="complex * ImageD is not correct")
    image2 = (2+5j) / image1
    np.testing.assert_array_equal(image2.array, (2+5j) / ref_array.astype(float),
            err_msg="complex / ImageD is not correct")

    image2 = image1 * (3+1j)

    # Binary ImageC op complex scalar
    image3 = image2 + (2+5j)
    np.testing.assert_array_equal(image3.array, (3+1j)*ref_array + (2+5j),
            err_msg="ImageC + complex is not correct")
    image3 = image2 - (2+5j)
    np.testing.assert_array_equal(image3.array, (3+1j)*ref_array - (2+5j),
            err_msg="ImageC - complex is not correct")
    image3 = image2 * (2+5j)
    np.testing.assert_array_equal(image3.array, (3+1j)*ref_array * (2+5j),
            err_msg="ImageC * complex is not correct")
    image3 = image2 / (2+5j)
    np.testing.assert_array_equal(image3.array, (3+1j)*ref_array / (2+5j),
            err_msg="ImageC / complex is not correct")

    # Binary complex scalar op ImageC
    image3 = (2+5j) + image2
    np.testing.assert_array_equal(image3.array, (3+1j)*ref_array + (2+5j),
            err_msg="complex + ImageC is not correct")
    image3 = (2+5j) - image2
    np.testing.assert_array_equal(image3.array, (-3-1j)*ref_array + (2+5j),
            err_msg="complex - ImageC is not correct")
    image3 = (2+5j) * image2
    np.testing.assert_array_equal(image3.array, (3+1j)*ref_array * (2+5j),
            err_msg="complex * ImageC is not correct")
    image3 = (2+5j) / image2
    np.testing.assert_array_equal(image3.array, (2+5j) / ((3+1j)*ref_array),
            err_msg="complex / ImageC is not correct")

    # Binary ImageD op ImageC
    image3 = image1 + image2
    np.testing.assert_array_equal(image3.array, (4+1j)*ref_array,
            err_msg="ImageD + ImageC is not correct")
    image3 = image1 - image2
    np.testing.assert_array_equal(image3.array, (-2-1j)*ref_array,
            err_msg="ImageD - ImageC is not correct")
    image3 = image1 * image2
    np.testing.assert_array_equal(image3.array, (3+1j)*ref_array**2,
            err_msg="ImageD * ImageC is not correct")
    image3 = image1 / image2
    np.testing.assert_almost_equal(image3.array, 1./(3+1j), decimal=12,
            err_msg="ImageD / ImageC is not correct")

    # Binary ImageC op ImageD
    image3 = image2 + image1
    np.testing.assert_array_equal(image3.array, (4+1j)*ref_array,
            err_msg="ImageD + ImageC is not correct")
    image3 = image2 - image1
    np.testing.assert_array_equal(image3.array, (2+1j)*ref_array,
            err_msg="ImageD - ImageC is not correct")
    image3 = image2 * image1
    np.testing.assert_array_equal(image3.array, (3+1j)*ref_array**2,
            err_msg="ImageD * ImageC is not correct")
    image3 = image2 / image1
    np.testing.assert_almost_equal(image3.array, (3+1j), decimal=12,
            err_msg="ImageD / ImageC is not correct")

    # Binary ImageC op ImageC
    image3 = (4-3j) * image1
    image4 = image2 + image3
    np.testing.assert_array_equal(image4.array, (7-2j)*ref_array,
            err_msg="ImageC + ImageC is not correct")
    image4 = image2 - image3
    np.testing.assert_array_equal(image4.array, (-1+4j)*ref_array,
            err_msg="ImageC - ImageC is not correct")
    image4 = image2 * image3
    np.testing.assert_array_equal(image4.array, (15-5j)*ref_array**2,
            err_msg="ImageC * ImageC is not correct")
    image4 = image2 / image3
    np.testing.assert_almost_equal(image4.array, (9+13j)/25., decimal=12,
            err_msg="ImageC / ImageC is not correct")

    # In place ImageC op complex scalar
    image4 = image2.copy()
    image4 += (2+5j)
    np.testing.assert_array_equal(image4.array, (3+1j)*ref_array + (2+5j),
            err_msg="ImageC + complex is not correct")
    image4 = image2.copy()
    image4 -= (2+5j)
    np.testing.assert_array_equal(image4.array, (3+1j)*ref_array - (2+5j),
            err_msg="ImageC - complex is not correct")
    image4 = image2.copy()
    image4 *= (2+5j)
    np.testing.assert_array_equal(image4.array, (3+1j)*ref_array * (2+5j),
            err_msg="ImageC * complex is not correct")
    image4 = image2.copy()
    image4 /= (2+5j)
    np.testing.assert_array_equal(image4.array, (3+1j)*ref_array / (2+5j),
            err_msg="ImageC / complex is not correct")

    # In place ImageC op ImageD
    image4 = image2.copy()
    image4 += image1
    np.testing.assert_array_equal(image4.array, (4+1j)*ref_array,
            err_msg="ImageD + ImageC is not correct")
    image4 = image2.copy()
    image4 -= image1
    np.testing.assert_array_equal(image4.array, (2+1j)*ref_array,
            err_msg="ImageD - ImageC is not correct")
    image4 = image2.copy()
    image4 *= image1
    np.testing.assert_array_equal(image4.array, (3+1j)*ref_array**2,
            err_msg="ImageD * ImageC is not correct")
    image4 = image2.copy()
    image4 /= image1
    np.testing.assert_almost_equal(image4.array, (3+1j), decimal=12,
            err_msg="ImageD / ImageC is not correct")

    # In place ImageC op ImageC
    image4 = image2.copy()
    image4 += image3
    np.testing.assert_array_equal(image4.array, (7-2j)*ref_array,
            err_msg="ImageC + ImageC is not correct")
    image4 = image2.copy()
    image4 -= image3
    np.testing.assert_array_equal(image4.array, (-1+4j)*ref_array,
            err_msg="ImageC - ImageC is not correct")
    image4 = image2.copy()
    image4 *= image3
    np.testing.assert_array_equal(image4.array, (15-5j)*ref_array**2,
            err_msg="ImageC * ImageC is not correct")
    image4 = image2.copy()
    image4 /= image3
    np.testing.assert_almost_equal(image4.array, (9+13j)/25., decimal=12,
            err_msg="ImageC / ImageC is not correct")

@timer
def test_wrap():
    """Test the image.wrap() function.
    """
    # Start with a fairly simple test where the image is 4 copies of the same data:
    im_orig = galsim.Image([[ 11., 12., 13., 14., 11., 12., 13., 14. ],
                            [ 21., 22., 23., 24., 21., 22., 23., 24. ],
                            [ 31., 32., 33., 34., 31., 32., 33., 34. ],
                            [ 41., 42., 43., 44., 41., 42., 43., 44. ],
                            [ 11., 12., 13., 14., 11., 12., 13., 14. ],
                            [ 21., 22., 23., 24., 21., 22., 23., 24. ],
                            [ 31., 32., 33., 34., 31., 32., 33., 34. ],
                            [ 41., 42., 43., 44., 41., 42., 43., 44. ]])
    im = im_orig.copy()
    b = galsim.BoundsI(1,4,1,4)
    im_quad = im_orig[b]
    im_wrap = im.wrap(b)
    np.testing.assert_almost_equal(im_wrap.array, 4.*im_quad.array, 12,
                                   "image.wrap() into first quadrant did not match expectation")

    # The same thing should work no matter where the lower left corner is:
    for xmin, ymin in ( (1,5), (5,1), (5,5), (2,3), (4,1) ):
        b = galsim.BoundsI(xmin, xmin+3, ymin, ymin+3)
        im_quad = im_orig[b]
        im = im_orig.copy()
        im_wrap = im.wrap(b)
        np.testing.assert_almost_equal(im_wrap.array, 4.*im_quad.array, 12,
                                       "image.wrap(%s) did not match expectation"%b)
        np.testing.assert_array_equal(im_wrap.array, im[b].array,
                                      "image.wrap(%s) did not return the right subimage")
        im[b].fill(0)
        np.testing.assert_array_equal(im_wrap.array, im[b].array,
                                      "image.wrap(%s) did not return a view of the original")

    # Now test where the subimage is not a simple fraction of the original, and all the
    # sizes are different.
    im = galsim.ImageD(17, 23, xmin=0, ymin=0)
    b = galsim.BoundsI(7,9,11,18)
    im_test = galsim.ImageD(b, init_value=0)
    for i in range(17):
        for j in range(23):
            val = np.exp(i/7.3) + (j/12.9)**3  # Something randomly complicated...
            im[i,j] = val
            # Find the location in the sub-image for this point.
            ii = (i-b.xmin) % (b.xmax-b.xmin+1) + b.xmin
            jj = (j-b.ymin) % (b.ymax-b.ymin+1) + b.ymin
            im_test.addValue(ii,jj,val)
    im_wrap = im.wrap(b)
    np.testing.assert_almost_equal(im_wrap.array, im_test.array, 12,
                                   "image.wrap(%s) did not match expectation"%b)
    np.testing.assert_array_equal(im_wrap.array, im[b].array,
                                  "image.wrap(%s) did not return the right subimage")
    np.testing.assert_equal(im_wrap.bounds, b,
                            "image.wrap(%s) does not have the correct bounds")

    # For complex images (in particular k-space images), we often want the image to be implicitly
    # Hermitian, so we only need to keep around half of it.
    M = 38
    N = 25
    K = 8
    L = 5
    im = galsim.ImageC(2*M+1, 2*N+1, xmin=-M, ymin=-N)  # Explicitly Hermitian
    im2 = galsim.ImageC(2*M+1, N+1, xmin=-M, ymin=0)   # Implicitly Hermitian across y axis
    im3 = galsim.ImageC(M+1, 2*N+1, xmin=0, ymin=-N)   # Implicitly Hermitian across x axis
    print('im = ',im)
    print('im2 = ',im2)
    print('im3 = ',im3)
    b = galsim.BoundsI(-K+1,K,-L+1,L)
    b2 = galsim.BoundsI(-K+1,K,0,L)
    b3 = galsim.BoundsI(0,K,-L+1,L)
    im_test = galsim.ImageC(b, init_value=0)
    for i in range(-M,M+1):
        for j in range(-N,N+1):
            # An arbitraryish Hermitian function.
            #val = np.exp(i**2/57.3 + 1j*(2.8*i-1.3*j)) + ((2 + 3j*j)/12.9)**3
            val = 2*(i-j)**2 + 3j*(i+j)

            im[i,j] = val
            if j >= 0:
                im2[i,j] = val
            if i >= 0:
                im3[i,j] = val

            ii = (i-b.xmin) % (b.xmax-b.xmin+1) + b.xmin
            jj = (j-b.ymin) % (b.ymax-b.ymin+1) + b.ymin
            im_test.addValue(ii,jj,val)
    #print("im = ",im.array)

    # Confirm that the image is Hermitian.
    for i in range(-M,M+1):
        for j in range(-N,N+1):
            assert im(i,j) == im(-i,-j).conjugate()

    im_wrap = im.wrap(b)
    #print("im_wrap = ",im_wrap.array)
    np.testing.assert_almost_equal(im_wrap.array, im_test.array, 12,
                                   "image.wrap(%s) did not match expectation"%b)
    np.testing.assert_array_equal(im_wrap.array, im[b].array,
                                  "image.wrap(%s) did not return the right subimage")
    np.testing.assert_equal(im_wrap.bounds, b,
                            "image.wrap(%s) does not have the correct bounds")

    im2_wrap = im2.wrap(b2, hermitian='y')
    #print('im_test = ',im_test[b2].array)
    #print('im2_wrap = ',im2_wrap.array)
    #print('diff = ',im2_wrap.array-im_test[b2].array)
    np.testing.assert_almost_equal(im2_wrap.array, im_test[b2].array, 12,
                                   "image.wrap(%s) did not match expectation"%b)
    np.testing.assert_array_equal(im2_wrap.array, im2[b2].array,
                                  "image.wrap(%s) did not return the right subimage")
    np.testing.assert_equal(im2_wrap.bounds, b2,
                            "image.wrap(%s) does not have the correct bounds")

    im3_wrap = im3.wrap(b3, hermitian='x')
    #print('im_test = ',im_test[b3].array)
    #print('im3_wrap = ',im3_wrap.array)
    #print('diff = ',im3_wrap.array-im_test[b3].array)
    np.testing.assert_almost_equal(im3_wrap.array, im_test[b3].array, 12,
                                   "image.wrap(%s) did not match expectation"%b)
    np.testing.assert_array_equal(im3_wrap.array, im3[b3].array,
                                  "image.wrap(%s) did not return the right subimage")
    np.testing.assert_equal(im3_wrap.bounds, b3,
                            "image.wrap(%s) does not have the correct bounds")

if __name__ == "__main__":
    test_Image_basic()
    test_undefined_image()
    test_Image_FITS_IO()
    test_Image_MultiFITS_IO()
    test_Image_CubeFITS_IO()
    test_Image_array_view()
    test_Image_binary_add()
    test_Image_binary_subtract()
    test_Image_binary_multiply()
    test_Image_binary_divide()
    test_Image_binary_scalar_add()
    test_Image_binary_scalar_subtract()
    test_Image_binary_scalar_multiply()
    test_Image_binary_scalar_divide()
    test_Image_binary_scalar_pow()
    test_Image_inplace_add()
    test_Image_inplace_subtract()
    test_Image_inplace_multiply()
    test_Image_inplace_divide()
    test_Image_inplace_scalar_add()
    test_Image_inplace_scalar_subtract()
    test_Image_inplace_scalar_multiply()
    test_Image_inplace_scalar_divide()
    test_Image_inplace_scalar_pow()
    test_Image_subImage()
    test_Image_resize()
    test_ConstImage_array_constness()
    test_BoundsI_init_with_non_pure_ints()
    test_Image_constructor()
    test_Image_view()
    test_Image_writeheader()
    test_ne()
    test_copy()
    test_complex_image()
    test_complex_image_arith()
    test_wrap()
