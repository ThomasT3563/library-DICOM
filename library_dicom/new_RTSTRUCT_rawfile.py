import datetime
import pydicom
import random

from library_dicom.RTROIObservations import RTROIObservations
from library_dicom.ROIContour import ROIContour
from library_dicom.StructureSetROI import StructureSetROI

class new_RTSTRUCT_rawfile(pydicom.dataset.FileDataset):
    """
        Generates a RTSTRUCT rawfile from a Dicom CT scans Set
    """
    def __init__(self,filename,heir_tags):
        
        file_meta = self.generates_file_meta()
        #print('file meta:')
        #print(file_meta)

        # Generates FileDataset element
        super().__init__(filename,{},file_meta=file_meta, preamble=b"\0" * 128)

        # FileDataset specific fields
        self.is_little_endian = True
        self.is_implicit_VR = True

        #gather and generates tags of the RTSTRUCT file
        self.gathering_tags(heir_tags)
        self.generates_tags()
        
        # instantiate sequence
        self.RTROIObservationsSequence = pydicom.sequence.Sequence()
        self.ROIContourSequence = pydicom.sequence.Sequence()
        self.StructureSetROISequence = pydicom.sequence.Sequence()
        
        # insert empty ROI in sequences
        self.RTROIObservationsSequence.append(RTROIObservations())
        self.ROIContourSequence.append(ROIContour())
        self.StructureSetROISequence.append(StructureSetROI())
        
    def generates_file_meta(self):
        """
            Generates required values for file meta information
            List of tags :
                  - FileMetaInformationGroupLength':
                  - FileMetaInformationVersion'    :
                  - MediaStorageSOPClassUID'       :
                  - MediaStorageSOPInstanceUID'    :
                  - TransferSyntaxUID'             :
                  - ImplementationClassUID'        :
        """
        file_meta = pydicom.dataset.Dataset()
        file_meta.FileMetaInformationGroupLength = 166
        file_meta.FileMetaInformationVersion = b'\x00\x01'
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.481.3' # RT Structure Set Storage
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.TransferSyntaxUID = '1.2.840.10008.1.2' #Implicit VR Little Endian
        file_meta.ImplementationClassUID = '1.2.246.352.70.2.1.7'
        
        return file_meta
    
    def gathering_tags(self,heir_tags):
        """
            Extract each tag+value from dictionnary heir_tags and
            insert it to the FileDataset
            List of tags :
                  - AccessionNumber'       :
                  - PatientBirthDate'      :
                  - PatientBirthTime'      :
                  - PatientID'             :
                  - PatientName'           :
                  - PatientSex'            :
                  - PhysiciansOfRecord'    :
                  - ReferringPhysicianName':
                  - SpecificCharacterSet'  :
                  - StudyDate'             :
                  - StudyDescription'      :
                  - StudyID'               :
                  - StudyInstanceUID'      :
                  - StudyTime'             : 
        """     
        
        self.AccessionNumber = heir_tags.get('AccessionNumber')
        self.PatientBirthDate = heir_tags.get('PatientBirthDate')
        self.PatientBirthTime = heir_tags.get('PatientBirthTime')
        self.PatientID = heir_tags.get('PatientID')
        self.PatientName = heir_tags.get('PatientName')
        self.PatientSex = heir_tags.get('PatientSex')
        self.PhysiciansOfRecord = heir_tags.get('PhysiciansOfRecord')
        self.ReferringPhysicianName = heir_tags.get('ReferringPhysicianName')
        self.SpecificCharacterSet = heir_tags.get('SpecificCharacterSet')
        self.StudyDate = heir_tags.get('StudyDate')
        self.StudyDescription = heir_tags.get('StudyDescription')
        self.StudyID = heir_tags.get('StudyID')
        self.StudyInstanceUID = heir_tags.get('StudyInstanceUID')
        self.StudyTime = heir_tags.get('StudyTime')

        return None
    
    def generates_tags(self):
        """
            Generates new values for tags specific to RTSTRUCT file
            List custom tags:
                  - AccessionNumber'       :
                  - PatientBirthDate'      :
                  - PatientBirthTime'      :
                  - PatientID'             :
                  - PatientName'           :
                  - PatientSex'            :
            List randomly generated tags:
                  - AccessionNumber'       :
                  - PatientBirthDate'      :
                  - PatientBirthTime'      :
                  - PatientID'             :
                  - PatientName'           :
                  - PatientSex'            :
            
        """
        self.ApprovalStatus = 'UNAPPROVED'
        self.Manufacturer   = ''
        dt = datetime.datetime.now()
        self.InstanceCreationDate = dt.strftime('%Y%m%d')
        self.InstanceCreationTime = dt.strftime('%H%M%S.%f')
        self.InstanceNumber = '1'
        self.Modality = 'RTSTRUCT'
        self.ReviewDate = '' #because UNAPPROVED
        self.ReviewTime = '' #because UNAPPROVED
        self.ReviewerName = '' #because UNAPPROVED
        self.SeriesDescription = 'RTSTRUCT generated by DICOM package'
        self.SeriesInstanceUID = pydicom.uid.generate_uid()
        self.SeriesNumber = random.randint(0,1e3)
        self.SOPClassUID = self.file_meta.MediaStorageSOPClassUID 
        self.SOPInstanceUID = self.file_meta.MediaStorageSOPInstanceUID 
        self.StructureSetDate = dt.strftime('%Y%m%d')
        self.StructureSetDescription = 'RTSTRUCT generated by DICOM package'
        self.StructureSetLabel = 'test'
        self.StructureSetTime = dt.strftime('%H%M%S.%f')
        
        return None