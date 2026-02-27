# 3-DOF Planar Arm Interactive Plot
# Requirements:
# l1 = 12.5, l2 = 10.5, l3 = 17.5
# Theta measured from horizontal (0 degree along +x axis)
# Sliders + Textboxes for degree input

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox

# Link lengths
l1 = 12.5
l2 = 10.5
l3 = 17.5

# Forward Kinematics
def forward_kinematics(theta1, theta2, theta3):
    t1 = np.deg2rad(theta1)
    t2 = np.deg2rad(theta2)
    t3 = np.deg2rad(theta3)
    
    x1 = l1 * np.cos(t1)
    y1 = l1 * np.sin(t1)
    
    x2 = x1 + l2 * np.cos(t1 + t2)
    y2 = y1 + l2 * np.sin(t1 + t2)
    
    x3 = x2 + l3 * np.cos(t1 + t2 + t3)
    y3 = y2 + l3 * np.sin(t1 + t2 + t3)
    
    return [0, x1, x2, x3], [0, y1, y2, y3]

# Initial angles
theta1_init = 0
theta2_init = 0
theta3_init = 0

# Create figure
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.35)

# Initial plot
x, y = forward_kinematics(theta1_init, theta2_init, theta3_init)
arm_line, = ax.plot(x, y, marker='o')

ax.set_xlim(-45, 45)
ax.set_ylim(-45, 45)
ax.set_aspect('equal', 'box')
ax.set_title("3-DOF Planar Arm (Theta from Horizontal)")
ax.grid(True)

# Slider axes
ax_theta1 = plt.axes([0.15, 0.25, 0.7, 0.03])
ax_theta2 = plt.axes([0.15, 0.20, 0.7, 0.03])
ax_theta3 = plt.axes([0.15, 0.15, 0.7, 0.03])

slider_theta1 = Slider(ax_theta1, 'Theta1', -180, 180, valinit=theta1_init)
slider_theta2 = Slider(ax_theta2, 'Theta2', -180, 180, valinit=theta2_init)
slider_theta3 = Slider(ax_theta3, 'Theta3', -180, 180, valinit=theta3_init)

# Textbox axes
ax_box1 = plt.axes([0.15, 0.08, 0.15, 0.04])
ax_box2 = plt.axes([0.40, 0.08, 0.15, 0.04])
ax_box3 = plt.axes([0.65, 0.08, 0.15, 0.04])

box1 = TextBox(ax_box1, 'T1', initial=str(theta1_init))
box2 = TextBox(ax_box2, 'T2', initial=str(theta2_init))
box3 = TextBox(ax_box3, 'T3', initial=str(theta3_init))

# Update function
def update(val):
    t1 = slider_theta1.val
    t2 = slider_theta2.val
    t3 = slider_theta3.val
    
    x, y = forward_kinematics(t1, t2, t3)
    arm_line.set_data(x, y)
    
    box1.set_val(str(round(t1, 2)))
    box2.set_val(str(round(t2, 2)))
    box3.set_val(str(round(t3, 2)))
    
    fig.canvas.draw_idle()

slider_theta1.on_changed(update)
slider_theta2.on_changed(update)
slider_theta3.on_changed(update)

# Textbox submit function
def submit_theta1(text):
    slider_theta1.set_val(float(text))

def submit_theta2(text):
    slider_theta2.set_val(float(text))

def submit_theta3(text):
    slider_theta3.set_val(float(text))

box1.on_submit(submit_theta1)
box2.on_submit(submit_theta2)
box3.on_submit(submit_theta3)

plt.show()
