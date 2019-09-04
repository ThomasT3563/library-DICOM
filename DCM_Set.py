import pydicom
import numpy as np
import glob
import random
import time

from DICOM_package.DCM_RTSTRUCT import DCM_RTSTRUCT
from DICOM_package.new_RTSTRUCT_rawfile import new_RTSTRUCT_rawfile

class DCM_Set(object):
    """
        Classe wrapper of dcm directory
            - self.heir_tags is loaded into RTSTRUCT file
            - self.parameters is shared with RTSTRUCT class
    """
    def __init__(self,series_directory):
        
        self.directoryName=series_directory
        self.rtstruct = []
        self.list_SOPInstanceUID = []
        
        all_filenames = np.sort(glob.glob(self.directoryName+'/*.dcm'))
        #print(*all_filenames,sep='\n')
        
        # loop over files to get:
        #    - rtstruct files
        #    - SOPInstanceUID list
        rtstruct_filenames = []
        ct_filenames = []
        for filename in all_filenames:
            dcm = pydicom.dcmread(filename)
            if dcm.SOPClassUID=='1.2.840.10008.5.1.4.1.1.481.3': # if RTSTRUCT
                rtstruct_filenames.append(filename)
            elif dcm.SOPClassUID=='1.2.840.10008.5.1.4.1.1.2': # if CT
                ct_filenames.append(filename)
            else:
                # WIP : add other than CT
                print("\nModality %s not implemented" % str(dcm.SOPClassUID))
            
        # sort CT slices by image position to extract ordered uid and slice thickness
        self.slices = [pydicom.read_file(s) for s in ct_filenames]
        self.slices.sort(key=lambda x:int(x.ImagePositionPatient[2]))
        self.list_SOPInstanceUID = [s.SOPInstanceUID for s in self.slices]
        #print(*self.list_SOPInstanceUID,sep='\n')
        self.SliceThickness = self.getSliceThickness()

        with pydicom.dcmread(ct_filenames[0]) as dcm:
            # init self.heir_tags
            #          - tags from DICOM file that will be loaded into the RT file
            self.init_tags(dcm)   
            # informations and tags from DICOM that will be shared with RT file
            self.parameters = self.init_params(dcm)            

        # create rtstruct item if rtstruct_filenames is empty a.k.a is there is no rt
        if not rtstruct_filenames:
            filename = self.directoryName+"/RS.generated."+str(random.randint(1e6,9e6))+'.dcm'
            # generates empty new rtstruct
            new_rt = new_RTSTRUCT_rawfile(filename,self.heir_tags)
            new_rt.save_as(filename)
            # add filename to the list if rtstruct
            rtstruct_filenames.append(filename)
            print('Generated empty RTSTRUCT file: %s' % filename)
            
        # load rtstruct files as DCM_RTSTRUCT objects
        for rtstruct_filename in rtstruct_filenames:
            self.rtstruct.append(DCM_RTSTRUCT(rtstruct_filename,self.heir_tags,
                                              self.parameters))

    def getSliceThickness(self):
        """
            Gather distance between successive slices all over the scan
            Raise an error if the distance is not constant
        """
        #mean slice thickness in mm
        #real_SliceThickness = np.abs(self.slices[0].ImagePositionPatient[2]-self.slices[-1].ImagePositionPatient[2])/len(self.slices) 
        
        # get initial slice thickness
        initial_SliceThickness = np.abs(self.slices[0].ImagePositionPatient[2]-self.slices[1].ImagePositionPatient[2])
        
        for i in range(1,len(self.slices)-1):
            current_SliceThickness = np.abs(self.slices[i].ImagePositionPatient[2]-self.slices[i+1].ImagePositionPatient[2])
            if initial_SliceThickness!=current_SliceThickness:
                raise ValueError('Slice thickness is not constant: %s / %s' % (str(initial_SliceThickness),str(current_SliceThickness)))
        
        return initial_SliceThickness
    
    def getPixelData(self):
        """
            Compute and return pixel matrix of the whole CT scan
        """
        pixel_data = [s.pixel_array for s in self.slices]
        pixel_data = np.stack(pixel_data,axis=-1)
        return pixel_data
    
    
    def init_tags(self,dcm):
        """
            Initialization of shared tags with try
            Importance of tags :
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
        #assert tag are defined an unique time
        #assert(self.heir_tags is None),"self.heir_tags is already defined"

        # tags from DICOM file that will be loaded into the RT file
        self.heir_tags = {'AccessionNumber':None,
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
                          'StudyTime':None
                         }
        
        for tag in self.heir_tags.keys():
            try:
                self.heir_tags[tag] = dcm.get(tag)
            except AttributeError:
                print("AttributeError with tag: %s" % tag)
                pass
            except Exception:
                raise Exception
                
        return None
        
    def init_params(self,dcm):
        """
            Initialization of informations and tags that will be shared with RT file
            Importance of tags :
                - 
        """        
        shape_image = (dcm.Columns,dcm.Rows,len(self.list_SOPInstanceUID))

        # informations and tags from DICOM that will be shared with RT file
        parameters = {'list_SOPInstanceUID':self.list_SOPInstanceUID,
                      'FrameOfReferenceUID': dcm.FrameOfReferenceUID,
                      'ShapeImage':shape_image,
                      'PixelSpacing':dcm.PixelSpacing,
                      'ImagePositionPatient':dcm.ImagePositionPatient,
                      'SliceThickness':self.SliceThickness,
                      'RescaleSlope':dcm.RescaleSlope,
                      'RescaleIntercept':dcm.RescaleIntercept
                     }
                          
        return parameters
    
                         #'BitsAllocated':None,
                         #'BitsStored':None,
                         #'Columns':None,
                         #'ContentDate':None,
                         #'ContentTime':None,
                         #'ConvolutionKernel':None,
                         #'DataCollectionDiameter':None,
                         #'DistanceSourceToDetector':None,
                         #'DistanceSourceToPatient':None,
                         #'Exposure':None,
                         #'ExposureTime':None,
                         #'FilterType':None,
                         #'FocalSpots':None,
                         #'FrameOfReferenceUID':None,
                         #'GantryDetectorTilt':None,
                         #'GeneratorPower':None,
                         #'HighBit':None,
                         #'ImageOrientationPatient':None,
                         #'ImagePositionPatient':None,
                         #'ImageType':None,
                         #'InstitutionName':None,
                         #'KVP':None,
                         #'PatientPosition':None,
                         #'PhotometricInterpretation':None,
                         #'PixelData':None,
                         #'PixelRepresentation':None,
                         #'PixelSpacing':None,
                         #'PositionReferenceIndicator':None,
                         #'ReconstructionDiameter':None,
                         #'RescaleIntercept':None,
                         #'RescaleSlope':None,
                         #'RescaleType':None,
                         #'RotationDirection':None,
                         #'Rows':None,
                         #'SamplesPerPixel':None,
                         #'ScanOptions':None,
                         #'SeriesDate':None,
                         #'SeriesTime':None,
                         #'SliceLocation':None,
                         #'SliceThickness':None, #avoid using it
                         #'TableHeight':None,
                         #'WindowCenter':None,
                         #'WindowWidth':None,
                         #'XRayTubeCurrent':None,
