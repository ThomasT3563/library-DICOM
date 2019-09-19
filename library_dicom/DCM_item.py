import pydicom
import random
import datetime

class DCM_item(object):
    """
        Superclass of every type of dicom items
    """
    def __init__(self,filename,tags,parameters):
        
        # WIP :check if filename is a .dcm file
        self.filename = filename
        
        self.heir_tags = tags
        
        # load dicom item and instantiate new randoms UIDs
        #      - new file_meta.MediaStorageSOPInstanceUID
        #             - new SOPInstanceUID
        #             - new InstanceCreationDate
        #             - new InstanceCreationTime
        #             - new InstanceNumber
        #      - new SeriesInstanceUID
        #             - new SeriesNumber
        self.rawfile = pydicom.read_file(filename)
        self.rawfile.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        self.rawfile.SOPInstanceUID = self.rawfile.file_meta.MediaStorageSOPInstanceUID
        dt = datetime.datetime.now()
        self.rawfile.InstanceCreationDate = dt.strftime('%Y%m%d')
        self.rawfile.InstanceCreationTime = dt.strftime('%H%M%S.%f')
        self.rawfile.InstanceNumber = '1'
        self.rawfile.SeriesInstanceUID = pydicom.uid.generate_uid()
        self.rawfile.SeriesNumber = random.randint(0,1e3)        
        
        self.list_SOPInstanceUID  = parameters.get('list_SOPInstanceUID')
        self.FrameOfReferenceUID  = parameters.get('FrameOfReferenceUID')
        self.ShapeImage           = parameters.get('ShapeImage')
        self.PixelSpacing         = parameters.get('PixelSpacing')
        self.ImagePositionPatient = parameters.get('ImagePositionPatient')

    def save(self,overwrite=True):
        """
            Save DICOM file
        """
        #WIP : add overwrite option
        self.rawfile.save_as(self.filename)