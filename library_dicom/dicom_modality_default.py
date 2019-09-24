
import numpy as np
import pydicom
import warnings
import os
import random
import SimpleITK as sitk

from library_dicom.new_RTSTRUCT.new_RTSTRUCT_rawfile import new_RTSTRUCT_rawfile
from library_dicom.dicom_manipulations import convert_MASK_to_ROI

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
    
    def convert_to_NIFTI(self,filename=None):
        """ Generates .nii files from the DICOM serie """
        
        self.__GatherSlices()
        (Direction,Origin,Spacing) = self.__getMetadata()
        
        Array = np.stack(self.__getPixelData(),axis=0).astype(self.output_format)
        
        sitk_img = sitk.GetImageFromArray(Array)
        
        sitk_img.SetDirection(Direction)
        sitk_img.SetOrigin(Origin)
        sitk_img.SetSpacing(Spacing)
        #sitk_img.SetMetaData()
        
        sitk.WriteImage(sitk_img,filename)
    
    def __GatherTags(self):
        """ called by generates_empty_RTSTRUCT """

        Tags = {'AccessionNumber':None,
                #'DeviceSerialNumber':None,
                #'Manufacturer':None,
                #'ManufacturerModelName':None,
                'PatientBirthDate':None,
                'PatientBirthTime':None,
                'PatientID':None,
                'PatientName':None,
                'PatientSex':None,
                'PhysiciansOfRecord':None,
                'ReferringPhysicianName':None,
                #'SoftwareVersions':None,
                'SpecificCharacterSet':None,
                #'StationName':None,
                'StudyDate':None,
                'StudyDescription':None,
                'StudyID':None,
                'StudyInstanceUID':None,
                'StudyTime':None,
                'FrameOfReferenceUID':None
                }
        
        with pydicom.dcmread(self.filenames[0]) as dcm:

            for tag in Tags.keys():
                try:
                    Tags[tag] = dcm.get(tag)
                except AttributeError:
                    warnings.warn("AttributeError with tag: %s" % tag)
                    pass
                except Exception:
                    raise Exception

        return Tags
    
    def generates_empty_RTSTRUCT(self,filename):
        """ create a empty DICOM RTSTRUCT file, save it and return the modality_DICOM_RTSTRUCT object """
        
        inheritance_tags = self.__GatherTags()
               
        new_RTSTRUCT = new_RTSTRUCT_rawfile(filename,inheritance_tags)
        new_RTSTRUCT.save_as(filename)

        return None
    
    
    def add_MASK_to_RTSTRUCT(self,mask,labels_names,labels_numbers,file_RTSTRUCT,filename):
        """ from an existing RTSTRUCT, generates new UIDs, add a Mask and save it """

        self.__GatherSlices() # gather and sort self.slices
        self.list_SOPInstanceUID = [s.SOPInstanceUID for s in self.slices]
        
        (Direction,Origin,Spacing) = self.__getMetadata()
        
        # convert MASK to ROI
        list_ROI,list_UID = convert_MASK_to_ROI(mask=mask,
                                                label_numbers=labels_numbers,
                                                list_SOPInstanceUID=self.list_SOPInstanceUID,
                                                dicom_spacing=Spacing,
                                                dicom_origin=Origin)
        
        
        # gathering shared DICOM source parameters
        # parameters that might be needed for new files
        #shape_image = (dcm.Columns,dcm.Rows,len(self.list_SOPInstanceUID))
        #parameters = {'list_SOPInstanceUID':self.list_SOPInstanceUID,
        #              'FrameOfReferenceUID': dcm.FrameOfReferenceUID,
        #              'ShapeImage':shape_image,
        #              'PixelSpacing':dcm.PixelSpacing,
        #              'ImagePositionPatient':dcm.ImagePositionPatient,
        #              'SliceThickness':self.SliceThickness,
        #              'RescaleSlope':dcm.RescaleSlope,
        #              'RescaleIntercept':dcm.RescaleIntercept
        
        # operations specific to RTSTRUCT
        file_RTSTRUCT.instantiate_SOPUIDs(list_SOPInstanceUID = self.list_SOPInstanceUID,
                                          FrameOfReferenceUID = self.slices[0].FrameOfReferenceUID)
        file_RTSTRUCT.add_ROIs(list_ROI,list_UID,labels_names,labels_numbers)
        file_RTSTRUCT.save(filename)
        
        return None


        
        
        
        