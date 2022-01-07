# -*- coding: utf-8 -*-

# plane-mo

# import libraries
import time
import math
import numpy as np
import matplotlib.pyplot as plt

"""## Classes"""

class Observer:
    __name = None
    __objects = None
    __location = None
    __timeMode = None
    __time = None

    def __init__(self, na, ob, lo, ti, te):
        self.__name = na
        self.__objects = ob
        self.__location = lo
        self.__timeMode = ti
        self.__time = te

    def infob(self):
        from bokeh.io import output_file, output_notebook
        from bokeh.models import ColumnDataSource, LabelSet
        from bokeh.models import PanTool, WheelZoomTool, ResetTool, SaveTool, CrosshairTool
        from bokeh.models.annotations import Label
        from bokeh.plotting import figure, show, save
        from bokeh.palettes import Plasma, Viridis, Category20

        for sy in self.__objects:
            print(f"observer name : {self.__name.title()}".title())
            print(f"system observed : {sy.getSystemName().title()}".title())
            te = Time(self.__time, self)
            fo = lambda: te.forward()
            ba = lambda: te.backward()
            runMode = fo if te.getNow() < te.getEnd() else ba
            s = 10
            a = 3

            while te.getNow() != te.getEnd():
                runMode()
                # te.adjust()
                print(te.statusUpdate())

                # Output the visualization directly in the notebook
                output_file(filename='index.html', title='plane-mo')

                # Create a figure with no toolbar and axis ranges of [0,s]
                fig = figure(
                    title=f"Planetary-Motion; Observer Name : {self.__name.title()}; System Name : {sy.getSystemName().title()}; {te.statusUpdate().title()}",
                    tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool(), CrosshairTool()],
                    sizing_mode='scale_both',
                    x_range=(-s,s), y_range=(-s,s))

                lx, ly, sz, nm = [], [], [], []

                for i in sy.getLSO():
                    x, y = i.info()[2].getXY()
                    lx.append((x/a) * s)
                    ly.append((y/a) * s)
                    sz.append(.4 if i.info()[0] == 'star' else .25)
                    nm.append(i.info()[1].title())
                    lb = Label(x=lx[len(lx)-1], y=ly[len(ly)-1], x_offset=3, y_offset=3, text=nm[len(nm)-1], angle=.3)
                    fig.add_layout(lb)

                for i in sy.getLOO():
                    x, y = i.info()[2].getXY()
                    lx.append((x/a) * s)
                    ly.append((y/a) * s)
                    sz.append(.15 if i.info()[0] == 'planet' else .1)
                    nm.append(i.info()[1].title())
                    lb = Label(x=lx[len(lx)-1], y=ly[len(ly)-1], x_offset=3, y_offset=3, text=nm[len(nm)-1], angle=.3)
                    fig.add_layout(lb)
                    
                    x, y = i.getOC()[1].info()[2].getXY()
                    x, y = (x/a) * s, (y/a) * s
                    fig.circle(x=x, y=y, radius=i.getOC()[2]/a * s, fill_alpha=0, line_color='black', line_width=1)
                    
                fig.circle(x=lx, y=ly, color=Category20[len(lx)], radius=sz, alpha=.5)

                # Show plot
                save(fig)

    def info(self):
        for sy in self.__objects:
            print(f"observer name : {self.__name.title()}".title())
            print(f"system observed : {sy.getSystemName().title()}".title())
            te = Time(self.__time, self)
            fo = lambda: te.forward()
            ba = lambda: te.backward()
            runMode = fo if te.getNow() < te.getEnd() else ba
            s = 10
            a = 3

            while te.getNow() != te.getEnd():
                runMode()
                # te.adjust()
                print(te.statusUpdate())

                fig = plt.figure(figsize=(s, s))
                ax = plt.axes()
                ax.set_xlim(-s, s)
                ax.set_ylim(-s, s)
                ax.set_title(
                    f"Planetary-Motion\nObserver Name : {self.__name.title()}\nSystem Name : {sy.getSystemName().title()}\n{te.statusUpdate().title()}"
                )
                plt.grid(True)

                for i in sy.getLSO():
                    x, y = i.info()[2].getXY()
                    x, y = (x/a) * s, (y/a) * s
                    # ax.scatter(x, y, s=2000 if i.info()[0] == 'star' else 67.5, alpha=.5)
                    ax.scatter(x, y, s=i.info()[3] * s)
                    ax.text(x, y, i.info()[1].title())
                    # print(
                    #     f"{i.info()[0]}, {i.info()[1]}, {i.info()[2].getXY()}, {i.info()[3]}"
                    # )

                for i in sy.getLOO():
                    x, y = i.info()[2].getXY()
                    x, y = (x/a) * s, (y/a) * s
                    ax.scatter(x, y, s=i.info()[3] * s)
                    # ax.scatter(x, y, s=250 if i.info()[0] == 'planet' else 67.5, alpha=.5)
                    # if i.info()[0] != 'satelite':
                    #     ax.text(x, y, i.info()[1].title())
                    ax.text(x, y, i.info()[1].title())

                    x, y = i.getOC()[1].info()[2].getXY()
                    x, y = (x/a) * s, (y/a) * s
                    ot = plt.Circle( (x, y), (i.getOC()[2]/a) * s, fill = False, alpha=.5)
                    ax.set_aspect(1)
                    ax.add_artist(ot)

                    # print(
                    #     f"{i.info()[0]}, {i.info()[1]}, {i.info()[2].getXY()}, {i.info()[3]}"
                    # )

                plt.show()
                plt.savefig(f"{1000000+te.runNo()}.png")
                plt.close(fig)
                # gc.collect()

    def setTimeMode(ti):
        mo = ["second", "minute", "hour", "day", "week", "month"]
        print(ti, "is not allowed!, resetting to second")
        self.__timeMode = ti if ti in mo else "second"

    def getTimeMode(self):
        return self.__timeMode

    def getLOO(self):
        loo = []
        for sy in self.__objects:
            for i in sy.getLOO():
                loo.append(i)
        return loo

class PlanetarySystem:
    __systemName = None
    __listOfStationaryObjects = None
    __listOfOrbitingObjects = None

    def __init__(self, sy, st, ob):
        self.__systemName = sy
        self.__listOfStationaryObjects = st
        self.__listOfOrbitingObjects = ob

    def getSystemName(self):
        return self.__systemName

    def getLSO(self):
        return self.__listOfStationaryObjects

    def getLOO(self):
        return self.__listOfOrbitingObjects

class Coordinate:
    __x = None
    __y = None

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def setXY(self, x, y):
        self.__x = x
        self.__y = y

    def getXY(self):
        return self.__x, self.__y

    def dist(self, other):
        return math.sqrt(((self.__x - other.__x) ** 2) + ((self.__y - other.__y) ** 2))

class Time:
    # time is always in seconds
    # it's the timeMode that controls
    # it's display for user
    __begin = None
    __end = None
    __speed = None
    __now = None
    __updateVal = None
    __observer = None

    def __init__(self, te, ob):
        self.__speed = te[2]
        self.__observer = ob
        self.__updateVal = self.eq(self.__observer.getTimeMode())
        self.__begin = te[0] * self.__updateVal
        self.__now = te[0] * self.__updateVal
        self.__end = te[1] * self.__updateVal

    # translate choosen timeMode
    # to default time (seconds)
    @staticmethod
    def eq(mo):
        eq = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
            "week": 604800,
            "month": 2592000,
        }  # fixed at 30 days
        return eq[mo]

    # increment time
    def forward(self):
        if self.__now + self.__updateVal > self.__end:
            self.__now = self.__end
        else:
            self.__now += self.__updateVal
        for i in self.__observer.getLOO():
            i.motionFormula(self.timeProgress())

    # decrement time
    def backward(self):
        if self.__now - self.__updateVal < self.__end:
            self.__now = self.__end
        else:
            self.__now -= self.__updateVal
        for i in self.__observer.getLOO():
            i.motionFormula(self.timeProgress())

    # interupt for a while
    def adjust(self):
        time.sleep(1 / self.__speed)

    # strictly for motion formula
    # required to calculate angle
    def timeProgress(self):
        return self.__now / 31536000

    # return #time passed until end
    def statusUpdate(self):
        no = self.__now // self.__updateVal
        en = self.__end // self.__updateVal
        return f"#{no}/{en} {self.__observer.getTimeMode().title()}s".title()

    # return current #run
    def runNo(self):
        return self.__now // self.__updateVal

    def getNow(self):
        return self.__now

    def getEnd(self):
        return self.__end

class StellarObject:
    __category = None
    __name = None
    __position = None
    __size = None

    def __init__(self, ca, na, po, si):
        self.__category = ca
        self.__name = na
        self.__position = po
        self.__size = si

    def info(self):
        return self.__category, self.__name, self.__position, self.__size

class StationaryObject(StellarObject):
    def __init__(self, ca, na, po, si):
        StellarObject.__init__(self, ca, na, po, si)

    def info(self):
        return StellarObject.info(self)

class OrbitingObject(StellarObject):
    __timeRatio = None
    __orbitalCentre = None
    __orbitalRadius = None

    def __init__(self, ca, na, po, si, ti, oe, os):
        StellarObject.__init__(self, ca, na, po, si)
        self.__timeRatio = ti
        self.__orbitalCentre = oe
        self.__orbitalRadius = os

    def motionFormula(self, tp):
        oe_x, oe_y = self.__orbitalCentre.info()[2].getXY()
        deg = tp * 360 / self.__timeRatio
        while deg >= 360:
            deg -= 360
        rad = math.radians(deg)
        x = oe_x + (self.__orbitalRadius * (math.cos(rad)))
        y = oe_y + (self.__orbitalRadius * (math.sin(rad)))
        StellarObject.info(self)[2].setXY(x, y)

    def getOC(self):
        return self.__timeRatio, self.__orbitalCentre, self.__orbitalRadius

    def info(self):
        return StellarObject.info(self)

"""## Main Program

### Ivan : Milky Way (Inner Region)
"""

lso = []
lso.append(StationaryObject("star", "sol", Coordinate(0, 0), 109))

loo = []
loo.append(
    OrbitingObject(
        "planet", # category
        "mercury", # name
        Coordinate(0.39, 0), # position
        0.383, # size
        0.24, # timeratio
        lso[0], # orbital centre
        lso[0].info()[2].dist(Coordinate(0.39, 0)), # orbital radius
    )
)
loo.append(
    OrbitingObject(
        "planet",
        "venus",
        Coordinate(0.72, 0),
        0.949,
        0.62,
        lso[0],
        lso[0].info()[2].dist(Coordinate(0.72, 0)),
    )
)
loo.append(
    OrbitingObject(
        "planet",
        "earth",
        Coordinate(1, 0),
        3,
        1,
        lso[0],
        lso[0].info()[2].dist(Coordinate(1, 0)),
    )
)
loo.append(
    OrbitingObject(
        "satelite",
        "moon",
        Coordinate(1.1, 0),
        0.27,
        0.074,
        loo[2],
        loo[2].info()[2].dist(Coordinate(1.1, 0)),
    )
)
loo.append(
    OrbitingObject(
        "planet",
        "mars",
        Coordinate(1.52, 0),
        0.532,
        1.88,
        lso[0],
        lso[0].info()[2].dist(Coordinate(1.52, 0)),
    )
)
loo.append(
    OrbitingObject(
        "satelite",
        "phobos",
        Coordinate(1.62, 0),
        1.76,
        0.0008,
        loo[4],
        loo[4].info()[2].dist(Coordinate(1.62, 0)),
    )
)
loo.append(
    OrbitingObject(
        "satelite",
        "deimos",
        Coordinate(1.67, 0),
        0.0009,
        0.003,
        loo[4],
        loo[4].info()[2].dist(Coordinate(1.67, 0)),
    )
)
loo.append(
    OrbitingObject(
        "asteroid",
        "vesta",
        Coordinate(2.36, 0),
        0.041,
        3.63,
        lso[0],
        lso[0].info()[2].dist(Coordinate(2.36, 0)),
    )
)
loo.append(
    OrbitingObject(
        "asteroid",
        "juno",
        Coordinate(2.66, 0),
        0.019,
        4.36,
        lso[0],
        lso[0].info()[2].dist(Coordinate(2.66, 0)),
    )
)
loo.append(
    OrbitingObject(
        "asteroid",
        "ceres",
        Coordinate(2.77, 0),
        0.073,
        4.6,
        lso[0],
        lso[0].info()[2].dist(Coordinate(2.77, 0)),
    )
)
loo.append(
    OrbitingObject(
        "asteroid",
        "pallas",
        Coordinate(2.77, 0),
        0.04,
        4.62,
        lso[0],
        lso[0].info()[2].dist(Coordinate(2.77, 0)),
    )
)

lps = []
lps.append(PlanetarySystem("milky way (inner region)", lso, loo))

lob = []
lob.append(Observer(
    "ivan", # observer name
    lps, # list planet
    lso[0].info()[2], # posisi observer (bumi)
    "day",
    [999999, 1000000, 100]))

for i in lob:
    i.infob()
