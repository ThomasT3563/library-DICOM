import pydicom

from DICOM_package.DCM_item import DCM_item
from DICOM_package.ROIContour import ROIContour
from DICOM_package.RTROIObservations import RTROIObservations
from DICOM_package.StructureSetROI import StructureSetROI

class DCM_RTSTRUCT(DCM_item):
    """
        Child class of dicom item
    """
    def __init__(self,filename,heir_tags,parameters):
        
        # Initialization of parent class:
        #       - self.filename
        #       - self.heir_tags
        #       - self.rawfile
        #       - self.list_SOPInstanceUID
        #       - self.ShapeImage
        #       - self.PixelSpacing
        #
        # + generation of new random UIDs
        super().__init__(filename,heir_tags,parameters)
        
        self.rt_tags = self.rawfile.dir()
        # WIP : mise a jour des rt tags
        #self.ApprovalStatus = 'APPROVED'
        #self.DeviceSerialNumber = '950586737223'
            #self.ROIContourSequence = None
            #self.RTROIObservationsSequence = None
        #self.ReferencedFrameOfReferenceSequence = None #LONG, Seq 1
        #self.ReviewDate = '20171212'
        #self.ReviewTime = '095106'
        #self.ReviewerName = 'cm'
        #self.StructureSetDate = '20171212'
        #self.StructureSetDescription = '|AcurosXB-13.5'
        #self.StructureSetLabel = 'TDM301117_AVG6'
            #self.StructureSetROISequence = None
        #self.StructureSetTime = (095106.180000)
        
        # update ROIs defined
        (self.ROI_defined, self.ROI_available) = self.extractROIlist()
        (self.ObservationNumbers,self.ReferenceROINumbers) = self.extractROInumbers()

        #print('RTSTRUCT loaded: %s' % filename)
    
    def extractROIlist(self):
        """
            Extract list of ROI defined and available 
                defined : ROI existing in StructureSetROISequence
                available : ROI with ContourSequence
        """
        rtstruct = self.rawfile
        # check ROI defined != ROI with actual contour
        ROI_defined = [roitr.ROIName for roitr in rtstruct.StructureSetROISequence]
        ROI_available = [label_name for label_name in ROI_defined if 'ContourSequence' in rtstruct.ROIContourSequence[ROI_defined.index(label_name)]] 
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
    
    def extractROIContour(self,index=None,name=None):
        """
            From a ROI of the RTSTRUCT, extract and return list of
            contour points and SOPInstanceUID related
        """
        if (index is None):
            if (name is None):
                print("Please specify a ROI to extract")
            else:
                index = self.ROI_defined.index(name)
                
        #print("    - extraction of: ROI %s of index %s"%(self.ROI_defined[index],index))
        
        list_ContourData = []
        list_SOPInstanceUID = []
        for Contour in self.rawfile.ROIContourSequence[index].ContourSequence:
            list_ContourData.append(Contour.ContourData)
            list_SOPInstanceUID.append(Contour.ContourImageSequence[0].ReferencedSOPInstanceUID)

        return (list_ContourData,list_SOPInstanceUID)
    
    def deleteROI(self,index=None,name=None):
        """
            Delete a ROI of the RTSTRUCT
        """
        
        if (index is None):
            if (name is None):
                print("Please specify a ROI to remove")
            else:
                index = self.ROI_defined.index(name)
        
        #remove element index from ROI Sequences
        self.rawfile.RTROIObservationsSequence.pop(index)
        self.rawfile.ROIContourSequence.pop(index)
        self.rawfile.StructureSetROISequence.pop(index)
        
        print("ROI %s of index %s is removed" % (self.ROI_defined[index],index))
        
        # update ROIs defined
        (self.ROI_defined, self.ROI_available) = self.extractROIlist()
        (self.ObservationNumbers,self.ReferenceROINumbers) = self.extractROInumbers()
    
    def getROIinfos(self):
        for i in range(len(self.ROI_defined)):
            print("ObsNb: %s / RefNb: %s / ROI: %s" % 
                  (self.ObservationNumbers[i],self.ReferenceROINumbers[i],self.ROI_defined[i]))
    
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
        
        if ('RTROIObservationsSequence' in self.rt_tags) and ('ROIContourSequence' in self.rt_tags) and ('StructureSetROISequence' in self.rt_tags):
            
            # initialization of new Datasets
            new_RTROIObservations = self.create_RTROIObservations(
                ReferencedROINumber=ROI_number,
                ROIObservationLabel=ROI_name
            ) 
            new_ROIContour = self.create_ROIContour(
                list_ContourData=ROI_list_ContourData,
                list_SOPInstanceUID=ROI_list_SOPInstanceUID,
                ROIDisplayColor=ROI_Color,
                ReferencedROINumber=ROI_number
            ) 
            new_StructureSetROI = self.create_StructureSetROI(
                ROIGenerationAlgorithm='MANUAL',
                ROIName=ROI_name,
                ROINumber=ROI_number,
                FrameOfReferenceUID=ROI_FrameOfReferenceUID
            ) 

            # object to update when adding a ROI
            self.rawfile.RTROIObservationsSequence.append(new_RTROIObservations)
            self.rawfile.ROIContourSequence.append(new_ROIContour)
            self.rawfile.StructureSetROISequence.append(new_StructureSetROI)

            # update
            (self.ROI_defined, self.ROI_available) = self.extractROIlist()
            (self.ObservationNumbers,self.ReferenceROINumbers) = self.extractROInumbers()

        else:
            raise AssertionError('rtstruct element needs ROIContourSequence and RTROIObservationsSequence')
            
    def create_RTROIObservations(self,
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
            
        # possiblement à changer
        ObservationNumber = ReferencedROINumber
        
        new_RTROIObservations = RTROIObservations(
            ObservationNumber=ObservationNumber,
            ReferencedROINumber=ReferencedROINumber,
            ROIObservationLabel=ROIObservationLabel)
        return new_RTROIObservations
    
    def create_ROIContour(self,
                          list_ContourData=[[1.0,1.0,1.0],],
                          list_SOPInstanceUID=None,
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
            ROIDisplayColor=ROIDisplayColor,
            ReferencedROINumber=ReferencedROINumber)
        return new_ROIContour
    
    def create_StructureSetROI(self,
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