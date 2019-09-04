# WORK IN PROGRESS
# Child classes to implement to realise further operations on Dicoms
class DCM_CT(DCM_item):
    """
        Child class 2
        WIP
    """
    def __init__(self,filename,dcm_item,dcm_tags):
        
        super().__init__(filename,dcm_tags)
        
        #self.tags = dcm_item.dir()
        #print('dcm img defined')  
        
    def getPixelMatrix(self):
        """
            WIP
        """
        pass
    
class DCM_PET(DCM_item):
    """
        Child class 3
        WIP
    """
    def __init__(self,filename,dcm_item,dcm_tags):
        
        super().__init__(filename,dcm_tags)
        
        #self.tags = dcm_item.dir()
        #print('dcm img defined')  
        
    def getPixelMatrix(self):
        """
            WIP
        """
        pass