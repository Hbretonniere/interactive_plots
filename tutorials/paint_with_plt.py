'''
author : hbretonniere

This script is a paint like interactive plot to produce pixel art
You will have a canvas on the left, and a color on the right. By left clicking on the color of the palette,
you will select the color.

Now, click on the canvas : this will paint the color on the clicked pixel.

If you right click, it will save the image as a png !

'''

from math import ceil
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import matplotlib

# matplotlib.use("TkAgg")


class pixel_art:
    def __init__(
        self,
        fig,
        gs,
        size=15
    ):


        self.size = size
        self.latest_pix = []

        # Create the canvas plot where we're going to draw
        self.canvas = fig.add_subplot(gs[0])
        self.canvas.set_title('Left click to paint with the selected color. \n Right click (or ctrl click) to save', fontsize=7)
        self.canvas.set_xticks(np.arange(self.size))
        self.canvas.set_yticks(np.arange(self.size))
        self.canvas.set_xticklabels([""]*self.size)  # remove the ticks labels
        self.canvas.set_yticklabels([""]*self.size)  # remove the ticks labels

        # Create the blanck image to plot on the canvas
        self.image = np.zeros((self.size, self.size, 3)) + (255, 255, 255)
        self.image = self.image.astype(np.uint8)
        
        # Plot the blank image
        self.canvas.set_aspect('equal')
        self.canvas.imshow(self.image, vmin=0, vmax=9, extent=[-1, self.size-1, -1, self.size-1], origin='lower')
        self.canvas.grid()
        
        # Create the color palette plot
        self.show_palette = fig.add_subplot(gs[1])
        self.show_palette.set_title('Left click on the color to select it.', fontsize=7)
        self.show_palette.set_xticks(np.arange(3))
        self.show_palette.set_yticks(np.arange(3))
        self.show_palette.set_xticklabels([""]*3)
        self.show_palette.set_yticklabels([""]*3)
        
        # Create the color palette to plot on the palette plot
        self.palette = np.asarray([[255, 0, 0], [0, 255, 0], [0, 0, 255],
                                  [253, 173, 11], [125, 28, 187], [28, 187, 183],
                                  [233, 249, 35], [0, 0, 0], [255, 255, 255]])
        
        self.palette = self.palette.reshape(3, 3, 3)
        # Plot the palette
        self.show_palette.imshow(self.palette, vmin=0, vmax=9, extent=[-1, 2, -1, 2], origin='lower')

        # Link the action to the plot
        fig.canvas.mpl_connect('button_press_event', self)
        
        # intitalise the color to 0
        self.color = 0

    def __call__(self, event):
        
        click_x = event.xdata
        click_y = event.ydata
        
        # get the subplots we're clicking on (canvas or palette)
        ax = event.inaxes
        

        if event.button == 1:  # if left click

            if ax == self.show_palette: # if you're on the palette, select the corresponding color
                
                self.color = self.palette[ceil(click_y), ceil(click_x)]
                plt.suptitle(" ", x=0.5, y=0.9)

            else:  # if you're on the canvas, draw
                self.image[ceil(click_y), ceil(click_x)] = self.color
                self.canvas.imshow(self.image, vmin=0, vmax=9,
                                    extent=[-1, self.size-1, -1, self.size-1], origin='lower')
                plt.suptitle(" ", x=0.5, y=0.92)
                self.latest_pix.append([ceil(click_y), ceil(click_x)])
                plt.draw()  # update

        # if right click, save the image
        if event.button == 3:
            im_to_save = np.copy(self.image)  # We need to inver the R and B channels
            im_to_save[:, :, 0] = self.image[:, :, 2]  # B to R
            im_to_save[:, :, 2] = self.image[:, :, 0]  # R to B
            im_to_save = np.flip(np.flip(im_to_save), axis=1)  # We need to flip horizontaly and verticaly
            im = Image.fromarray(im_to_save)
            im.save("masterpiece.png")
            plt.suptitle("Image saved !", x=0.5, y=0.92, color='red')
            plt.draw()

fig = plt.figure(figsize=(5, 5), constrained_layout=True)
gs = fig.add_gridspec(ncols=2, nrows=1, width_ratios=[5, 3])
pixel_art(fig, gs)
plt.show()
