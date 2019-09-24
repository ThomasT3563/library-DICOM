import pydicom

class StructureSetROI(pydicom.dataset.Dataset):
    """
        Generates a StructureSetROI item to append in a 
        StructureSetROISequence
            - ROIGenerationAlgorithm
            - ROIName
            - ROINumber
            - ReferencedFrameOfReferenceUID
    """
    def __init__(self,
                 ROIGenerationAlgorithm='MANUAL',
                 ROIName='VOID',
                 ROINumber='0',
                 ReferencedFrameOfReferenceUID=''):
        
        super().__init__()
        
        self.ROIGenerationAlgorithm = ROIGenerationAlgorithm
        self.ROIName = ROIName
        self.ROINumber = ROINumber
        self.ReferencedFrameOfReferenceUID = ReferencedFrameOfReferenceUID
        
if __name__=='main':
    StructureSetROI()