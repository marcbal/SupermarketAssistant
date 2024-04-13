# Copyright (c) 2024 Marc Baloup
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



def lerp(y0: float, y1: float, x: float): 
    return y0 + (y1 - y0) * x

def inverse_lerp(x0: float, x1: float, x: float): 
    return (x - x0) / (x1 - x0)



def local_max(f: callable, x_min: float, x_max: float, precision: float):
    """Approximates the local maximum of the provided function.
    Only works on a continuous function that increases then decrease on the provided interval.
    """
    if (x_max - x_min < precision):
        return (x_min + x_max) / 2
    xList = [
        x_min,
        lerp(x_min, x_max, 0.25),
        lerp(x_min, x_max, 0.5),
        lerp(x_min, x_max, 0.75),
        x_max]
    yList = [f(x) for x in xList]
    for i in range(len(xList)-1):
        if (yList[i] >= yList[i + 1]):
            return local_max(f, xList[i if i == 0 else (i - 1)], xList[i + 1], precision)

    return local_max(f, xList[len(xList) - 2], xList[len(xList) - 1], precision)


class Keyframe:
    def __init__(self, data):
        self.time = float(data["time"])
        self.value = float(data["value"])
        self.inTangent = float(data["inTangent"])
        self.outTangent = float(data["outTangent"])



class AnimationCurve:
    """An AnimationCurve, as implemented in the Unity game engine."""
    def __init__(self, data):
        self.keys: list[Keyframe] = []
        for curveData in data["keys"]:
            self.keys.append(Keyframe(curveData))
        self.keys = sorted(self.keys, key=lambda k: k.time)
        self.preWrapMode = int(data["preWrapMode"])
        self.postWrapMode = int(data["postWrapMode"])



    
    def evaluate(self, t: float) -> float:
        for i in range(len(self.keys)):
            if (self.keys[i].time >= t):
                if (i == 0):
                    return self.keys[0].value
                else:
                    kf0 = self.keys[i - 1]
                    kf1 = self.keys[i]
                    lerpT = inverse_lerp(kf0.time, kf1.time, t)
                    return AnimationCurve.evaluate_between_kf(lerpT, kf0, kf1)
        return self.keys[-1].value

    # sourced from https://discussions.unity.com/t/what-is-the-math-behind-animationcurve-evaluate/72058/3       
    @staticmethod
    def evaluate_between_kf(t: float, kf0: Keyframe, kf1: Keyframe):
            dt = kf1.time - kf0.time
            # dt = (x1 - x0)
            # t = ((x - x0) / dt)
            
            m0 = kf0.outTangent * dt
            m1 = kf1.inTangent * dt

            t2 = t * t
            t3 = t2 * t
            
            a = 2 * t3 - 3 * t2 + 1
            b = t3 - 2 * t2 + t
            c = t3 - t2
            d = -2 * t3 + 3 * t2
            
            #y = (2*((x-x_0)/(x_1-x_0))^3-3*((x-x_0)/(x_1-x_0))^2+1)*y_0
            #    + (((x-x_0)/(x_1-x_0))^3-2*((x-x_0)/(x_1-x_0))^2+((x-x_0)/(x_1-x_0)))*(o_0*(x_1-x_0))
            #    + (((x-x_0)/(x_1-x_0))^3-((x-x_0)/(x_1-x_0))^2)*(i_1*(x_1-x_0))
            #    + (-2*((x-x_0)/(x_1-x_0))^3+3*((x-x_0)/(x_1-x_0))^2)*y_1
            
            #y = ((y_0*(x_1+2*x-3*x_0)*(x-x_1)^2)+(y_1*(3*x_1-2*x-x_0)*(x-x_0)^2))/((x_1-x_0)^3)
            #    + ((x-x_1)/(x_1-x_0))^2*(x-x_0)*o_0
            #    + ((x-x_0)/(x_1-x_0))^2*(x-x_1)*i_1
            return a * kf0.value + b * m0 + c * m1 + d * kf1.value
