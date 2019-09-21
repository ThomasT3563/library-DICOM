
import numpy as np

from library_dicom.dicom_modality_default import modality_DICOM_default

class modality_DICOM_TEP(modality_DICOM_default):
    
    def __init__(self,filenames):
        super().__init__(filenames)
        self.output_format = np.float32
    
