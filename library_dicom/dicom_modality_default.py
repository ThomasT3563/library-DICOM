
import numpy as np
import pydicom
import warnings
import os
import random
import SimpleITK as sitk

class modality_DICOM_default(object):
    
    def __init__(self,filenames):
        
        self.filenames = filenames
        self.output_format = np.float32

    def __GatherSlices(self):
        """ called by convert_to_NIFTI """
        self.slices = [pydicom.dcmread(s) for s in self.filenames]
        self.slices.sort(key=lambda x:int(x.ImagePositionPatient[2]),reverse=True)
    
    def __getPixelData(self):
        """ called by convert_to_NIFTI """
        pixel_data = [self.__RescaleSlope_PixelData(ds) for ds in self.slices]
        return pixel_data
    
    def __RescaleSlope_PixelData(self,ds):
        """ called by __getPixelData """
        return ds.pixel_array*float(ds.RescaleSlope)+float(ds.RescaleIntercept)
    
    def __getMetadata(self):
        """ called by convert_to_NIFTI """
        Direction = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0) #hard coded
        Origin = (self.slices[-1].ImagePositionPatient[0],self.slices[-1].ImagePositionPatient[1],self.slices[-1].ImagePositionPatient[2])
        Spacing = (self.slices[-1].PixelSpacing[0],self.slices[-1].PixelSpacing[1],self.__getZSpacing())
        return (Direction,Origin,Spacing)
    
    def __getZSpacing(self):
        """ called by __getMetadata """
        Z_positions = [ds.ImagePositionPatient[2] for ds in self.slices]
        
        initial_z_spacing = Z_positions[0]-Z_positions[1]
        for i in range(1,len(Z_positions)):
            z_spacing = Z_positions[i-1]-Z_positions[i]
            if (z_spacing!=initial_z_spacing):
                warnings.warn("Z axis Spacing is not constant : %s / %s" % (z_spacing,initial_z_spacing))
        return initial_z_spacing
    
    def convert_to_NIFTI(self,path_save,filename=None):
        """ Generates .nii files from the DICOM serie """

        # generates folder
        if not os.path.exists(path_save):
            os.makedirs(path_save)
        
        # generates filename
        if filename is None:
            filename = path_save+'/'+str(random.randint(0,1e8))+'.nii'
        else:
            filename = path_save+'/'+filename
        
        self.__GatherSlices()
        (Direction,Origin,Spacing) = self.__getMetadata()
        
        Array = np.stack(self.__getPixelData(),axis=0).astype(self.output_format)
        
        sitk_img = sitk.GetImageFromArray(Array)
        
        sitk_img.SetDirection(Direction)
        sitk_img.SetOrigin(Origin)
        sitk_img.SetSpacing(Spacing)
        #sitk_img.SetMetaData()
        
        sitk.WriteImage(sitk_img,filename)
        
    def generate_RTSTRUCT(self,mask,path_new_directory,existing_RTSTRUCT=None,filename=None):
        """ Generates a RTSTRUCT instance from a mask """
        warnings.warn("work in progress")

