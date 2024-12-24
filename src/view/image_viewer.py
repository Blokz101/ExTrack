"""
Contains the ImageViewer class which allows the user to view, zoom, and pan images.
"""

from typing import Any
from pathlib import Path
from PySimpleGUI import Column, Element, Button, Window
from PySimpleGUI import Image as GuiImage
from typing import Optional
from PIL import Image


class ImageViewer(Column):

    GUI_IMAGE_KEY: str = "-IMAGE-"
    ZOOM_IN_BUTTON_KEY: str = "-ZOOM IN BUTTON-"
    ZOOM_OUT_BUTTON_KEY: str = "-ZOOM OUT BUTTON-"

    def __init__(self, width: int = 500, height: int = 500, key: Optional[str] = None):
        """
        :param width: Width of the image element.
        :param height: Height of the image element.
        """

        self.image_path: Optional[Path] = None
        """Path to image to be displayed."""

        self.zoom_level: int = 0
        """Number of times the user has clicked zoom in minus the number of times the user has clicked zoom out."""

        self.width: int = width
        """Width of the image element."""

        self.height: int = height
        """Height of the image element."""

        self.window: Optional[Window] = None
        """Window that this element is in."""

        self.zoom_level: int = 0
        """Zoom level, gets multiplied by ZOOM_INCREMENTS to find the target width of the image."""

        self.image_element: GuiImage
        """Image element."""

        self.scroll_column_element: Column
        """Scroll column element that contains the image element."""

        super().__init__(
            layout=self._layout_generator(), expand_x=True, expand_y=True, key=key
        )

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the window.

        :return: Layout for the window
        """
        self.image_element = GuiImage(key=ImageViewer.GUI_IMAGE_KEY)
        self.scroll_column_element = Column(
            layout=[[self.image_element]],
            expand_x=True,
            expand_y=True,
            scrollable=True,
            size=(self.width, self.height),
        )
        return [
            [self.scroll_column_element],
            [
                Button("Zoom In", key=ImageViewer.ZOOM_IN_BUTTON_KEY, expand_x=True),
                Button("Zoom Out", key=ImageViewer.ZOOM_OUT_BUTTON_KEY, expand_x=True),
            ],
        ]

    def set_image(self, image_path: Optional[Path], window: Window) -> None:
        """
        Sets the image viewer to display a specific image.

        :param image_path: Path to the image to display
        :param window: Window that this element is in
        """
        if (
            image_path is None
            or not image_path.exists()
            or not image_path.suffix.lower() == ".png"
        ):
            self.image_path = None
            self._update_image()
            return

        with Image.open(image_path) as img:
            self.image_path = image_path
            scale = img.width / self.width
            if scale > 1:
                self.zoom_level = -int(scale - 1)
            if scale < 1:
                self.zoom_level = int(1 / scale + 1)

        self.window = window
        self._update_image()

    def event_loop_callback(self, event: Any, values: dict) -> None:
        """
        Function that should be called every event loop to respond to these elements events when required.

        :param event: Event that occurred
        :param values: Values for event
        """

        if event == ImageViewer.ZOOM_IN_BUTTON_KEY:
            self.zoom_level += 1
            self._update_image()
            return

        if event == ImageViewer.ZOOM_OUT_BUTTON_KEY:
            self.zoom_level -= 1
            self._update_image()
            return

    def _update_image(self, ) -> None:
        """
        Updates the image element using instance variables set before this call.
        """
        if self.window is None:
            return

        if self.image_path is None:
            self.image_element.update(source=None)

        else:
            zoom, subsample = self._get_zoom_and_subsample()
            self.image_element.update(
                source=str(self.image_path.absolute()),
                zoom=zoom,
                subsample=subsample,
            )
        self.window.refresh()
        self.scroll_column_element.contents_changed()

    def _get_zoom_and_subsample(self) -> tuple[Optional[int], Optional[int]]:
        """
        Calculates the PySimpleGui Image zoom and subsample values.

        :returns: Zoom and subsample values
        """
        if self.zoom_level > 0:
            return self.zoom_level + 1, None

        if self.zoom_level < 0:
            return None, abs(self.zoom_level) + 1

        return None, None
