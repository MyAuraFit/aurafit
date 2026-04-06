__all__ = ("CoverImage",)

from kivy import resources
from kivy.clock import triggered
from kivy.core.image import Image as CoreImage
from kivy.loader import Loader
from kivy.logger import Logger
from kivy.properties import StringProperty, OptionProperty
from kivy.uix.image import AsyncImage

from components.behaviors.stencil import StencilBehavior


class CoverImage(AsyncImage, StencilBehavior):
    fit_mode = OptionProperty(
        "cover", options=["scale-down", "fill", "contain", "cover"]
    )
    loading_image = StringProperty()

    @triggered(1)
    def try_load_image(self):
        self.reload()

    def on_error(self, error):
        self.try_load_image()

    def _load_source(self, *args):
        source = self.source
        if not source:
            self._clear_core_image()
            return
        if not self.is_uri(source):
            source = resources.resource_find(source)
            if not source:
                Logger.error("AsyncImage: Not found <%s>" % self.source)
                self._clear_core_image()
                return
        self._found_source = source
        self._coreimage = image = Loader.image(
            source, nocache=self.nocache, mipmap=self.mipmap, anim_delay=self.anim_delay
        )
        image.bind(
            on_load=self._on_source_load,
            on_error=self._on_source_error,
            on_texture=self._on_tex_change,
        )
        if self.loading_image and not image.loaded:
            self.texture = CoreImage(self.loading_image).texture
        elif self.texture:
            pass
        else:
            self.texture = image.texture

    @property
    def is_loaded(self):
        return self._coreimage and self._coreimage.loaded
        # data = Cache.get("kv.loader", self.source)
        # if not self.source:
        #     return False
        # if data not in (None, False):
        #     return True
        # return False
