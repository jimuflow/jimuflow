# This software is dual-licensed under the GNU General Public License (GPL) 
# and a commercial license.
#
# You may use this software under the terms of the GNU GPL v3 (or, at your option,
# any later version) as published by the Free Software Foundation. See 
# <https://www.gnu.org/licenses/> for details.
#
# If you require a proprietary/commercial license for this software, please 
# contact us at jimuflow@gmail.com for more information.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copyright (C) 2024-2025  Weng Jing

import sys

from PySide6.QtCore import QRectF, Qt, QLineF, QPointF, Slot, QSizeF
from PySide6.QtGui import QPen, QPainter, QTransform
from PySide6.QtWidgets import QGraphicsItem, QGraphicsView, QGraphicsScene, QApplication, QMainWindow, QVBoxLayout, \
    QPushButton


class Component(QGraphicsItem):

    def __init__(self):
        super().__init__()
        self.in_port = InPort(self)
        self.in_port.setPos(QPointF(50, 0))
        self.out_ports = []
        self.add_out_port('default')
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def add_out_port(self, out_port_id):
        for out_port in self.out_ports:
            if out_port.out_port_id == out_port_id:
                return
        out_port = OutPort(self, out_port_id)
        self.out_ports.append(out_port)
        self.adjust_out_ports()

    def adjust_out_ports(self):
        x_space = 100 / (len(self.out_ports) + 1)
        for i, out_port in enumerate(self.out_ports):
            out_port.setPos(QPointF(x_space * (i + 1), 100))

    def boundingRect(self):
        return QRectF(0, 0, 100, 100)

    def paint(self, painter, option, widget):
        # 绘制组件的矩形框
        rect = QRectF(0, 0, 100, 100)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.darkGray)
        painter.drawRect(rect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.in_port.item_moved()
            for out_port in self.out_ports:
                out_port.item_moved()
        return QGraphicsItem.itemChange(self, change, value)


class InPort(QGraphicsItem):

    def __init__(self, parent):
        super().__init__(parent)
        self._edge_list = []

    def get_first_edge(self):
        if self._edge_list:
            return self._edge_list[0]
        return None

    def add_edge(self, edge):
        self._edge_list.append(edge)

    def remove_edge(self, edge):
        self._edge_list.remove(edge)

    def boundingRect(self):
        return QRectF(-5, -25, 10, 25)

    def paint(self, painter, option, widget):
        # 绘制入口棒棒糖
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.darkGray)
        painter.drawLine(QLineF(0, 0, 0, -20))
        painter.drawEllipse(QRectF(-5, -25, 10, 10))

    def item_moved(self):
        for edge in self._edge_list:
            edge.adjust()


class OutPort(QGraphicsItem):

    def __init__(self, parent, out_port_id):
        super().__init__(parent)
        self.out_port_id = out_port_id
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self._edge = None

    def set_edge(self, edge):
        self._edge = edge

    def get_edge(self):
        return self._edge

    def boundingRect(self):
        return QRectF(-5, 0, 10, 25)

    def paint(self, painter, option, widget):
        # 绘制出口棒棒糖
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.darkGray)
        painter.drawLine(QLineF(0, 0, 0, 20))
        painter.drawEllipse(QRectF(-5, 15, 10, 10))

    def item_moved(self):
        if self._edge:
            self._edge.adjust()

    # def sceneEvent(self,event):
    #     print('sceneEvent',event)
    #     return QGraphicsItem.sceneEvent(self, event)
    #
    # def mousePressEvent(self, event):
    #     print("mousePressEvent")
    #     QGraphicsItem.mousePressEvent(self, event)
    #
    # def mouseMoveEvent(self, event):
    #     print("mouseMoveEvent")
    #     QGraphicsItem.mouseMoveEvent(self, event)
    #
    # def mouseReleaseEvent(self, event):
    #     print("mouseReleaseEvent")
    #     QGraphicsItem.mouseReleaseEvent(self, event)


class Edge(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.out_port = None
        self.in_port = None
        self.drag_point = QPointF()
        self._source_point = QPointF()
        self._dest_point = QPointF()

    def set_out_port(self, out_port):
        if self.out_port:
            self.out_port.set_edge(None)
        if out_port:
            out_port.set_edge(self)
        self.out_port = out_port
        self.adjust()

    def get_out_port(self):
        return self.out_port

    def set_in_port(self, in_port):
        if self.in_port:
            self.in_port.remove_edge(self)
        if in_port:
            in_port.add_edge(self)
        self.in_port = in_port
        self.adjust()

    def get_in_port(self):
        return self.in_port

    def set_drag_point(self, point):
        self.drag_point = point
        self.adjust()

    def adjust(self):
        points = 0
        if self.in_port:
            points += 1
        if self.out_port:
            points += 1
        if not self.drag_point.isNull():
            points += 1
        if points < 2:
            return

        self.prepareGeometryChange()
        if self.out_port:
            self._source_point = self.mapFromItem(self.out_port, 0, 20)
        else:
            self._source_point = self.drag_point

        if self.in_port:
            self._dest_point = self.mapFromItem(self.in_port, 0, -20)
        else:
            self._dest_point = self.drag_point

    def boundingRect(self):
        points = 0
        if self.in_port:
            points += 1
        if self.out_port:
            points += 1
        if not self.drag_point.isNull():
            points += 1
        if points < 2:
            return QRectF()

        width = self._dest_point.x() - self._source_point.x()
        height = self._dest_point.y() - self._source_point.y()
        rect = QRectF(self._source_point, QSizeF(width, height))
        return rect.normalized()

    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.darkGray)
        painter.drawLine(QLineF(self._source_point, self._dest_point))


class Scene(QGraphicsScene):
    def __init__(self, parent):
        super().__init__(parent)
        self._drag_edge = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        edge = None
        if isinstance(item, OutPort):
            edge = item.get_edge()
            if edge:
                edge.set_out_port(None)
            else:
                edge = Edge()
                edge.set_out_port(item)
                self.addItem(edge)
        elif isinstance(item, InPort):
            edge = item.get_first_edge()
            if edge:
                edge.set_in_port(None)
            else:
                edge = Edge()
                edge.set_in_port(item)
                self.addItem(edge)
        if edge:
            print('mousePressEvent', edge)
            edge.set_drag_point(edge.mapFromScene(event.scenePos()))
            self._drag_edge = edge
        QGraphicsScene.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self._drag_edge:
            self._drag_edge.set_drag_point(self._drag_edge.mapFromScene(event.scenePos()))
        QGraphicsScene.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self._drag_edge:
            items = self.items(event.scenePos())
            item=None
            if self._drag_edge.get_in_port():
                for i in items:
                    if isinstance(i, OutPort):
                        item = i
                        break
            elif self._drag_edge.get_out_port():
                for i in items:
                    if isinstance(i, InPort):
                        item = i
                        break
            if isinstance(item, InPort):
                if self._drag_edge.get_out_port() and self._drag_edge.get_out_port().parentItem() is not item.parentItem():
                    self._drag_edge.set_drag_point(QPointF())
                    self._drag_edge.set_in_port(item)
                    print('ok')
                else:
                    self._drag_edge.set_out_port(None)
                    self.removeItem(self._drag_edge)
                    print('fail')
            elif isinstance(item, OutPort):
                if self._drag_edge.get_in_port() and self._drag_edge.get_in_port().parentItem() is not item.parentItem():
                    self._drag_edge.set_drag_point(QPointF())
                    self._drag_edge.set_out_port(item)
                else:
                    self._drag_edge.set_in_port(None)
                    self.removeItem(self._drag_edge)
            else:
                self._drag_edge.set_in_port(None)
                self._drag_edge.set_out_port(None)
                self.removeItem(self._drag_edge)
            self._drag_edge = None
        QGraphicsScene.mouseReleaseEvent(self, event)


class GraphWidget(QGraphicsView):
    def __init__(self):
        super().__init__()

        scene = Scene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        scene.setSceneRect(-200, -200, 400, 400)
        self.setScene(scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        comp1 = Component()
        comp1.setPos(0, 0)
        scene.addItem(comp1)
        self.comp1 = comp1
        # self.scene().focusItemChanged.connect(self.on_focuse_item_changed)

    @Slot(QGraphicsItem, QGraphicsItem, Qt.FocusReason)
    def on_focuse_item_changed(self, newFocusItem, oldFocusItem, reason):
        print('on_focuse_item_changed', newFocusItem, oldFocusItem, reason)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(GraphWidget())
        layout = QVBoxLayout(self.centralWidget())
        self.graphWidget = GraphWidget()
        layout.addWidget(self.graphWidget)
        self.add_out_port_button = QPushButton("Add OutPort")
        layout.addWidget(self.add_out_port_button)
        self.add_out_port_button.clicked.connect(self.add_out_port)
        self.add_component_button = QPushButton("Add Component")
        layout.addWidget(self.add_component_button)
        self.add_component_button.clicked.connect(self.add_component)

    @Slot()
    def add_out_port(self):
        items = self.graphWidget.scene().selectedItems()
        if len(items) == 0:
            return
        comp = items[0]
        if not isinstance(comp, Component):
            return
        comp.add_out_port(f'new{len(comp.out_ports)}')

    @Slot()
    def add_component(self):
        comp = Component()
        self.graphWidget.scene().addItem(comp)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
