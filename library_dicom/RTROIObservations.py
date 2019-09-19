import pydicom

class RTROIObservations(pydicom.dataset.Dataset):
    """
        Generates a RTROIObservations item to append in a
        RTROIObservationsSequence
            - ObservationNumber
            - ROIObservationLabel
            - RTROIInterpretedType
            - ReferencedROINumber
    """
    def __init__(self,
                 ObservationNumber='0',
                 ReferencedROINumber='0',
                 ROIObservationLabel='VOID',
                 RTROIInterpretedType='ORGAN'):

        super().__init__()
        
        self.ObservationNumber = ObservationNumber
        self.ReferencedROINumber = ReferencedROINumber
        self.ROIObservationLabel = ROIObservationLabel
        self.RTROIInterpretedType = RTROIInterpretedType     
    
if __name__=='main':
    RTROIObservations()
    