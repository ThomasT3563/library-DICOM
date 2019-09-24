
import pydicom
import glob
import warnings
import random
import os

from library_dicom.dicom_modality_default import modality_DICOM_default
from library_dicom.dicom_modality_specific import modality_DICOM_CT,modality_DICOM_TEP,modality_DICOM_RTSTRUCT

class DICOM_handler(object):
    """
        class that handle a dicom folder containing a complete serie
    """
    def __init__(self,dcm_directory):
        
        self.directory = dcm_directory
        self.filenames = glob.glob(dcm_directory+'/**')
        self.modality_UID = self.__determine_modality()
        self.file = self.__get_modality_file()
        
    def __determine_modality(self):
        modality_UID = pydicom.dcmread(self.filenames[0]).SOPClassUID
        for filename in self.filenames:
            with pydicom.dcmread(filename) as ds:
                if ds.SOPClassUID!=modality_UID:
                    warnings.warn("SOPClassUID differ : %s / %s" % (modality_UID,ds.SOPClassUID))
        return modality_UID
    
    def __get_modality_file(self):
        if self.modality_UID=='1.2.840.10008.5.1.4.1.1.2': # CT
            modality_file = modality_DICOM_CT(self.filenames)
        elif self.modality_UID=='1.2.840.10008.5.1.4.1.1.128': # TEP
            modality_file = modality_DICOM_TEP(self.filenames)
        elif self.modality_UID=='1.2.840.10008.5.1.4.1.1.481.3': #RTSTRUCT
            modality_file = modality_DICOM_RTSTRUCT(self.filenames)
        else:
            warning.warn('DICOM modality not recognized')
            self.file = modality_DICOM_default(self.filenames)
        return modality_file
    
            
    def convert_to_NIFTI(self,path_save,filename=None):
        
        # generates folder
        if not os.path.exists(path_save):
            os.makedirs(path_save)
        
        # generates filename
        if filename is None:
            filename = path_save+'/'+str(random.randint(0,1e8))+'.nii'
        else:
            filename = path_save+'/'+filename
        
        self.file.convert_to_NIFTI(filename=filename)
        return None
    
    def generates_empty_RTSTRUCT(self,path_new_directory,filename=None):
        
        # generates folders
        if not os.path.exists(path_new_directory):
            os.makedirs(path_new_directory)
        
        if filename is None:
            filename = path_new_directory+'/'+random.randint(0,1e8)+'.dcm'
        else:
            filename = path_new_directory+'/'+filename
            
        self.file.generates_empty_RTSTRUCT(filename=filename)
        return None
    
    def generate_RTSTRUCT_from_MASK(self,mask,path_new_directory,labels_names,labels_numbers,
                                    existing_RTSTRUCT=None,filename=None):
        
        # generates folders
        if not os.path.exists(path_new_directory):
            os.makedirs(path_new_directory)
        
        if filename is None:
            filename = path_new_directory+'/'+random.randint(0,1e8)+'.dcm'
        else:
            filename = path_new_directory+'/'+filename
        
        # create a new RTSTRUCT
        if existing_RTSTRUCT is None:
            self.file.generates_empty_RTSTRUCT(filename=filename)
            existing_RTSTRUCT = modality_DICOM_RTSTRUCT(filename)

        # add mask to associated RTSTRUCT, generates pseudo new RTSTRUCT and save it at "path_new_directory+filename"
        # by default label 0 is considered as back ground and is ignored
        self.file.add_MASK_to_RTSTRUCT(mask=mask,labels_names=labels_names[1:],labels_numbers=labels_numbers[1:],
                                       file_RTSTRUCT=existing_RTSTRUCT,filename=filename)
        return None

