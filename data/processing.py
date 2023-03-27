#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 20:07:00 2023

@author: lion
"""
from typing import List, Mapping, Optional, Tuple, Union
import os
import numpy  as np
import json
import matplotlib.pyplot as plt
import quaternion

# Set the path of the directory to search in
dir_path = '/home/lion/Downloads'

locs =  []
# Search for .json files in the 'test' subdirectory, but not in any subdirectories of 'test'
for root, dirs, files in os.walk(dir_path):
    if os.path.basename(root) == 'test' and not any(d for d in dirs if os.path.join(root, d).startswith(os.path.join(root, 'test'))):
        for file in files:
            if file.endswith('.json'):
                print(os.path.join(root, file))
                locs.append(os.path.join(root, file)) 
    

raw_data = []    
for i in locs: 
    f = open(i)
    raw_data.append(json.load(f))
    
    
    
pro_data = [] 
for i in raw_data: 
    cordinate = []
    for ii in i[0]: 
        cordinate.append([ii["x"],ii["y"],ii["z"]])
    pro_data.append([np.array(cordinate), i[1]])
    
def plot_hand(joint_positions): 
    pass

#addapted from mediapipe framework. 

def plot_landmarks(landmark_list,
                   connections: List[Tuple[int, int]] ,
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
  plotted_landmarks = {}
  i = 0
  print(landmark_list)  

  for landmark in landmark_list:
    ax.scatter3D(
        xs=[-landmark[2]],
        ys=[landmark[0]],
        zs=[-landmark[1]],
        color= "red",
        linewidth=8)
    plotted_landmarks[i] = (-landmark[2], landmark[0], -landmark[1])
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
        print("hey ",start_idx )
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
    
adjecency_hand = [
    (0,1), #Thumb1
    (1,2), #Thumb2
    (2,3), #Thumb3
    (3,4), #Thumb4
    (0,5), # second refrece. determens rotation 
    (5,6),
    (6,7),
    (7,8),
    (0,9), #heuristic for global orientetion of the hand, i.e in world coordinates. other rotrations are in relation to that. (this should idealy be quaterion of rightHand, but only the piont 0 we get does not has orientation i,e need (-1,0))
    (9,10),
    (10,11),
    (11,12),
    (0,13),
    (13,14),
    (14,15),
    (15,16),
    (0,17),
    (17,18),
    (18,19),
    (19,20)    
    ]
addiational_visualisation = [
     #those are more for demonstration than they are for visualsiation they do not appear in the 3d model 
    (5,9),
    (9,13),
    (13,17)
    ]
def abs_alingment(data, charality): 
    pass  

    


def gen_local_quat(coords, adjecency): 
    # align hand to 3d grid. (0,5,9) Then calculate the delta vectors for the template, then calculate the quaterions from theire
    
    """ 
    Do alignment here
    """
    quaternions = []
    for connection in adjecency: 
        #print("hey", connection)
        start = connection[0]
        end  = connection[1]
        print(start, " ,", end)
        delta = coords[end] - coords[start] #vectors 
        quaternions.append(quaternion.from_rotation_vector(delta)) 

    return quaternions



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    