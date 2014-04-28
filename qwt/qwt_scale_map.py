# -*- coding: utf-8 -*-

from qwt.qwt_math import qwtFuzzyCompare

from qwt.qt.QtCore import QRectF, QPointF


class QwtScaleMap(object):
    def __init__(self, other=None):
        self.d_transform = None # QwtTransform
        if other is None:
            self.d_s1 = 0.
            self.d_s2 = 1.
            self.d_p1 = 0.
            self.d_p2 = 1.
            self.d_cnv = 1.
            self.d_ts1 = 0.
        else:
            self.d_s1 = other.d_s1
            self.d_s2 = other.d_s2
            self.d_p1 = other.d_p1
            self.d_p2 = other.d_p2
            self.d_cnv = other.d_cnv
            self.d_ts1 = other.d_ts1
            if other.d_transform:
                self.d_transform = other.d_transform.copy()

    def __eq__(self, other):
        return self.d_s1 == other.d_s1 and\
               self.d_s2 == other.d_s2 and\
               self.d_p1 == other.d_p1 and\
               self.d_p2 == other.d_p2 and\
               self.d_cnv == other.d_cnv and\
               self.d_ts1 == other.d_ts1

    def s1(self):
        return self.d_s1
        
    def s2(self):
        return self.d_s2
        
    def p1(self):
        return self.d_p1
        
    def p2(self):
        return self.d_p2
    
    def pDist(self):
        return abs(self.d_p2 - self.d_p1)
        
    def sDist(self):
        return abs(self.d_s2 - self.d_s1)

    def transform_scalar(self, s):
        if self.d_transform:
            s = self.d_transform.transform(s)
        return self.d_p1 + (s - self.d_ts1)*self.d_cnv
    
    def invTransform_scalar(self, p):
        s = self.d_ts1 + ( p - self.d_p1 ) / self.d_cnv
        if self.d_transform:
            s = self.d_transform.invTransform(s)
        return s
    
    def isInverting(self):
        return ( self.d_p1 < self.d_p2 ) != ( self.d_s1 < self.d_s2 )
    
    def setTransformation(self, transform):
        if self.d_transform != transform:
            self.d_transform = transform
        self.setScaleInterval(self.d_s1, self.d_s2)
    
    def transformation(self):
        return self.d_transform
    
    def setScaleInterval(self, s1, s2):
        self.d_s1 = s1
        self.d_s2 = s2
        if self.d_transform:
            self.d_s1 = self.d_transform.bounded(self.d_s1)
            self.d_s2 = self.d_transform.bounded(self.d_s2)
        self.updateFactor()

    def setPaintInterval(self, p1, p2):
        self.d_p1 = p1
        self.d_p2 = p2
        self.updateFactor()
    
    def updateFactor(self):
        self.d_ts1 = self.d_s1
        ts2 = self.d_s2
        if self.d_transform:
            self.d_ts1 = self.d_transform.transform(self.d_ts1)
            ts2 = self.d_transform.transform(ts2)
        self.d_cnv = 1.
        if self.d_ts1 != ts2:
            self.d_cnv = (self.d_p2 - self.d_p1)/(ts2 - self.d_ts1)
    
    def transform(self, *args):
        """Transform from scale to paint coordinates
        
        Scalar: scalemap.transform(scalar)
        Point (QPointF): scalemap.transform(xMap, yMap, pos)
        Rectangle (QRectF): scalemap.transform(xMap, yMap, rect)
        """
        if len(args) == 1:
            # Scalar transform
            return self.transform_scalar(args[0])
        elif isinstance(args[2], QPointF):
            xMap, yMap, pos = args
            return QPointF(xMap.transform(pos.x()),
                           yMap.transform(pos.y()))
        elif isinstance(args[2], QRectF):
            xMap, yMap, rect = args
            x1 = xMap.transform(rect.left())
            x2 = xMap.transform(rect.right())
            y1 = yMap.transform(rect.top())
            y2 = yMap.transform(rect.bottom())
            if x2 < x1:
                x1, x2 = x2, x1
            if y2 < y1:
                y1, y2 = y2, y1
            if qwtFuzzyCompare(x1, 0., x2-x1) == 0:
                x1 = 0.
            if qwtFuzzyCompare(x2, 0., x2-x1) == 0:
                x2 = 0.
            if qwtFuzzyCompare(y1, 0., y2-y1) == 0:
                y1 = 0.
            if qwtFuzzyCompare(y2, 0., y2-y1) == 0:
                y2 = 0.
            return QRectF(x1, y1, x2-x1+1, y2-y1+1)

    def invTransform(self, *args):
        """Transform from paint to scale coordinates
        
        Scalar: scalemap.invTransform(scalar)
        Point (QPointF): scalemap.invTransform(xMap, yMap, pos)
        Rectangle (QRectF): scalemap.invTransform(xMap, yMap, rect)
        """
        if len(args) == 1:
            # Scalar transform
            return self.invTransform_scalar(args[0])
        elif isinstance(args[2], QPointF):
            xMap, yMap, pos = args
            return QPointF(xMap.invTransform(pos.x()),
                           yMap.invTransform(pos.y()))
        elif isinstance(args[2], QRectF):
            xMap, yMap, rect = args
            x1 = xMap.invTransform(rect.left())
            x2 = xMap.invTransform(rect.right()-1)
            y1 = yMap.invTransform(rect.top())
            y2 = yMap.invTransform(rect.bottom()-1)
            r = QRectF(x1, y1, x2-x1, y2-y1)
            return r.normalized()
