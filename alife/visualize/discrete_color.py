# Generate a color scheme by equal spacing along the color wheel. 
import numpy as np
import matplotlib.pyplot as plt

def test_scheme(colors,show=False,savefn='test_colorscheme.png'):
    fig = plt.figure()
    fig.set_size_inches(18.5,10.5)
    n = len(colors)
    xs = np.arange(n)
    ys = np.array([1 for _ in range(n)])
    plt.scatter(xs,ys,color=colors)
    if savefn is not None:
        plt.savefig(savefn,dpi=100)
    if show:
        plt.show()

def hsl_to_rgb(h,s,l):
    pass

def rgb_to_html_string(r,g,b):
    pass

def gen_color_scheme(home_color=(193,67,28), n=10):
    """
    Generate a color scheme based on n colors evenly space around the color wheel,
    in terms of angle. The home_color is the default starting point, which is
    cyan, in hsl notation. We can divide the 2(pi) radians by n to get the angle offset. 
    Then the angles are given by (start_angle) + (2*pi*i)/n as i varies from 0 to n-1. 
    """
    pass

# After this if we have a list of integers we wish to map to colors, just index them (already done if they're in a list!)
# and assign the ith color to angle (start_angle) + (2*pi*i)/n, where n is the number of unique integers in the list. 

# Finally, make this a matplotlib color scheme? Or just manually convert to html color name. 

if __name__ == '__main__':
    colors = ['red', 'purple', 'blue', 'cyan', 'green', 'yellow']
    test_scheme(colors)
