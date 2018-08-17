# Mandelbrot and Julia set Explorer
#TO DO:
#   -Find a way to speed up the mSetCol and jSetCol algorithms
#   -Different colour schemes
#   -Remove ailiasing
#   -improve asthetic quality of rendering
#   -Add more rigours comments
import sys, re
import numpy as np
from math import *
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage

class Window(QWidget):
        """Class that handels the rendering and diplaying of fractals"""
        def __init__(self):
            super().__init__()
            self.title = 'Fractal Explorer'
            self.left = 10
            self.top = 10
            self.width = 640
            self.height = 480
            #Set up Rest of class wide variables
            self.maxItr = 25
            self.xdim = 1000
            self.img = None
            self.col = [[66, 30, 15],[25, 7, 26],[9, 1, 47],[4, 4, 73],\
                        [0, 7, 100],[12, 44, 138],[24, 82, 177],[57, 125, 209],\
                        [134, 181, 229],[211, 236, 248],[241, 233, 191],[248, 201, 95],\
                        [255, 170, 0],[204, 128, 0],[153, 87, 0],[106, 52, 3]]
            self.initUI()
            terminal = Terminal(self)

        def initUI(self):
            self.setWindowTitle(self.title)
            self.setGeometry(self.left, self.top, self.width, self.height)
            # Create widget
            self.label = QLabel(self)
            #Generate initial image
            self.showMset([[-2.5,1],[-1.2,1.2]])
            #pixmap = QPixmap('image.jpg')
            self.show()
            return

        def mSetCol(self, zrange):
            """Function that generates numpy array containing mandelbrot set"""
            #Caclulate y dimension and size of pixle in the complex plane
            ydim = floor((abs(zrange[1][1]-zrange[1][0])/abs(zrange[0][1]-zrange[0][0]))*self.xdim)
            xpix = abs(zrange[0][1]-zrange[0][0])/self.xdim
            ypix = abs(zrange[1][1]-zrange[1][0])/((abs(zrange[1][1]-zrange[1][0])/abs(zrange[0][1]-zrange[0][0]))*self.xdim)

            #Generate a ydim by self.xdim matrix of complex numbers
            C = np.zeros((ydim,self.xdim),dtype=complex)
            for i in range(ydim):
                for ii in range(self.xdim):
                    C[i,ii] = complex((zrange[0][0]+((ii+1/2)*xpix)),(zrange[1][1]-((i+1/2)*ypix)))

            #Perform interative operation Z^2+C on each point of the plane to generate set
            M = [[[0 for k in range(3)] for j in range(self.xdim)] for i in range(ydim)]
            for i in range(ydim):
                print(i)
                for ii in range(self.xdim):
                    z = 0j
                    c = C[i,ii]
                    itr = 0
                    while abs(z)<4 and itr < self.maxItr:
                        z = z**2 + c
                        itr += 1
                    if  itr != self.maxItr:
                        M[i][ii]= self.smoothCol(itr,z)
            return np.asarray(M, dtype=np.uint8)

        def jSetCol(self, zrange, c):
            """Function that generates numpy array containing filled julia set described by c"""
            #Caclulate y dimension and size of pixle in the complex plane
            ydim = floor((abs(zrange[1][1]-zrange[1][0])/abs(zrange[0][1]-zrange[0][0]))*self.xdim)
            xpix = abs(zrange[0][1]-zrange[0][0])/self.xdim
            ypix = abs(zrange[1][1]-zrange[1][0])/((abs(zrange[1][1]-zrange[1][0])/abs(zrange[0][1]-zrange[0][0]))*self.xdim)

            #Generate a ydim by self.xdim matrix of complex numbers
            Z = np.zeros((ydim,self.xdim),dtype=complex)
            for i in range(ydim):
                for ii in range(self.xdim):
                    Z[i,ii] = complex((zrange[0][0]+((ii+1/2)*xpix)),(zrange[1][1]-((i+1/2)*ypix)))

            #Perform interative operation Z^2+C on each point of the plane to generate set
            J = [[[0 for k in range(3)] for j in range(self.xdim)] for i in range(ydim)]
            for i in range(ydim):
                print(i)
                for ii in range(self.xdim):
                    z = Z[i,ii]
                    itr = 0
                    while abs(z)<4 and itr < self.maxItr:
                        z = z**2 + c
                        itr += 1
                    if  itr != self.maxItr:
                        J[i][ii]= self.smoothCol(itr,z)
            #light = colors.LightSource(azdeg=315, altdeg=10)
            #M = light.shade(J, cmap=plt.cm.hot, vert_exag=1.5,norm=colors.PowerNorm(0.3), blend_mode='hsv')
            return np.asarray(J, dtype=np.uint8)

        def smoothCol(self, itr, z):
            """A function to remove aliasing from M and J set renderings.
            The mathematics of this method illudes my comprehesion a better
            understanding would no doubt improve the quality of it's output"""
            #Caclulate potential function
            log_zn = log(abs(z)*2)/2
            nu = log(log_zn/log(2))/log(2)
            itr = itr+1-nu
            #linearly iterpolate
            nuF = nu%1 # Get the fractional part of nu
            c = [0,0,0]
            c1 = self.col[(floor(itr))%len(self.col)]
            c2 = self.col[(floor(itr)+1)%len(self.col)]
            for i in range(3):
                c[i] =  c2[i] - ((c2[i]-c1[i])*nuF)
            return c

        def overlayGrid(self, n, m):
            """private method, overlays a n by m grid current image"""
            #get dimensions of img
            x = self.img.shape[0]
            y = self.img.shape[1]
            #x/n, y/m and floor to get grid distance
            dx = int(np.ceil(x/n))
            dy = int(np.ceil(y/m))
            #draw lines onto the image in the apropriate way
            t = int(np.ceil(max(x,y)/1000))
            for i in range(1,n):
                for j in range((i*dx),(i*dx)+t):
                    self.img[j,range(y)] = 0
            for k in range(1,m):
                for l in range((k*dy),(k*dy)+t):
                    self.img[range(x),l] = 0
            return

        def updateImage(self):
            """private method, update image on screen to current state of img[] feild"""
            height, width, channel = self.img.shape
            bytesPerLine = 3 * width
            qImg = QPixmap.fromImage(QImage(self.img.data, width, height, bytesPerLine, QImage.Format_RGB888))
            self.label.setPixmap(qImg)
            self.resize(width,height)
            self.show()

        def showMset(self, zrange): #Add optional arguments for grid?
            """public method, render mset over specificed reigion and update display"""
            self.img = self.mSetCol(zrange)
            self.updateImage()
            return

        def showJset(self, zrange, c): #Add optional arguments for grid?
            """public method, render mset over specificed reigion and update display"""
            self.img = self.jSetCol(zrange, c)
            self.updateImage()
            return

        def showGrid(self, n, m): #Add code to save plain version and add method to restore it
            """public method, add a n by m grid to the currently displayed image"""
            self.overlayGrid(n, m)
            self.updateImage()
            return

        def setXdim(self, xdim):
            """public method sets self.xdim to passed value"""
            self.xdim = xdim
            return

        def setMaxItr(self, maxItr):
            """public method sets self.maxItr to passed value"""
            self.maxItr = maxItr
            return

        def getImage(self):
            """public method, returns current image"""
            return self.img

class Terminal:
    def __init__(self, window):
        self.zrange = [[-2.5,1],[-1.2,1.2]]
        self.n=self.m = None
        self.type = 'm'
        self.c = complex(0,0)
        self.window = window
        while True:
            self.showPrompt()

    def showPrompt(self):
        self.runCommand(input("> ").lower())
        return

    def runCommand(self, cmd):
        #REVISE
        """Uses regular expresions to detemine command,
        extract input data and call corresponding fucntions"""
        if cmd == "quit":
            #Terminate program
            sys.exit(0)
            return
        elif cmd == "show mset":
            self.zrange = [[-2.5,1],[-1.2,1.2]]
            self.n=self.m = None
            self.type = "m"
            self.window.showMset(self.zrange)
            return
        elif "show julia" in cmd:
            try:
                reg = re.findall(r"[-+]?[0-9]+\.?[0-9]*",cmd)
                Re = float(reg[0])
                Im = float(reg[1])
                self.c = complex(Re,Im)
                #Render Julia set
                self.zrange = [[-1.75,1.75],[-1,1]]
                self.n=self.m = None
                self.type = "j"
                self.window.showJset(self.zrange, self.c)
            except:
                print("Please enter complex number")

        elif "show grid" in cmd:
            #extract grid data from cmd
            try:
                nm = re.findall(r"[0-9]+",cmd)
                self.n = int(nm[0])
                self.m = int(nm[1])
                self.window.showGrid(self.n, self.m)
            except:
                print("Please enter grid dimensions")

        elif "zoom" in cmd and re.search(r"[1-9]+",cmd) and re.search(r"[1-9]+",cmd):
            try:
                reg = re.findall(r"[0-9]+", cmd)
                x = int(reg[1])-1
                y = int(reg[0])-1
                lx = abs(self.zrange[0][1]-self.zrange[0][0])
                ly = abs(self.zrange[1][1]-self.zrange[1][0])
                dx = lx/self.m
                dy = ly/self.n
                self.zrange[0] = [self.zrange[0][0]+(y*dx),self.zrange[0][0]+((y+1)*dx)]
                self.zrange[1] = [self.zrange[1][0]+(x*dy),self.zrange[1][0]+((x+1)*dy)]
                if self.type == "m":
                    self.window.showMset(self.zrange)
                elif self.type == "j":
                    self.window.showJset(self.zrange, self.c)
                self.n=self.m = None
            except:
                print("Please enter grid reference")

        elif cmd == "zoom out":
            if self.type == "m":
                runCommand("show mset")
            elif self.type == "j":
                runCommand("show julia "+str(self.c.real)+" "+str(self.c.imag))
        elif cmd == "rerender":
            if self.type == "m":
                self.window.showMset(self.zrange)
            elif self.type == "j":
                self.window.showJset(self.zrange, self.c)
            self.n=self.m = None
        elif cmd == "help":
            print("None to give atm")
        elif "set resolution" in cmd:
            #get xdim resolution from cmd and set xdim global variable
            self.window.setXdim(int(re.search(r"[0-9]+", cmd).group()))
            self.runCommand("rerender")
        elif "set max" in cmd:
            #get max from cmd and set maxItr global variable
            self.window.setMaxItr(int(re.search(r"[0-9]+", cmd).group()))
            self.runCommand("rerender")
        elif "save image" in cmd:
            imsave("./temp.png", self.window.getImage())
        else:
            print("Invalid command")

if __name__ == '__main__':
    #REVISION NEEDED
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())
