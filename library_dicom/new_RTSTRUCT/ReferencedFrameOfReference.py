import pydicom

class ReferencedFrameOfReference(pydicom.dataset.Dataset):
    """
        This element is intended to be only optional (actually in specific software it is not Eclipse)
        
        Generates a ReferencedFrameOfReference item to append in a 
        ReferencedFrameOfReferenceSequence
            - FrameOfReferenceUID
            - RTReferencedStudySequence (big)
                - StudyInstanceUID
                - SeriesInstanceUID
    """
    def __init__(self,
                 FrameOfReferenceUID,
                 StudyInstanceUID,
                 SeriesInstanceUID,
                 ReferencedSOPClassUID,
                 list_SOPInstanceUID):
        
        super().__init__()
        
        self.FrameOfReferenceUID = FrameOfReferenceUID
        
        self.RTReferencedStudySequence = pydicom.sequence.Sequence()
        self.RTReferencedStudySequence.append(self.create_RTReferencedStudy(
                                                        StudyInstanceUID,
                                                        SeriesInstanceUID,
                                                        ReferencedSOPClassUID,
                                                        list_SOPInstanceUID)) #only one item
        
    def create_RTReferencedStudy(self,StudyInstanceUID,SeriesInstanceUID,ReferencedSOPClassUID,list_SOPInstanceUID):
        """
            Generates a RTReferencedStudy item
                - RTReferencedSeriesSequence (big)
                - ReferencedSOPClassUID
                - ReferencedSOPInstanceUID
        """
        RTReferencedStudy = pydicom.dataset.Dataset()
        
        RTReferencedStudy.ReferencedSOPClassUID = '1.2.840.10008.3.1.2.3.2' #Study Management SOP Class (Retired)
        RTReferencedStudy.ReferencedSOPInstanceUID = StudyInstanceUID # Study SOP UID
        RTReferencedStudy.RTReferencedSeriesSequence = pydicom.sequence.Sequence()
        RTReferencedStudy.RTReferencedSeriesSequence.append(self.create_RTReferencedSeries(
                                                                    SeriesInstanceUID,
                                                                    ReferencedSOPClassUID,
                                                                    list_SOPInstanceUID)) #only one item
        
        return RTReferencedStudy
    
    def create_RTReferencedSeries(self,SeriesInstanceUID,ReferencedSOPClassUID,list_SOPInstanceUID):
        """
            Generates a RTReferencedSeries item
                - SeriesInstanceUID
                - ContourImageSequence
        """
        RTReferencedSeries = pydicom.dataset.Dataset()
        
        RTReferencedSeries.SeriesInstanceUID = SeriesInstanceUID # Series SOP UID
        RTReferencedSeries.ContourImageSequence = self.create_ContourImageSequence(ReferencedSOPClassUID,list_SOPInstanceUID)
        
        return RTReferencedSeries

    def create_ContourImageSequence(self,ReferencedSOPClassUID,list_SOPInstanceUID):
        
        ContourImageSequence = pydicom.sequence.Sequence()
        
        for SOPInstanceUID in list_SOPInstanceUID:
            
            # iterative creation of ContourImage items
            ContourImage = pydicom.dataset.Dataset()
            ContourImage.ReferencedSOPClassUID = ReferencedSOPClassUID
            ContourImage.ReferencedSOPInstanceUID = SOPInstanceUID
            ContourImageSequence.append(ContourImage)
        
        return ContourImageSequence
        







