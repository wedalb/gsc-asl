#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 14:05:18 2023

Adjusted from https://github.com/google/mediapipe/tree/master/mediapipe
"""
import matplotlib.pyplot as plt
from typing import List, Mapping, Optional, Tuple, Union
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic
import numpy as np 
from scipy.spatial.transform import Rotation as R
#f = open("/home/lion/Downloads/bob.jpg")
marks =  []


def marks2np(landmarks): 
    xs =  []
    for landmark in landmarks.landmark: 
        xs.append([-landmark.z,landmark.x, -landmark.y])
        #ys.append(landmark.y)
        #zs.append(landmark.z)
    return np.array(xs)
    

def plot_landmarks(landmark_list,
                   connections: List[Tuple[int, int]],
                   elevation: int = 10,
                   azimuth: int = 10):
  """Plot the landmarks and the connections in matplotlib 3d.
  Args:
    landmark_list: A normalized landmark list proto message to be plotted.
    connections: A list of landmark index tuples that specifies how landmarks to
      be connected.
    landmark_drawing_spec: A DrawingSpec object that specifies the landmarks'
      drawing settings such as color and line thickness.
    connection_drawing_spec: A DrawingSpec object that specifies the
      connections' drawing settings such as color and line thickness.
    elevation: The elevation from which to view the plot.
    azimuth: the azimuth angle to rotate the plot.
  Raises:
    ValueError: If any connection contains an invalid landmark index.
  """
  if not landmark_list.any():
    return
  plt.figure(figsize=(10, 10))
  ax = plt.axes(projection='3d')
  ax.view_init(elev=elevation, azim=azimuth)
  
  # Set axis limits
  ax.set_xlim([-1, 1])
  ax.set_ylim([-1, 1])
  ax.set_zlim([-1, 1])
  
  plotted_landmarks = {}
  i = 0
  print(landmark_list.shape)  

  for landmark in landmark_list:
    ax.scatter3D(
        xs=[landmark[0]], #-2
        ys=[landmark[1]],  # 0 
        zs= [landmark[2]], # -1
        color= "red",
        linewidth=8)
    plotted_landmarks[i] = (landmark[0], landmark[1], landmark[2])
    i+=1
  if connections:
    num_landmarks = landmark_list.shape[0]
    # Draws the connections if the start and end landmarks are both visible.
    for connection in connections:
      #print("hey", connection)
      start_idx = connection[0]
      end_idx = connection[1]
      if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
        raise ValueError(f'Landmark index is out of range. Invalid connection '
                         f'from landmark #{start_idx} to landmark #{end_idx}.')
      if start_idx in plotted_landmarks and end_idx in plotted_landmarks:
        #print("hey ",start_idx )
        landmark_pair = [
            plotted_landmarks[start_idx], plotted_landmarks[end_idx]
        ]
        ax.plot3D(
            xs=[landmark_pair[0][0], landmark_pair[1][0]],
            ys=[landmark_pair[0][1], landmark_pair[1][1]],
            zs=[landmark_pair[0][2], landmark_pair[1][2]],
            color= "blue",
            linewidth=4)
  plt.show()    
  return ax

def add_coords(ax, pos, ori,quat= True): 
    quat and (mat := ori.as_matrix())
    if quat: 
        mat =np.eye(3)
        rot = R.align_vectors([[0,0,0],ori.as_quat()[:3]],[[0,0,0],mat[1]])[0]
        mat = rot.apply(mat)
        mat = ori.apply(mat)
        #mat[1] = ori.as_quat()[:3]
        
    not quat and (mat := ori)
    U,V,W = pos
    ax.quiver(*pos,*mat[0],color = "red")
    ax.quiver(*pos,*mat[1],color = "green")
    ax.quiver(*pos,*mat[2],color = "blue")

    
    quat and ax.quiver(*pos,*ori.as_rotvec()[:3],color = "purple")
# For static images: "/home/lion/Downloads/bob.jpg
IMAGE_FILES = ["/home/lion/Downloads/Remix.png"]
BG_COLOR = (192, 192, 192) # gray
with mp_holistic.Holistic(
    static_image_mode=True,
    model_complexity=2,
    enable_segmentation=True,
    refine_face_landmarks=True) as holistic:
  for idx, file in enumerate(IMAGE_FILES):
    image = cv2.imread(file)
    image_height, image_width, _ = image.shape
    # Convert the BGR image to RGB before processing.
    results = holistic.process(image)#cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if results.pose_landmarks:
      print(
          f'Nose coordinates: ('
          f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x * image_width}, '
          f'{results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y * image_height})'
      )

    annotated_image = image.copy()
    # Draw segmentation on the image.
    # To improve segmentation around boundaries, consider applying a joint
    # bilateral filter to "results.segmentation_mask" with "image".
    condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
    bg_image = np.zeros(image.shape, dtype=np.uint8)
    bg_image[:] = BG_COLOR
    annotated_image = np.where(condition, annotated_image, bg_image)
    # Draw pose, left and right hands, and face landmarks on the image.
    mp_drawing.draw_landmarks(
        annotated_image,
        results.face_landmarks,
        mp_holistic.FACEMESH_TESSELATION,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_tesselation_style())
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_holistic.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.
        get_default_pose_landmarks_style())
    
    cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)
    # Plot pose world landmarks.
    mp_drawing.plot_landmarks(
        results.pose_world_landmarks, mp_holistic.POSE_CONNECTIONS)
    marks = results.pose_world_landmarks
 

# For webcam input:
rest = 4 




"""
cap = cv2.VideoCapture(0)
with mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as holistic:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = holistic.process(image)
    rest = [results.pose_landmarks,results.left_hand_landmarks, results.right_hand_landmarks]


    # Draw landmark annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.left_hand_landmarks,
        mp_holistic.HAND_CONNECTIONS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_hand_connections_style())
    mp_drawing.draw_landmarks(
        image,
        results.right_hand_landmarks,
        mp_holistic.HAND_CONNECTIONS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_hand_connections_style())
    
    mp_drawing.draw_landmarks(
        image,
        results.face_landmarks,
        mp_holistic.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_contours_style())
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_holistic.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles
        .get_default_pose_landmarks_style())
    
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Holistic', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
"""

#plot_landmarks(marks2np(marks),mp_holistic.POSE_CONNECTIONS)


def calc_dihedral(u1, u2, u3, u4):
    """ Calculate dihedral angle method. From bioPython.PDB
    (uses np.array instead)
    """
    a1 = u2 - u1
    a2 = u3 - u2
    a3 = u4 - u3

    v1 = np.cross(a1, a2)
    v1 = v1 / (v1 * v1).sum(-1)**0.5
    v2 = np.cross(a2, a3)
    v2 = v2 / (v2 * v2).sum(-1)**0.5
    porm = np.sign((v1 * a3).sum(-1))
    rad = np.arccos((v1*v2).sum(-1) / ((v1**2).sum(-1) * (v2**2).sum(-1))**0.5)
    if not porm == 0:
        rad = rad * porm
    return rad , a2 , u2

def end_piece(u1, u2, u3):
    a2 = u3 - u2
    return a2 , u2



#Need mapping between skelton of animation and pose points, i.e. look-up table 
# with this table need to aerage out some pionts and ignore first 10 (face) pionts: 
# scale ? 
# normilized connection between piont one and two is  world roation. 
# go from source to local 
# dihedal can be rotation streght of the vector. 

wire_map = {
    
    "RightToeBase"   : [30],
    "RightToe_End"   : [32],
    "RightFoot"      : [28],
    "RightLeg"       : [26],
    "RightUpLeg"     : [24], 
    "Hips"           : [24,23],
    "LeftToeBase"    : [29],
    "LeftToe_End"    : [31],
    "LeftFoot"       : [27],
    "LeftLeg"        : [25],
    "LeftUpLeg"      : [23],
    "Neck"           : [12,11],
    "RightArm"       : [12], 
    "RightForeArm"   : [14], 
    "RightHand"      : [16], 
    "RightHandThumb1": [22], 
    "LeftArm"        : [11], 
    "LeftForeArm"    : [13], 
    "LeftHand"       : [15], 
    "LeftHandThumb1" : [21],
    "Head"           : [7,8]
    }
 #"RightShoulder" : [12] # schultern nicht angegeben . Extrapulation nicht sinnvoll 

wire_lookup = [
    "RightToeBase"   , 
    "RightToe_End"   ,
    "RightFoot"      ,
    "RightLeg"       ,
    "RightUpLeg"     , 
    "Hips"           ,
    "LeftToeBase"    ,
    "LeftToe_End"    ,
    "LeftFoot"       ,
    "LeftLeg"        ,
    "LeftUpLeg"      ,
    "Neck"           ,
    "RightArm"       , 
    "RightForeArm"   , 
    "RightHand"      , 
    "RightHandThumb1", 
    "LeftArm"        , 
    "LeftForeArm"    , 
    "LeftHand"       , 
    "LeftHandThumb1" ,
    "Head"
    ]
wl = wire_lookup
wire_topo = [
    (0,1),
    (1,2),
    (0,2),
    (2,3),
    (3,4),
    (6,7),
    (7,8),
    (6,8),
    (8,9),
    (9,10),
    (5,11),
    (11,12),
    (12,13),
    (13,14),
    (14,15),
    (11,16),
    (16,17),
    (17,18),
    (18,19),
    (11,20)
    ]
#given the mapping from 3d model to mediapipe output, produce a ed template that has same topography as model 
def mapping(landmarks, wire_map, wire_lookup) :
    wire_marks = []
    for key in wire_lookup:
        if len(wire_map[key]) == 1:
            wire_marks.append(landmarks[wire_map[key][0]])
        elif len(wire_map[key]) == 2:
            pos = landmarks[wire_map[key]]
            new_pos = np.average(pos, axis = 0)
            wire_marks.append(new_pos)
    
    return np.array(wire_marks)
land = marks2np(marks)

change_matrix = np.array([[0,1,0],[0,0,1],[1,0,0]]).T

land= land @ change_matrix
wm= mapping(land, wire_map, wire_lookup)
# given the the wireframe what are the local and global scalings, positions, and rotations. 

def get_trans(wm,wire_lookup,landmarks): 
    trans = {}
    #Hips
    di,vec,pos = calc_dihedral(wm[wl.index("LeftUpLeg")], wm[wl.index("Hips")], wm[wl.index("Neck")], wm[wl.index("LeftArm")])
    #vec = wires[ wire_lookup.index("Hips")] - wires[ wire_lookup.index("Neck")
    trans["Hips"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos}
    
    #Neck
    di,vec,pos = calc_dihedral(wm[wl.index("RightArm")], wm[wl.index("Neck")], wm[wl.index("Head")],landmarks[8] )
    trans["Neck"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #RightArm
    di,vec,pos = calc_dihedral(wm[wl.index("Neck")], wm[wl.index("RightArm")], wm[wl.index("RightForeArm")],wm[wl.index("RightHand")] )
    trans["RightArm"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
   
    #RightForeArm
    di,vec,pos = calc_dihedral(wm[wl.index("RightArm")], wm[wl.index("RightForeArm")], wm[wl.index("RightHand")],wm[wl.index("RightHandThumb1")] )
    trans["RightForeArm"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #RightHand
    vec,pos = end_piece(wm[wl.index("RightForeArm")], wm[wl.index("RightHand")],wm[wl.index("RightHandThumb1")] )
    trans["RightHand"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #LeftArm
    di,vec,pos = calc_dihedral(wm[wl.index("Neck")], wm[wl.index("LeftArm")], wm[wl.index("LeftForeArm")],wm[wl.index("LeftHand")] )
    trans["LeftArm"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
   
    #LeftForeArm
    di,vec,pos = calc_dihedral(wm[wl.index("LeftArm")], wm[wl.index("LeftForeArm")], wm[wl.index("LeftHand")],wm[wl.index("LeftHandThumb1")] )
    trans["LeftForeArm"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #LeftHand
    vec,pos = end_piece(wm[wl.index("LeftForeArm")], wm[wl.index("LeftHand")],wm[wl.index("LeftHandThumb1")] )
    trans["LeftHand"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
        
    #RightUpLeg
    di,vec,pos = calc_dihedral(wm[wl.index("Hips")], wm[wl.index("RightUpLeg")], wm[wl.index("RightLeg")],wm[wl.index("RightFoot")] )
    trans["RightUpLeg"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #RightLeg
    di,vec,pos = calc_dihedral(wm[wl.index("RightUpLeg")], wm[wl.index("RightLeg")], wm[wl.index("RightFoot")],wm[wl.index("RightToe_End")] )
    trans["RightLeg"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #RightFoot
    vec,pos = end_piece(wm[wl.index("RightLeg")], wm[wl.index("RightFoot")],wm[wl.index("RightToe_End")] )
    trans["RightFoot"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #LeftUpLeg
    di,vec,pos = calc_dihedral(wm[wl.index("Hips")], wm[wl.index("LeftUpLeg")], wm[wl.index("LeftLeg")],wm[wl.index("LeftFoot")] )
    trans["LeftUpLeg"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #LeftLeg
    di,vec,pos = calc_dihedral(wm[wl.index("LeftUpLeg")], wm[wl.index("LeftLeg")], wm[wl.index("LeftFoot")],wm[wl.index("LeftToe_End")] )
    trans["LeftLeg"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    
    #LeftFoot
    vec,pos = end_piece(wm[wl.index("LeftLeg")], wm[wl.index("LeftFoot")],wm[wl.index("LeftToe_End")] )
    trans["LeftFoot"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }

    #Head
    vec,pos = end_piece(wm[wl.index("Neck")], wm[wl.index("Head")],landmarks[8])
    trans["Head"] = {"Global" : vec, "Angle" : di, "Quat" : R.from_quat([vec[0], vec[1], vec[2], di]), "WPos": pos }
    return trans


trans = get_trans(wm, wire_lookup, land@ change_matrix)
ax = plot_landmarks(wm,wire_topo)
add_coords(ax, trans["Neck"]["WPos"], trans["Neck"]["Quat"])
add_coords(ax, trans["Hips"]["WPos"]- 0.4, np.eye(3), quat= False)

##save values
import json
def save (wires):
    DStyle = {}
    for keys in wires: 
        #print(keys)
        DStyle[keys] = {"Global" : list(wires[keys]["Global"]) , "Angle" : wires[keys]["Angle"], "Quat" : list(wires[keys]["Quat"].as_quat()) , "WPos": list(wires[keys]["WPos"]) }
    
    return  DStyle
bob = save(trans)

with open('position.json', 'w', encoding='utf-8') as f:
    json.dump(bob, f, ensure_ascii=False, indent=4)
    
    
def plot_wires(wire_marks,wire_topo):
    plot_landmarks(wire_marks,wire_topo)
#builds the wire frame, with the given Topologie and transfpormation, can build a wire frame. 
# mabey add capsule to it 
def built_wires(trans,base,element):
    pass