import pydicom

class ROIContour(pydicom.dataset.Dataset):
    """
        Generates an empty ROIContour item to append in a 
        ROIContourSequence
            - ContourSequence
            - ROIDisplayColor
            - ReferencedROINumber
            
        Takes as input:
            - list_ContourData : list of length nb_contour of 
                Contour Data element containing [x,y,z] nb_points times
            - list_SOPInstanceUID : list of length nb_contour of slice 
                numbers
    """
    
    def __init__(self,
                 list_ContourData=[[1.0,1.0,1.0],],   #important
                 list_SOPInstanceUID=[''],            #important
                 ReferencedSOPClassUID='1.2.840.10008.5.1.4.1.1.2', # CT by default
                 ROIDisplayColor=['255', '0', '0'],
                 ReferencedROINumber='0'):
        super().__init__()
        
        # creation of a ContourSequence
        self.ContourSequence = self.create_ContourSequence(
                                        list_ContourData=list_ContourData,
                                        list_SOPInstanceUID=list_SOPInstanceUID,
                                        ReferencedSOPClassUID=ReferencedSOPClassUID)
        
        self.ROIDisplayColor = ROIDisplayColor
        self.ReferencedROINumber = ReferencedROINumber

    def create_ContourSequence(self,
                               list_ContourData=[[1.0,1.0,1.0],],
                               list_SOPInstanceUID=[''],
                               ContourGeometricType='CLOSED_PLANAR',
                               ReferencedSOPClassUID=''):
        """
            Generates a ContourSequence item
                - ContourData
                - ContourGeometricType
                - ContourImageSequence
                - NumberOfContourPoints
        """
        #assert number of contour
        assert (len(list_SOPInstanceUID)==len(list_ContourData)),"UIDs number different than number of contour: %s != %s" % (len(list_SOPInstanceUID),len(list_ContourData))
        
        ContourSequence = pydicom.sequence.Sequence()

        # append Contour items to the Sequence
        for ContourData,SOPInstanceUID in zip(list_ContourData,list_SOPInstanceUID):
            
            dataset = pydicom.dataset.Dataset()
            dataset.ContourData = ContourData
            dataset.ContourGeometricType = ContourGeometricType
            
             # creation of a ContourImageSequence
            dataset.ContourImageSequence = self.create_ContourImageSequence(
                        ReferencedSOPInstanceUID = SOPInstanceUID,
                        ReferencedSOPClassUID    = ReferencedSOPClassUID)
            
            dataset.NumberOfContourPoints = len(ContourData)/3
            #assert integer number of contour points
            assert(float(dataset.NumberOfContourPoints)==int(dataset.NumberOfContourPoints)),"Number of point is not an integer: %s" % str(dataset.NumberOfContourPoints)
            
            ContourSequence.append(dataset)
            
        return ContourSequence
    
    def create_ContourImageSequence(self,
                                    ReferencedSOPInstanceUID='',
                                    ReferencedSOPClassUID=''):
        """
            Generates an empty ContourImageSequence item
                - ReferencedSOPClassUID
                - ReferencedSOPInstanceUID
        """
        ContourImageSequence = pydicom.sequence.Sequence()
        
        dataset = pydicom.dataset.Dataset()
        dataset.ReferencedSOPClassUID = ReferencedSOPClassUID
        dataset.ReferencedSOPInstanceUID = ReferencedSOPInstanceUID

        ContourImageSequence.append(dataset)
        return ContourImageSequence


if __name__=="__main__":
    ROIContour()
    