# # 3-DOF Planar Arm - Class Based Interactive Plot
# # Theta measured from horizontal (0° along +X axis)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox

# class Planar3DOFArm:
#     def __init__(self,t1= 0,t2=0,t3 = 0, l1=12.5, l2=10.5, l3=17.5):
#         self.l1 = l1
#         self.l2 = l2
#         self.l3 = l3
        
#         self.theta1 = t1
#         self.theta2 = t2
#         self.theta3 = t3
        
#         self._setup_plot()
#         self._setup_widgets()
#         self.update_plot()
#         plt.show()
    
#     def forward_kinematics(self):
#         t1 = np.deg2rad(self.theta1)
#         t2 = np.deg2rad(self.theta2)
#         t3 = np.deg2rad(self.theta3)
        
#         x1 = self.l1 * np.cos(t1)
#         y1 = self.l1 * np.sin(t1)
        
#         x2 = x1 + self.l2 * np.cos(t1 + t2)
#         y2 = y1 + self.l2 * np.sin(t1 + t2)
        
#         x3 = x2 + self.l3 * np.cos(t1 + t2 + t3)
#         y3 = y2 + self.l3 * np.sin(t1 + t2 + t3)
        
#         return [0, x1, x2, x3], [0, y1, y2, y3]
    
#     def _setup_plot(self):
#         self.fig, self.ax = plt.subplots()
#         plt.subplots_adjust(bottom=0.35)
        
#         self.arm_line, = self.ax.plot([], [], marker='o')
        
#         total_length = self.l1 + self.l2 + self.l3
#         self.ax.set_xlim(-total_length, total_length)
#         self.ax.set_ylim(-total_length, total_length)
#         self.ax.set_aspect('equal', 'box')
#         self.ax.set_title("3-DOF Planar Arm (Class Based)")
#         self.ax.grid(True)
    
#     def _setup_widgets(self):
#         ax_t1 = plt.axes([0.15, 0.25, 0.7, 0.03])
#         ax_t2 = plt.axes([0.15, 0.20, 0.7, 0.03])
#         ax_t3 = plt.axes([0.15, 0.15, 0.7, 0.03])
        
#         self.slider_t1 = Slider(ax_t1, 'Theta1', -180, 180, valinit=0)
#         self.slider_t2 = Slider(ax_t2, 'Theta2', -180, 180, valinit=0)
#         self.slider_t3 = Slider(ax_t3, 'Theta3', -180, 180, valinit=0)
        
#         ax_b1 = plt.axes([0.15, 0.08, 0.15, 0.04])
#         ax_b2 = plt.axes([0.40, 0.08, 0.15, 0.04])
#         ax_b3 = plt.axes([0.65, 0.08, 0.15, 0.04])
        
#         self.box1 = TextBox(ax_b1, 'T1', initial="0")
#         self.box2 = TextBox(ax_b2, 'T2', initial="0")
#         self.box3 = TextBox(ax_b3, 'T3', initial="0")
        
#         self.slider_t1.on_changed(self._slider_update)
#         self.slider_t2.on_changed(self._slider_update)
#         self.slider_t3.on_changed(self._slider_update)
        
#         self.box1.on_submit(lambda text: self._textbox_update(1, text))
#         self.box2.on_submit(lambda text: self._textbox_update(2, text))
#         self.box3.on_submit(lambda text: self._textbox_update(3, text))
    
#     def _slider_update(self, val):
#         self.theta1 = self.slider_t1.val
#         self.theta2 = self.slider_t2.val
#         self.theta3 = self.slider_t3.val
        
#         self.box1.set_val(str(round(self.theta1, 2)))
#         self.box2.set_val(str(round(self.theta2, 2)))
#         self.box3.set_val(str(round(self.theta3, 2)))
        
#         self.update_plot()
    
#     def _textbox_update(self, joint, text):
#         try:
#             value = float(text)
#         except:
#             return
        
#         if joint == 1:
#             self.slider_t1.set_val(value)
#         elif joint == 2:
#             self.slider_t2.set_val(value)
#         elif joint == 3:
#             self.slider_t3.set_val(value)
    
#     def update_plot(self):
#         x, y = self.forward_kinematics()
#         self.arm_line.set_data(x, y)
#         self.fig.canvas.draw_idle()



#     def set_angles(self, theta1, theta2, theta3):
#         self.theta1 = theta1
#         self.theta2 = theta2
#         self.theta3 = theta3

#         self.slider_t1.set_val(theta1)
#         self.slider_t2.set_val(theta2)
#         self.slider_t3.set_val(theta3)

#         self.update_plot()
class Planar3DOFArm:
    def __init__(self, t1=0, t2=0, t3=0, l1=12.5, l2=10.5, l3=17.5):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.theta1 = t1
        self.theta2 = t2
        self.theta3 = t3
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.35)
        total_length = self.l1 + self.l2 + self.l3
        self.ax.set_xlim(-total_length, total_length)
        self.ax.set_ylim(-total_length, total_length)
        self.ax.set_aspect('equal', 'box')
        self.ax.grid(True)
        self.arm_line, = self.ax.plot([], [], marker='o')
        self._setup_widgets()
        self.update_plot()
        plt.show()

    def forward_kinematics(self):
        t1 = np.deg2rad(self.theta1)
        t2 = np.deg2rad(self.theta2)
        t3 = np.deg2rad(self.theta3)
        x1 = self.l1 * np.cos(t1)
        y1 = self.l1 * np.sin(t1)
        x2 = x1 + self.l2 * np.cos(t1 + t2)
        y2 = y1 + self.l2 * np.sin(t1 + t2)
        x3 = x2 + self.l3 * np.cos(t1 + t2 + t3)
        y3 = y2 + self.l3 * np.sin(t1 + t2 + t3)
        return [0, x1, x2, x3], [0, y1, y2, y3]

    def _setup_widgets(self):
        ax_t1 = plt.axes([0.15, 0.25, 0.7, 0.03])
        ax_t2 = plt.axes([0.15, 0.20, 0.7, 0.03])
        ax_t3 = plt.axes([0.15, 0.15, 0.7, 0.03])
        self.slider_t1 = Slider(ax_t1, 'Theta1', -180, 180, valinit=self.theta1)
        self.slider_t2 = Slider(ax_t2, 'Theta2', -180, 180, valinit=self.theta2)
        self.slider_t3 = Slider(ax_t3, 'Theta3', -180, 180, valinit=self.theta3)
        ax_b1 = plt.axes([0.15, 0.08, 0.15, 0.04])
        ax_b2 = plt.axes([0.40, 0.08, 0.15, 0.04])
        ax_b3 = plt.axes([0.65, 0.08, 0.15, 0.04])
        self.box1 = TextBox(ax_b1, 'T1', initial=str(self.theta1))
        self.box2 = TextBox(ax_b2, 'T2', initial=str(self.theta2))
        self.box3 = TextBox(ax_b3, 'T3', initial=str(self.theta3))
        self.slider_t1.on_changed(self._slider_update)
        self.slider_t2.on_changed(self._slider_update)
        self.slider_t3.on_changed(self._slider_update)
        self.box1.on_submit(lambda text: self._textbox_update(1, text))
        self.box2.on_submit(lambda text: self._textbox_update(2, text))
        self.box3.on_submit(lambda text: self._textbox_update(3, text))

    def _slider_update(self, val):
        self.theta1 = self.slider_t1.val
        self.theta2 = self.slider_t2.val
        self.theta3 = self.slider_t3.val
        self.box1.set_val(str(round(self.theta1, 2)))
        self.box2.set_val(str(round(self.theta2, 2)))
        self.box3.set_val(str(round(self.theta3, 2)))
        self.update_plot()

    def _textbox_update(self, joint, text):
        try:
            value = float(text)
        except:
            return
        if joint == 1:
            self.slider_t1.set_val(value)
        elif joint == 2:
            self.slider_t2.set_val(value)
        elif joint == 3:
            self.slider_t3.set_val(value)

    def update_plot(self):
        x, y = self.forward_kinematics()
        self.arm_line.set_data(x, y)
        self.fig.canvas.draw_idle()

    def set_angles(self, theta1, theta2, theta3, steps=50, delay=0.01):
        t1_start, t2_start, t3_start = self.theta1, self.theta2, self.theta3
        for i in range(1, steps + 1):
            self.theta1 = t1_start + (theta1 - t1_start) * i / steps
            self.theta2 = t2_start + (theta2 - t2_start) * i / steps
            self.theta3 = t3_start + (theta3 - t3_start) * i / steps
            self.slider_t1.set_val(self.theta1)
            self.slider_t2.set_val(self.theta2)
            self.slider_t3.set_val(self.theta3)
            self.update_plot()
            plt.pause(delay)