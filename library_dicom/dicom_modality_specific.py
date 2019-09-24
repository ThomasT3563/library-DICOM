
import pydicom
import random
import numpy as np
import sys
import warnings
import datetime

from library_dicom.dicom_modality_default import modality_DICOM_default

from library_dicom.new_RTSTRUCT.ROIContour import ROIContour
from library_dicom.new_RTSTRUCT.RTROIObservations import RTROIObservations
from library_dicom.new_RTSTRUCT.StructureSetROI import StructureSetROI

############################################################################################################

class modality_DICOM_CT(modality_DICOM_default):
    
    def __init__(self,filenames):
        super().__init__(filenames)
        self.output_format = np.int16

############################################################################################################

class modality_DICOM_TEP(modality_DICOM_default):
    
    def __init__(self,filenames):
        super().__init__(filenames)
        self.output_format = np.float32

    def __RescaleSlope_PixelData(self,ds):
        """ called by __getPixelData """
        warnings.warn("SUV computation not implemented")
        return ds.pixel_array*float(ds.RescaleSlope)+float(ds.RescaleIntercept)

############################################################################################################

class modality_DICOM_RTSTRUCT(modality_DICOM_default):
    
    def __init__(self,filenames):
        super().__init__(filenames)
        self.output_format = np.float32
        
        if len(self.filenames)>1:
            warnings.warn("Several RTSTRUCT defined in the same directory, errors might occur")

        self.rawfile = pydicom.dcmread(self.filenames[0])
        (self.ROI_defined, self.ROI_available) = self.extractROIlist()
        (self.ObservationNumbers,self.ReferenceROINumbers) = self.extractROInumbers()

    def convert_to_NIFTI(self,filename=None):
        """ deprecation """
        
        # TODO
        warnings.warn("operation not working yet")
        
        return None
    
    def generates_empty_RTSTRUCT(self,filename):
        """ deprecation : create a empty DICOM RTSTRUCT file, save it and return the modality_DICOM_RTSTRUCT object """
        sys.exit('Cannot create a new DICOM RTSTRUCT from a DICOM RTSTRUCT')

    def add_MASK_to_RTSTRUCT(self,mask,labels_names,labels_numbers_numbers,file_RTSTRUCT,filename):
        """ deprecation : from an existing RTSTRUCT, generates new UIDs, add a Mask and save it """
        sys.exit('Cannot create a new DICOM RTSTRUCT from a DICOM RTSTRUCT')

    def instantiate_SOPUIDs(self,ReferencedSOPClassUID,
                            list_SOPInstanceUID,FrameOfReferenceUID):
        """ by generating new SOP UIDs, create a pseudo new RTSTRUCT """
        
        # global parameters
        # possibility to add shape, pixel spacing etc
        self.ReferencedSOPClassUID = ReferencedSOPClassUID
        self.list_SOPInstanceUID = list_SOPInstanceUID
        self.FrameOfReferenceUID = FrameOfReferenceUID
        
        # rawfile parameters
        self.rawfile.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        self.rawfile.SOPInstanceUID = self.rawfile.file_meta.MediaStorageSOPInstanceUID
        dt = datetime.datetime.now()
        self.rawfile.InstanceCreationDate = dt.strftime('%Y%m%d')
        self.rawfile.InstanceCreationTime = dt.strftime('%H%M%S.%f')
        self.rawfile.InstanceNumber = '1'
        self.rawfile.SeriesInstanceUID = pydicom.uid.generate_uid()
        self.rawfile.SeriesNumber = random.randint(0,1e3)   
        
        return None
    
    def add_ROIs(self,list_ROI,list_UID,labels_names,labels_numbers):
        """ add ROIs to an existing DICOM RTSTRUCT """

        for contours,UIDs,label_name in zip(list_ROI,list_UID,labels_names):
            self.add_ROI(ROI_name=label_name,
                         ROI_number=None, #automatic identation
                         ROI_list_ContourData=contours,
                         ROI_list_SOPInstanceUID=UIDs,
                         ROI_FrameOfReferenceUID=None, #automatic
                         ROI_Color=['255', '0', '0'])

        return None
   
    def extractROIlist(self):
        """
            Extract list of ROI defined and available 
                defined : ROI existing in StructureSetROISequence
                available : ROI with ContourSequence
        """
        # check ROI defined != ROI with actual contour
        ROI_defined = [roitr.ROIName for roitr in self.rawfile.StructureSetROISequence]
        ROI_available = [label_name for label_name in ROI_defined if 'ContourSequence' in self.rawfile.ROIContourSequence[ROI_defined.index(label_name)]] 
        return (ROI_defined,ROI_available)
    
    def extractROInumbers(self):
        """
            Extract reference numbers of ROIs defined in the rtstruct
        """
        ObservationNumbers = []
        ReferenceROINumbers = []
        for rtroi in self.rawfile.RTROIObservationsSequence:
            ObservationNumbers.append(rtroi.ObservationNumber)
            ReferenceROINumbers.append(rtroi.ReferencedROINumber)
        return (ObservationNumbers,ReferenceROINumbers)

    def add_ROI(self,
                ROI_name = 'VOID',
                ROI_number = None,
                ROI_list_ContourData = [[1.0,1.0,1.0],],
                ROI_list_SOPInstanceUID = None,
                ROI_FrameOfReferenceUID = None,
                ROI_Color=['255', '0', '0']
                ):
        """
            Add a ROI to the RTSTRUCT with at least:
                - RTROIObservationsSequence
                - ROIContourSequence
                - StructureSetROISequence
                
            If not indicated, compute automatically :
                - ROI number
                - ROI_FrameOfReferenceUID
        """
        
        if ROI_number is None:
            ROI_number = max(self.ReferenceROINumbers)+1
            
        if ROI_FrameOfReferenceUID is None:
            ROI_FrameOfReferenceUID = self.FrameOfReferenceUID
        
        if ROI_list_SOPInstanceUID is None:
            ROI_list_SOPInstanceUID = [self.list_SOPInstanceUID[0],]
        
        if ('RTROIObservationsSequence' in self.rawfile.dir()) and ('ROIContourSequence' in self.rawfile.dir()) and ('StructureSetROISequence' in self.rawfile.dir()):
            
            # initialization of new Datasets
            new_RTROIObservations = self.__create_RTROIObservations(
                ReferencedROINumber=ROI_number,
                ROIObservationLabel=ROI_name
            )
            new_ROIContour = self.__create_ROIContour(
                list_ContourData=ROI_list_ContourData,
                list_SOPInstanceUID=ROI_list_SOPInstanceUID,
                ReferencedSOPClassUID=self.ReferencedSOPClassUID,
                ROIDisplayColor=ROI_Color,
                ReferencedROINumber=ROI_number
            ) 
            new_StructureSetROI = self.__create_StructureSetROI(
                ROIGenerationAlgorithm='MANUAL',
                ROIName=ROI_name,
                ROINumber=ROI_number,
                FrameOfReferenceUID=ROI_FrameOfReferenceUID
            ) 

            # object to update when adding a ROI
            self.rawfile.RTROIObservationsSequence.append(new_RTROIObservations)
            self.rawfile.ROIContourSequence.append(new_ROIContour)
            self.rawfile.StructureSetROISequence.append(new_StructureSetROI)

            # update ROI parameters
            (self.ROI_defined, self.ROI_available) = self.extractROIlist()
            (self.ObservationNumbers,self.ReferenceROINumbers) = self.extractROInumbers()

        else:
            raise AssertionError('rtstruct element needs ROIContourSequence and RTROIObservationsSequence')
    
    def __create_RTROIObservations(self,
                                   ReferencedROINumber=None,
                                   ROIObservationLabel='VOID'):
        """
            Generates a RTROIObservations item to append in a
            RTROIObservationsSequence
                - ObservationNumber
                - ROIInterpreter
                - ROIObservationLabel
                - RTROIInterpretedType
                - ReferencedROINumber
        """
        
        if ReferencedROINumber is None:
            ReferencedROINumber = self.ReferenceROINumbers[-1]+1
            
        # possibility to change, depends on norms
        ObservationNumber = ReferencedROINumber
        
        new_RTROIObservations = RTROIObservations(
            ObservationNumber=ObservationNumber,
            ReferencedROINumber=ReferencedROINumber,
            ROIObservationLabel=ROIObservationLabel)
        return new_RTROIObservations
    
    def __create_ROIContour(self,
                            list_ContourData=[[1.0,1.0,1.0],],
                            list_SOPInstanceUID=None,
                            ReferencedSOPClassUID='',
                            ROIDisplayColor=['255', '0', '0'],
                            ReferencedROINumber=None):
        """
            Generates a ROIContour item to append in a ROIContourSequence
                - ContourSequence
                - ROIDisplayColor
                - ReferencedROINumber
        """
        if ReferencedROINumber is None:
            ReferencedROINumber = self.ReferenceROINumbers[-1]+1
        
        if list_SOPInstanceUID is None:
            list_SOPInstanceUID = [self.list_SOPInstanceUID[0],]
        
        new_ROIContour = ROIContour(
            list_ContourData=list_ContourData,
            list_SOPInstanceUID=list_SOPInstanceUID,
            ReferencedSOPClassUID=ReferencedSOPClassUID,
            ROIDisplayColor=ROIDisplayColor,
            ReferencedROINumber=ReferencedROINumber)
        return new_ROIContour
    
    def __create_StructureSetROI(self,
                                 ROIGenerationAlgorithm='MANUAL',
                                 ROIName='VOID',
                                 ROINumber=None,
                                 FrameOfReferenceUID=None):
        """
            Generates a StructureSetROI item to append in a 
            StructureSetROISequence
                - ROIGenerationAlgorithm
                - ROIName
                - ROINumber
                - ReferencedFrameOfReferenceUID
        """
        if ROINumber is None:
            ROINumber = self.ReferenceROINumbers[-1]+1
        
        if FrameOfReferenceUID is None:
            FrameOfReferenceUID = self.heir_tags.get('FrameOfReferenceUID')

        new_StructureSetROI = StructureSetROI(
            ROIGenerationAlgorithm=ROIGenerationAlgorithm,
            ROIName=ROIName,
            ROINumber=ROINumber,
            ReferencedFrameOfReferenceUID=FrameOfReferenceUID)
        return new_StructureSetROI
    
    def save(self,filename):
        self.rawfile.save_as(filename)
  