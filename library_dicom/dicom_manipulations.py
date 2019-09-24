#!/usr/bin/env python
# coding: utf-8


import numpy as np
import cv2

def convert_MASK_to_ROI(mask,
                        label_numbers,
                        list_SOPInstanceUID,
                        dicom_spacing,
                        dicom_origin):
    """
        Convert a mask to a list of ROI contour and SOPInstanceUID
        By default label 0 is considered as Background and is ignored
    
        Parameters:
            - mask
            - list_SOPInstanceUID
            - label_numbers
            - dicom_spacing
            - dicom_origin
                
        Return list of ROIs, list of UID:
            - list of ROI
                 list of contours of a same ROI
                    list of x,y,z points of a same contour
            - list of UID
                 list of SOPInstanceUID
    """
    list_ROI = []
    list_UID = []

    x0,y0,z0 = dicom_origin
    dx,dy,dz = dicom_spacing
    
    # for each label a.k.a each ROI to extract
    for label_nb in label_numbers:
        
        contours_ROI = []
        SOPInstanceUID_ROI = []
        binary_mask = np.array(mask==label_nb,dtype=np.uint8)
        
        # for each slice of the mask
        for s in range(mask.shape[2]):
            
            contours, _ = cv2.findContours(binary_mask[:,:,s],cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        
            # if we are on a slice containing ROI parts
            if (contours!=[]):
                
                # loop over contours
                for contour in contours:
                    
                    # loop on every contour point
                    # ordered as succession of (x,y,z)
                    contour_points = []
                    for (x,y) in contour[:,0,:]:
                        contour_points.append(x0+x*dx)
                        contour_points.append(y0+y*dy)
                        contour_points.append(z0+s*dz)
                    
                    # gather contour coordinates and slice UID for 
                    #      each contour
                    contours_ROI.append(contour_points)
                    SOPInstanceUID_ROI.append(list_SOPInstanceUID[s])
        
        list_ROI.append(contours_ROI)
        list_UID.append(SOPInstanceUID_ROI)
        
    return list_ROI,list_UID  
