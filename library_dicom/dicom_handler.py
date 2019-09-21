
import pydicom
import glob
import warnings

from library_dicom.dicom_modality_default import modality_DICOM_default
from library_dicom.dicom_modality_ct import modality_DICOM_CT
from library_dicom.dicom_modality_tep import modality_DICOM_TEP
from library_dicom.dicom_modality_rtstruct import modality_DICOM_RTSTRUCT

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
        self.file.convert_to_NIFTI(path_save=path_save,filename=filename)
        
    def generate_RTSTRUCT(self,mask,path_new_directory,existing_RTSTRUCT=None,filename=None):
  
        if existing_RTSTRUCT is None:
            # generates 
            #existing_RTSTRUCT = modality_DICOM_RTSTRUCT(self.filenames)
            
            pass
            
        self.file.generate_RTSTRUCT(mask=mask,path_new_directory=path_new_directory,
                                    existing_RTSTRUCT=existing_RTSTRUCT,filename=filename)



