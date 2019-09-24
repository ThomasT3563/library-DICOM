import pydicom

class PredecessorStructureSet(pydicom.dataset.Dataset):
    """
        This element is intended to be only optionnal
        
        Generates a PredecessorStructureSet item to append in a 
        PredecessorStructureSetSequence
            - Referenced SOP Class UID
            - Referenced SOP Instance UID
    """
    def __init__(self,
                 ReferencedSOPClassUID='',
                 ReferencedSOPInstanceUID=''):
        
        super().__init__()
        
        self.ReferencedSOPClassUID = ReferencedSOPClassUID
        self.ReferencedSOPInstanceUID = ReferencedSOPInstanceUID
        
if __name__=='main':
    PredecessorStructureSet()
