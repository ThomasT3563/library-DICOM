
import numpy as np

from library_dicom.dicom_modality_default import modality_DICOM_default

class modality_DICOM_RTSTRUCT(modality_DICOM_default):
    
    def __init__(self,filenames):
        super().__init__(filenames)
        self.output_format = np.float32
    
    def convert_to_NIFTI(self,path_save,filename=None):
        warning.warn("operation not working yet")
        pass
    
    def add_ROI(self):
        warning.warn("operation not working yet")
        pass
