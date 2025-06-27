# from .color_swatch_docker import ColorSwatchDocker
# from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase
#
# dockFactory = DockWidgetFactory(
#     "color_swatch_docker",
#     DockWidgetFactoryBase.DockRight,
#     ColorSwatchDocker
# )
#
# Krita.instance().addDockWidgetFactory(dockFactory)


from .color_swatch_docker import BrushPreviewDocker
from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase

def createDockWidget():
    return BrushPreviewDocker()

dockFactory = DockWidgetFactory(
    "brush_preview_docker",  # Must match the objectName in the Docker class
    DockWidgetFactoryBase.DockRight,
    BrushPreviewDocker
)

Krita.instance().addDockWidgetFactory(dockFactory)
