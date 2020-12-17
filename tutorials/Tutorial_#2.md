# In this Notebook  : 
We are going define classes to have a cleaner implementationa and do more complex tasks with the plots.
We will have a usefull use of the interaction.


```python
import matplotlib.pyplot as plt
import numpy as np
```

###  Class
I define a **class** so that the interaction is done best. doing so, we will be able to **store information**, and do backward actions one which we've done before.

I just declare the class, **initialize** it and define a call **function**. The **arguemnt** of the class are just blank figure and axes (in this notebook I use **subplots** instead of just figure, which allows more complex plots. (You just need to know that the figure is the canvas, and the axes are plots inside the canvas.)
During the initialisation, we make the figure and the axes a property of the class (`self`), we plot the random plot we used before (see tutorial 1), and we create a empty list, which will store the points we add while clicking.

The call funciton will be called each time we click : it's the equivalent of the function we created in tutorial 1 defining what we wanted to do while interacting. 

Here, I kept the drawing color interaction. But now that we can store the added points, the left click (or `ctr` click) will **remove the latest drown point** ! 

# Try it :


```python
%matplotlib notebook
class Interact:
    def __init__(self, fig, ax):
        self.ax = ax
        fig.canvas.mpl_connect('button_press_event', self)
        self.plot = plt.scatter(np.random.uniform(0, 10, 10), np.random.uniform(0, 10, 10))
        self.points = []

    def __call__(self, event):
        
            click_x = event.xdata
            click_y = event.ydata
            plt.title(f"I'm clicking on : (x, y) = ({click_x:.2f}, {click_y:.2f})")
            if (click_x > plt.xlim()[1]/2):
                color = 'red'
            else:
                color = 'blue'
            if event.button == 1:
                marker = 'o'
                self.points.append(self.ax.scatter(event.xdata, event.ydata, marker=marker, c=color))
            if event.button == 3:
                try:
                    self.points[-1].remove()
                    self.points.pop(len(self.points)-1)

                except IndexError:
                    plt.title("Ooops, you want to remove a point but \n there is no more !")


fig, ax = plt.subplots(figsize=(5, 5))
interact = Interact(fig, ax)

```

### Cool right ?

Ok, now that we have the basis and a clean way to work, let's have our first usefull interactive plot.

I propose to have a 2D plot of a catalogue (let's play with galaxies, but you can use any table with more than 2 columns). The idea is to have a scatter plots of two of the parameters, and to print the values of the other when clicking to the point of interest.

First, lets import the data : 


```python
cat = np.load('../data/Galaxy_catalogue.npy', allow_pickle=True).item()
```

The catalogue is now stored in `cat`. It's a simple dictionnary containing 300 galaxies. For each galaxy(rows), we have 4 parameters (columns) : the magnitude `mag`, the radius and the ellipticity.

To do what we want, we need first a function to recognize the data point we are clicking. Don't look to much at the function, it's not the point of the notebook. Just for you to know, the function return the data point the closest to any position on a graph. When we will be clicking, we will not necessarly need to click exactly on the point, this function will do the job for us. In addition, it returns the index of the corresponding data point, so we can print the other parameters of the galaxy


```python
def find_closest_point(coords, cat, p1, p2):
    searching_for = np.zeros((1, 2))
    searching_for[0, 0] = coords[0]
    searching_for[0, 1] = coords[1]

    searching_in = np.zeros(((len(cat[next(iter(cat))]), 2)))
    searching_in[:, 0] = cat[p1]
    searching_in[:, 1] = cat[p2]
    _, match_index = KDTree(searching_in).query(searching_for)
    closestx, closesty = searching_in[match_index][0]
    return match_index[0], closestx, closesty
```

# New Interaction !
Well let's do it ! The initialisation plot the radii of the galaxies wrt to their magnitude. Each time you'll click on the plot, the closest corresponding galaxy will be found, and its ellipticity will be printed !

# Try it :


```python
%matplotlib notebook
from scipy.spatial import KDTree

class Explore_catalogue:
    def __init__(self, fig, ax, cat, param1='mag', param2='radius', param3='ellipticity'):
        self.ax = ax
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.cat = cat
        fig.canvas.mpl_connect('button_press_event', self)
        ax.scatter(cat[param1], cat[param2])

    def __call__(self, event):
        if event.button == 1:
            click_x = event.xdata
            click_y = event.ydata
            match_index, closest_x, closest_y = find_closest_point((click_x, click_y), self.cat, self.param1, self.param2)
            self.ax.set_title(f"clicked point : ({click_x:.2f}, {click_y:.2f}) \n "+
                              f"closest point : ({closest_x:.2f}, {closest_y:.2f}) \n"+
                             f"corresponding ellipticity:{cat[self.param3][match_index]:.2f}")
            
fig, ax = plt.subplots(figsize=(5, 5))
interact = Explore_catalogue(fig, ax, cat)

```

# Can be useful while exploring catalogs right ?
Well, of course you could have colorcoded the ellipitcity, but you can always do that and use the interaction to print a 4th parameter !

Let's add a cool behavior : I want to plot the galaxy of the clicked point next to the scatter plot. Here I'll just use a really toy (and dirty)model to create ''galaxies.....'' parameterized by the magnitude, the radius and ellipticity. What can be cool, with exactly the same code, is to show the images if you have the corresponfing galaxies to your catalogue !

Final thing : If you left click anywhere in the plot, it will create a new galaxy with the clicked mag and radius, and a random ellipticity.

# Try it :


```python
def gaussian_model(mag, rad, ell):
    rad = rad/2
    x, y = np.meshgrid(np.linspace(-32, 32, 64), np.linspace(-32, 32 ,64)) 
    dst = np.sqrt(x*x+y*y) 
    sigma = rad/2
    muu = 0
    
    galaxy = np.exp(-( (dst-muu)**2 / ( 2.0 * sigma**2 ) ) ) * 10**(-0.4*(mag-23.5))
    
    y, x = np.ogrid[-32:32, -32:32]
    mask = (x*x)/(rad) + (y*y)/(rad*(1-ell)) > rad
    
    galaxy[mask] = 0
    galaxy += np.random.normal(0, 0.1, (64, 64))
    return(galaxy)
```


```python
%matplotlib notebook
from scipy.spatial import KDTree

class Explore_catalogue:
    def __init__(self, fig, ax, cat, param1='mag', param2='radius', param3='ellipticity'):
        self.plot_cat = ax[0]
        self.new_galaxies = []
        self.image = ax[1]
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.cat = cat
        fig.canvas.mpl_connect('button_press_event', self)
        self.plot_cat.scatter(cat[param1], cat[param2])

    def __call__(self, event):
        click_x = event.xdata
        click_y = event.ydata
        
        if event.button == 1:
            match_index, closest_x, closest_y = find_closest_point((click_x, click_y), self.cat, self.param1, self.param2)
            self.plot_cat.set_title(f"clicked point : ({click_x:.2f}, ({click_y:.2f}) \n "+
                              f"closest point : ({closest_x:.2f}, {closest_y:.2f}) \n"+
                             f"corresponding ellipticity:{cat[self.param3][match_index]:.2f}")
            self.image.imshow(gaussian_model(self.cat['mag'][match_index], self.cat['radius'][match_index], self.cat['ellipticity'][match_index]))
        
        if event.button == 3:
            self.new_galaxies.append(self.plot_cat.scatter(event.xdata, event.ydata, marker='*', c='red'))
            self.plot_cat.set_title(f"new galaxy : ({click_x:.2f}, ({click_y:.2f}) \n")
            self.image.imshow(gaussian_model(click_x, click_y, np.random.uniform(0,1)))

fig, ax = plt.subplots(1, 2, figsize=(7, 3))
interact = Explore_catalogue(fig, ax, cat)

```


```python

```


```python

```
