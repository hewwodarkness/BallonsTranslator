from PyQt5.QtCore import pyqtSignal, Qt, QPointF, QSize, QLineF
from PyQt5.QtWidgets import QBoxLayout, QCheckBox, QHBoxLayout, QGraphicsView, QUndoCommand, QStackedWidget, QVBoxLayout, QLabel, QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QColor, QCursor, QPainter, QPixmap, QBrush, QFontMetrics
from .stylewidgets import Widget, SeparatorWidget, ColorPicker, PaintQSlider
from .canvas import Canvas
from .misc import DrawPanelConfig
from utils.imgproc_utils import enlarge_window
from typing import Union, Tuple, List
import numpy as np
import cv2

from .dl_manager import DLManager
from .image_edit import ImageEditMode, StrokeItem
from .configpanel import InpaintConfigPanel

INPAINT_BRUSH_COLOR = QColor(127, 0, 127, 127)
MAX_PEN_SIZE = 1000
MIN_PEN_SIZE = 1
TOOLNAME_POINT_SIZE = 13

class DrawToolCheckBox(QCheckBox):
    checked = pyqtSignal()
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stateChanged.connect(self.on_state_changed)

    def mousePressEvent(self, event) -> None:
        if self.isChecked():
            return
        return super().mousePressEvent(event)

    def on_state_changed(self, state: int) -> None:
        if self.isChecked():
            self.checked.emit()

class ToolNameLabel(QLabel):
    def __init__(self, fix_width=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        font = self.font()
        font.setPointSizeF(TOOLNAME_POINT_SIZE)
        fmt = QFontMetrics(font)
        
        if fix_width is not None:
            self.setFixedWidth(fix_width)
            text_width = fmt.width(self.text())
            if text_width > fix_width * 0.95:
                font_size = TOOLNAME_POINT_SIZE * fix_width * 0.95 / text_width
                font.setPointSizeF(font_size)
        self.setFont(font)
            

class InpaintPanel(Widget):

    thicknessChanged = pyqtSignal(int)

    def __init__(self, inpainter_panel: InpaintConfigPanel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.inpainter_panel = inpainter_panel
        self.thicknessSlider = PaintQSlider(self.tr('pen thickness ') + 'value px', Qt.Horizontal)
        self.thicknessSlider.setFixedHeight(50)
        self.thicknessSlider.setRange(MIN_PEN_SIZE, MAX_PEN_SIZE)
        self.thicknessSlider.valueChanged.connect(self.on_thickness_changed)
        
        thickness_layout = QHBoxLayout()
        thickness_label = ToolNameLabel(150, self.tr('Thickness'))
        thickness_layout.addWidget(thickness_label)
        thickness_layout.addWidget(self.thicknessSlider)
        thickness_layout.setSpacing(15)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(thickness_layout)
        layout.addWidget(inpainter_panel)
        layout.setSpacing(20)
        self.vlayout = layout

    def on_thickness_changed(self):
        if self.thicknessSlider.hasFocus():
            self.thicknessChanged.emit(self.thicknessSlider.value())

    def showEvent(self, e) -> None:
        self.inpainter_panel.needInpaintChecker.setVisible(False)
        self.vlayout.addWidget(self.inpainter_panel)
        super().showEvent(e)


    def hideEvent(self, e) -> None:
        self.vlayout.removeWidget(self.inpainter_panel)
        self.inpainter_panel.needInpaintChecker.setVisible(True)
        return super().hideEvent(e)


class PenConfigPanel(Widget):
    thicknessChanged = pyqtSignal(int)
    colorChanged = pyqtSignal(list)
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.thicknessSlider = PaintQSlider(self.tr('pen thickness ') + 'value px', Qt.Horizontal)
        self.thicknessSlider.setFixedHeight(50)
        self.thicknessSlider.setRange(MIN_PEN_SIZE, MAX_PEN_SIZE)
        self.thicknessSlider.valueChanged.connect(self.on_thickness_changed)
        self.alphaSlider = PaintQSlider(self.tr('alpha value'), Qt.Horizontal)
        self.alphaSlider.setFixedHeight(50)
        self.alphaSlider.setRange(0, 255)
        self.alphaSlider.valueChanged.connect(self.on_alpha_changed)

        self.colorPicker = ColorPicker()
        self.colorPicker.colorChanged.connect(self.on_color_changed)
        
        color_label = ToolNameLabel(None, self.tr('Color'))
        alpha_label = ToolNameLabel(None, self.tr('Alpha'))
        color_layout = QHBoxLayout()
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.colorPicker)
        color_layout.addWidget(alpha_label)
        color_layout.addWidget(self.alphaSlider)
        
        thickness_layout = QHBoxLayout()
        thickness_label = ToolNameLabel(150, self.tr('Thickness'))
        thickness_layout.addWidget(thickness_label)
        thickness_layout.addWidget(self.thicknessSlider)
        thickness_layout.setSpacing(15)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(color_layout)
        layout.addLayout(thickness_layout)
        layout.setSpacing(30)

    def on_thickness_changed(self):
        if self.thicknessSlider.hasFocus():
            self.thicknessChanged.emit(self.thicknessSlider.value())

    def on_alpha_changed(self):
        if self.alphaSlider.hasFocus():
            alpha = self.alphaSlider.value()
            color = self.colorPicker.rgba()
            color[-1] = alpha
            self.colorPicker.setPickerColor(color)
            self.colorChanged.emit(color)

    def on_color_changed(self):
        color = self.colorPicker.rgba()
        self.colorChanged.emit(color)


class DrawingPanel(Widget):

    scale_tool_pos: QPointF = None

    def __init__(self, canvas: Canvas, inpainter_panel: InpaintConfigPanel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.dl_manager: DLManager = None
        self.canvas = canvas
        self.inpaint_stroke: StrokeItem = None
        self.scale_circle = QGraphicsEllipseItem()
        
        canvas.finish_painting.connect(self.on_finish_painting)
        canvas.finish_erasing.connect(self.on_finish_erasing)
        canvas.ctrl_relesed.connect(self.on_canvasctrl_released)
        canvas.begin_scale_tool.connect(self.on_begin_scale_tool)
        canvas.scale_tool.connect(self.on_scale_tool)
        canvas.end_scale_tool.connect(self.on_end_scale_tool)
        canvas.scalefactor_changed.connect(self.on_canvas_scalefactor_changed)

        self.currentTool: DrawToolCheckBox = None
        self.handTool = DrawToolCheckBox()
        self.handTool.setObjectName("DrawHandTool")
        self.handTool.checked.connect(self.on_use_handtool)
        self.inpaintTool = DrawToolCheckBox()
        self.inpaintTool.setObjectName("DrawInpaintTool")
        self.inpaintTool.checked.connect(self.on_use_inpainttool)
        self.inpaintConfigPanel = InpaintPanel(inpainter_panel)
        self.inpaintConfigPanel.thicknessChanged.connect(self.setInpaintToolWidth)

        self.rectTool = DrawToolCheckBox()
        self.rectTool.setObjectName("DrawRectTool")
        self.rectTool.checked.connect(self.on_use_rectremoval_tool)

        self.penTool = DrawToolCheckBox()
        self.penTool.setObjectName("DrawPenTool")
        self.penTool.checked.connect(self.on_use_pentool)
        self.penConfigPanel = PenConfigPanel()
        self.penConfigPanel.thicknessChanged.connect(self.setPenToolWidth)
        self.penConfigPanel.colorChanged.connect(self.setPenToolColor)

        toolboxlayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        toolboxlayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        toolboxlayout.addWidget(self.handTool)
        toolboxlayout.addWidget(self.inpaintTool)
        toolboxlayout.addWidget(self.penTool)
        toolboxlayout.addWidget(self.rectTool)

        self.canvas.painting_pen = self.pentool_pen = \
            QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

        self.inpaint_pen = QPen(INPAINT_BRUSH_COLOR, 1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

        self.setPenToolWidth(10)
        self.setPenToolColor([0, 0, 0, 127])

        self.toolConfigStackwidget = QStackedWidget()
        self.toolConfigStackwidget.addWidget(self.inpaintConfigPanel)
        self.toolConfigStackwidget.addWidget(self.penConfigPanel)

        self.maskTransperancySlider = PaintQSlider(' value%', Qt.Orientation.Horizontal)
        self.maskTransperancySlider.setFixedHeight(40)
        self.maskTransperancySlider.valueChanged.connect(self.canvas.setMaskTransparencyBySlider)
        masklayout = QHBoxLayout()
        masklayout.addWidget(ToolNameLabel(220, self.tr('Mask Transparency')))
        masklayout.addWidget(self.maskTransperancySlider)

        layout = QVBoxLayout(self)
        layout.addLayout(toolboxlayout)
        layout.addWidget(SeparatorWidget())
        layout.addWidget(self.toolConfigStackwidget)
        layout.addWidget(SeparatorWidget())
        layout.addLayout(masklayout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def initDLModule(self, dl_manager: DLManager):
        self.dl_manager = dl_manager
        dl_manager.canvas_inpaint_finished.connect(self.on_inpaint_finished)
        dl_manager.inpaint_thread.exception_occurred.connect(self.on_inpaint_failed)

    def setInpaintToolWidth(self, width):
        self.inpaint_pen.setWidth(width)
        if self.isVisible():
            self.setInpaintCursor()

    def setPenToolWidth(self, width):
        self.pentool_pen.setWidthF(width)
        if self.isVisible():
            self.setPenCursor()

    def setPenToolColor(self, color: Union[QColor, Tuple, List]):
        if not isinstance(color, QColor):
            color = QColor(*color)
        self.pentool_pen.setColor(color)
        if self.isVisible():
            self.setPenCursor()

    def on_use_handtool(self) -> None:
        if self.currentTool is not None and self.currentTool != self.handTool:
            self.currentTool.setChecked(False)
        self.toolConfigStackwidget.hide()
        self.currentTool = self.handTool
        self.canvas.gv.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.canvas.painting = False
        self.canvas.image_edit_mode = ImageEditMode.HandTool

    def on_use_inpainttool(self) -> None:
        if self.currentTool is not None and self.currentTool != self.inpaintTool:
            self.currentTool.setChecked(False)
        self.toolConfigStackwidget.show()
        self.currentTool = self.inpaintTool
        self.canvas.image_edit_mode = ImageEditMode.InpaintTool
        self.canvas.painting_pen = self.inpaint_pen
        self.toolConfigStackwidget.setCurrentWidget(self.inpaintConfigPanel)
        if self.isVisible():
            self.canvas.gv.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setInpaintCursor()
            self.canvas.painting = True

    def on_use_pentool(self) -> None:
        if self.currentTool is not None and self.currentTool != self.penTool:
            self.currentTool.setChecked(False)
        self.toolConfigStackwidget.show()
        self.currentTool = self.penTool
        self.canvas.painting_pen = self.pentool_pen
        self.canvas.image_edit_mode = ImageEditMode.PenTool
        self.toolConfigStackwidget.setCurrentWidget(self.penConfigPanel)
        if self.isVisible():
            self.canvas.gv.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setPenCursor()
            self.canvas.painting = True

    def on_use_rectremoval_tool(self) -> None:
        print('use rect removal tool')

    def get_config(self) -> DrawPanelConfig:
        config = DrawPanelConfig()
        pc = self.pentool_pen.color()
        config.pentool_color = [pc.red(), pc.green(), pc.blue(), pc.alpha()]
        config.pentool_width = self.pentool_pen.widthF()
        config.inpainter_width = self.inpaint_pen.widthF()
        if self.currentTool == self.handTool:
            config.current_tool = 0
        elif self.currentTool == self.inpaintTool:
            config.current_tool = 1
        elif self.currentTool == self.penTool:
            config.current_tool = 2
        return config

    def set_config(self, config: DrawPanelConfig):
        self.setPenToolWidth(config.pentool_width)
        self.penConfigPanel.thicknessSlider.setValue(config.pentool_width)
        self.setInpaintToolWidth(config.inpainter_width)
        self.inpaintConfigPanel.thicknessSlider.setValue(config.inpainter_width)
        self.setPenToolColor(config.pentool_color)
        self.penConfigPanel.colorPicker.setPickerColor(config.pentool_color)
        if config.current_tool == 0:
            self.handTool.setChecked(True)
        elif config.current_tool == 1:
            self.inpaintTool.setChecked(True)
        elif config.current_tool == 2:
            self.penTool.setChecked(True)

    def get_pen_cursor(self, pen_color: QColor = None, pen_size = None, draw_circle=True) -> QCursor:
        cross_size = 31
        cross_len = cross_size // 4
        thickness = 3
        if pen_color is None:
            pen_color = self.pentool_pen.color()
        if pen_size is None:
            pen_size = self.pentool_pen.width()
        pen_size *= self.canvas.scale_factor
        map_size = max(cross_size+7, pen_size)
        cursor_center = map_size // 2
        pen_radius = pen_size // 2
        pen_color.setAlpha(127)
        pen = QPen(pen_color, thickness, Qt.DotLine, Qt.RoundCap, Qt.RoundJoin)
        pen.setDashPattern([3, 6])
        if pen_size < 20:
            pen.setStyle(Qt.SolidLine)

        cur_pixmap = QPixmap(QSize(map_size, map_size))
        cur_pixmap.fill(Qt.transparent)
        painter = QPainter(cur_pixmap)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
        if draw_circle:
            painter.drawEllipse(cursor_center-pen_radius + thickness, 
                                cursor_center-pen_radius + thickness, 
                                pen_size - 2*thickness, 
                                pen_size - 2*thickness)
        cross_left = (map_size  - 1 - cross_size) // 2 
        cross_right = map_size - cross_left

        pen = QPen(Qt.GlobalColor.white, 5, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        cross_hline0 = QLineF(cross_left, cursor_center, cross_left+cross_len, cursor_center)
        cross_hline1 = QLineF(cross_right-cross_len, cursor_center, cross_right, cursor_center)
        cross_vline0 = QLineF(cursor_center, cross_left, cursor_center, cross_left+cross_len)
        cross_vline1 = QLineF(cursor_center, cross_right-cross_len, cursor_center, cross_right)
        painter.drawLines([cross_hline0, cross_hline1, cross_vline0, cross_vline1])
        pen.setWidth(3)
        pen.setColor(Qt.GlobalColor.black)
        painter.setPen(pen)
        painter.drawLines([cross_hline0, cross_hline1, cross_vline0, cross_vline1])
        painter.end()
        return QCursor(cur_pixmap)

    def on_incre_pensize(self):
        self.scalePen(1.1)

    def on_decre_pensize(self):
        self.scalePen(0.9)
        pass

    def scalePen(self, scale_factor):
        if self.currentTool == self.penTool:
            val = self.pentool_pen.widthF()
            new_val = round(int(val * scale_factor))
            if scale_factor > 1:
                new_val = max(val+1, new_val)
            else:
                new_val = min(val-1, new_val)
            self.penConfigPanel.thicknessSlider.setValue(new_val)
            self.setPenToolWidth(self.penConfigPanel.thicknessSlider.value())

        elif self.currentTool == self.inpaintTool:
            val = self.inpaint_pen.widthF()
            new_val = round(int(val * scale_factor))
            if scale_factor > 1:
                new_val = max(val+1, new_val)
            else:
                new_val = min(val-1, new_val)
            self.inpaintConfigPanel.thicknessSlider.setValue(new_val)
            self.setInpaintToolWidth(self.inpaintConfigPanel.thicknessSlider.value())

    def showEvent(self, event) -> None:
        if self.currentTool is not None:
            self.currentTool.setChecked(False)
            self.currentTool.setChecked(True)
        return super().showEvent(event)

    def on_finish_painting(self, stroke_item: StrokeItem):
        if not self.canvas.imgtrans_proj.img_valid:
            self.canvas.removeItem(stroke_item)
            return
        if self.currentTool == self.penTool:
            pass
        elif self.currentTool == self.inpaintTool:
            # stroke_item.convertToPixmapItem(remove_stroke=False, convert_mask=True)
            self.mergeInpaintStroke(stroke_item)
            if self.canvas.gv.ctrl_pressed:
                return
            else:
                self.runInpaint()

    def mergeInpaintStroke(self, inpaint_stroke: StrokeItem):
        if self.inpaint_stroke is None:
            self.inpaint_stroke = inpaint_stroke
        else:
            if not inpaint_stroke.isEmpty():
                self.inpaint_stroke.addStroke(inpaint_stroke.stroke)
            self.canvas.removeItem(inpaint_stroke)

    def runInpaint(self):

        if self.inpaint_stroke is None:
            return
        mask = self.inpaint_stroke.getSubimg(convert_mask=True)
        pos = self.inpaint_stroke.subBlockPos()
        if mask is None:
            self.canvas.removeItem(self.inpaint_stroke)
            self.inpaint_stroke = None
            return

        # we need to enlarge the mask window a bit to get better results
        mask_h, mask_w = mask.shape[:2]
        mask_x, mask_y = pos.x(), pos.y()
        img = self.canvas.imgtrans_proj.inpainted_array
        inpaint_rect = [mask_x, mask_y, mask_w + mask_x, mask_h + mask_y]
        rect_enlarged = enlarge_window(inpaint_rect, img.shape[1], img.shape[0])
        top = mask_y - rect_enlarged[1]
        bottom = rect_enlarged[3] - inpaint_rect[3]
        left = mask_x - rect_enlarged[0]
        right = rect_enlarged[2] - inpaint_rect[2]

        # print('inpaint_rect: ', inpaint_rect, 'enlarged: ', rect_enlarged, 'ltrb: ', left, top, right, bottom)
        mask = cv2.copyMakeBorder(mask, top, bottom, left, right, cv2.BORDER_CONSTANT, value=0)
        inpaint_rect = rect_enlarged
        img = img[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
        
        self.canvas.painting = False
        inpaint_dict = {'img': img, 'mask': mask, 'inpaint_rect': inpaint_rect}
        self.dl_manager.canvas_inpaint(inpaint_dict)

    def on_inpaint_finished(self, inpaint_dict):
        inpainted = inpaint_dict['inpainted']
        inpaint_rect = inpaint_dict['inpaint_rect']
        mask_array = self.canvas.imgtrans_proj.mask_array
        mask = cv2.bitwise_or(inpaint_dict['mask'], mask_array[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]])
        self.canvas.removeItem(self.inpaint_stroke)
        self.inpaint_stroke = None
        self.canvas.undoStack.push(InpaintUndoCommand(self.canvas, inpainted, mask, inpaint_rect))

        if self.currentTool == self.inpaintTool:
            self.canvas.painting = True

    def on_finish_erasing(self, stroke_item: StrokeItem):

        # inpainted-erasing logic is essentially the same as inpainting
        if self.currentTool == self.inpaintTool:
            mask = 255 - stroke_item.getSubimg(convert_mask=True)
            pos = stroke_item.subBlockPos()
            self.canvas.removeItem(stroke_item)
            if mask is None:
                return
            mask_h, mask_w = mask.shape[:2]
            mask_x, mask_y = pos.x(), pos.y()
            inpaint_rect = [mask_x, mask_y, mask_w + mask_x, mask_h + mask_y]
            origin = self.canvas.imgtrans_proj.img_array
            origin = origin[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
            inpainted = self.canvas.imgtrans_proj.inpainted_array
            inpainted = inpainted[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
            inpaint_mask = self.canvas.imgtrans_proj.mask_array[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
            # no inpainted need to be erased
            if inpaint_mask.sum() == 0:
                return
            mask = cv2.bitwise_and(mask, inpaint_mask)
            inpaint_mask = np.zeros_like(inpainted)
            inpaint_mask[mask > 0] = 1
            erased_img = inpaint_mask * inpainted + (1 - inpaint_mask) * origin
            self.canvas.undoStack.push(InpaintUndoCommand(self.canvas, erased_img, mask, inpaint_rect))

    def on_inpaint_failed(self):
        if self.currentTool == self.inpaintTool and self.inpaint_stroke is not None:
            self.canvas.painting = True
            self.canvas.removeItem(self.inpaint_stroke)
            self.inpaint_stroke = None

    def on_canvasctrl_released(self):
        if self.currentTool == self.inpaintTool:
            self.runInpaint()

    def on_begin_scale_tool(self, pos: QPointF):
        
        if self.currentTool == self.penTool:
            circle_pen = QPen(self.pentool_pen)
        elif self.currentTool == self.inpaintTool:
            circle_pen = QPen(self.inpaint_pen)
        else:
            return
        pen_radius = circle_pen.widthF() / 2 * self.canvas.scale_factor
        
        r, g, b, a = circle_pen.color().getRgb()

        circle_pen.setWidth(3)
        circle_pen.setStyle(Qt.PenStyle.DashLine)
        circle_pen.setDashPattern([3, 6])
        self.scale_circle.setPen(circle_pen)
        self.scale_circle.setBrush(QBrush(QColor(r, g, b, 127)))
        self.scale_circle.setPos(pos - QPointF(pen_radius, pen_radius))
        pen_size = 2 * pen_radius
        self.scale_circle.setRect(0, 0, pen_size, pen_size)
        self.scale_tool_pos = pos - QPointF(pen_size, pen_size)
        self.canvas.addItem(self.scale_circle)
        self.setCrossCursor()
        
    def setCrossCursor(self):
        self.canvas.gv.setCursor(self.get_pen_cursor(draw_circle=False))

    def on_scale_tool(self, pos: QPointF):
        if self.scale_tool_pos is None:
            return
        radius = pos.x() - self.scale_tool_pos.x()
        radius = max(min(radius, MAX_PEN_SIZE * self.canvas.scale_factor), MIN_PEN_SIZE * self.canvas.scale_factor)
        self.scale_circle.setRect(0, 0, radius, radius)

    def on_end_scale_tool(self):
        circle_size = self.scale_circle.rect().width() / self.canvas.scale_factor
        self.scale_tool_pos = None
        self.canvas.removeItem(self.scale_circle)

        if self.currentTool == self.penTool:
            self.setPenToolWidth(circle_size)
            self.penConfigPanel.thicknessSlider.setValue(circle_size)
            self.setPenCursor()
        elif self.currentTool == self.inpaintTool:
            self.setInpaintToolWidth(circle_size)
            self.inpaintConfigPanel.thicknessSlider.setValue(circle_size)
            self.setInpaintCursor()

    def on_canvas_scalefactor_changed(self):
        if not self.isVisible():
            return
        if self.currentTool == self.penTool:
            self.setPenCursor()
        elif self.currentTool == self.inpaintTool:
            self.setInpaintCursor()

    def setPenCursor(self):
        self.canvas.gv.setCursor(self.get_pen_cursor())

    def setInpaintCursor(self):
        self.canvas.gv.setCursor(self.get_pen_cursor(INPAINT_BRUSH_COLOR, self.inpaint_pen.width()))


class InpaintUndoCommand(QUndoCommand):
    def __init__(self, canvas: Canvas, inpainted: np.ndarray, mask: np.ndarray, inpaint_rect: list):
        super().__init__()
        self.canvas = canvas
        img_array = self.canvas.imgtrans_proj.inpainted_array
        mask_array = self.canvas.imgtrans_proj.mask_array
        img_view = img_array[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
        mask_view = mask_array[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
        self.undo_img = np.copy(img_view)
        self.undo_mask = np.copy(mask_view)
        self.redo_img = inpainted
        self.redo_mask = mask
        self.inpaint_rect = inpaint_rect

    def redo(self) -> None:
        inpaint_rect = self.inpaint_rect
        img_array = self.canvas.imgtrans_proj.inpainted_array
        mask_array = self.canvas.imgtrans_proj.mask_array
        img_view = img_array[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
        mask_view = mask_array[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
        img_view[:] = self.redo_img
        mask_view[:] = self.redo_mask
        self.canvas.setInpaintLayer()
        self.canvas.setMaskLayer()

    def undo(self) -> None:
        inpaint_rect = self.inpaint_rect
        img_array = self.canvas.imgtrans_proj.inpainted_array
        mask_array = self.canvas.imgtrans_proj.mask_array
        img_view = img_array[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
        mask_view = mask_array[inpaint_rect[1]: inpaint_rect[3], inpaint_rect[0]: inpaint_rect[2]]
        img_view[:] = self.undo_img
        mask_view[:] = self.undo_mask
        self.canvas.setInpaintLayer()
        self.canvas.setMaskLayer()