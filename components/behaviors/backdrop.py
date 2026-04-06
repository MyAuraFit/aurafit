__all__ = ("BackdropBehavior",)

from functools import partial

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    OptionProperty,
    StringProperty,
    ObjectProperty,
)


class BackdropBehavior:
    anchor = OptionProperty("bottom", options=("left", "right", "top", "bottom"))
    """
    Anchoring screen edge for backdrop. Set it to `'right'` for right-to-left
    languages. Available options are: `'left'`, `'right'`.

    :attr:`anchor` is a :class:`~kivy.properties.OptionProperty`
    and defaults to `'left'`.
    """

    close_on_click = BooleanProperty(True)
    """
    Close when click on scrim or keyboard escape. It automatically sets to
    False for "standard" type.

    :attr:`close_on_click` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to `True`.
    """

    open_on_click = BooleanProperty(False)

    state = OptionProperty("open", options=("close", "open"))
    """
    Indicates if panel closed or opened. Sets after :attr:`status` change.
    Available options are: `'close'`, `'open'`.

    :attr:`state` is a :class:`~kivy.properties.OptionProperty`
    and defaults to `'close'`.
    """

    status = OptionProperty(
        "opened",
        options=(
            "closed",
            "opening_with_swipe",
            "opening_with_animation",
            "opened",
            "closing_with_swipe",
            "closing_with_animation",
        ),
    )  #
    """
    Detailed state. Sets before :attr:`state`. Bind to :attr:`state` instead
    of :attr:`status`. Available options are: `'closed'`,
    `'opening_with_swipe'`, `'opening_with_animation'`, `'opened'`,
    `'closing_with_swipe'`, `'closing_with_animation'`.

    :attr:`status` is a :class:`~kivy.properties.OptionProperty`
    and defaults to `'closed'`.
    """

    open_progress = NumericProperty(1.0)
    """
    Percent of visible part of side panel. The percent is specified as a
    floating point number in the range 0-1. 0.0 if panel is closed and 1.0 if
    panel is opened.

    :attr:`open_progress` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.0`.
    """

    enable_swiping = BooleanProperty(True)
    """
    Allow to open or close navigation drawer with swipe. It automatically
    sets to False for "standard" type.

    :attr:`enable_swiping` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to `True`.
    """

    swipe_distance = NumericProperty(10)
    """
    The distance of the swipe with which the movement of navigation drawer
    begins.

    :attr:`swipe_distance` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `10`.
    """

    swipe_edge_width = NumericProperty(20)
    """
    The size of the area in px inside which should start swipe to drag
    navigation drawer.

    :attr:`swipe_edge_width` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `20`.
    """

    opening_transition = StringProperty("out_cubic")
    """
    The name of the animation transition type to use when animating to
    the :attr:`state` `'open'`.

    :attr:`opening_transition` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'out_cubic'`.
    """

    opening_time = NumericProperty(0.5)
    """
    The time taken for the panel to slide to the :attr:`state` `'open'`.

    :attr:`opening_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.2`.
    """

    closing_transition = StringProperty("out_sine")
    """The name of the animation transition type to use when animating to
    the :attr:`state` 'close'.

    :attr:`closing_transition` is a :class:`~kivy.properties.StringProperty`
    and defaults to `'out_sine'`.
    """

    closing_time = NumericProperty(0.5)
    """
    The time taken for the panel to slide to the :attr:`state` `'close'`.

    :attr:`closing_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to `0.2`.
    """

    scroll_timeout = NumericProperty(200)
    """Timeout allowed to trigger the :attr:`scroll_distance`, in milliseconds.
    If the user has not moved :attr:`scroll_distance` within the timeout,
    no scrolling will occur and the touch event will go to the children.

    :attr:`scroll_timeout` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 200 (milliseconds)
    """

    scroll_distance = NumericProperty("20dp")
    """Distance to move before scrolling the :class:`Carousel` in pixels. As
    soon as the distance has been traveled, the :class:`Carousel` will start
    to scroll, and no touch event will go to children.
    It is advisable that you base this value on the dpi of your target device's
    screen.

    :attr:`scroll_distance` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 20dp.
    """

    max_close_size = NumericProperty("50dp")

    disable_swipe = BooleanProperty(False)

    _x = NumericProperty(None, allownone=True)
    _y = NumericProperty(None, allownone=True)
    _touch = ObjectProperty(None, allownone=True)

    __events__ = ("on_open", "on_close")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            open_progress=self.update_status,
            status=self.update_status,
            state=self.update_status,
        )

    def set_state(self, new_state="toggle", animation=True) -> None:
        """
        Change state of the side panel.
        New_state can be one of `"toggle"`, `"open"` or `"close"`.
        """

        if new_state == "toggle":
            new_state = "close" if self.state == "open" else "open"

        if new_state == "open":
            Animation.cancel_all(self, "open_progress")
            self.status = "opening_with_animation"
            if animation:
                anim = Animation(
                    open_progress=1.0,
                    d=self.opening_time * (1 - self.open_progress),
                    t=self.opening_transition,
                )
                anim.bind(on_complete=self._check_state)
                anim.start(self)
            else:
                self.open_progress = 1
        else:  # "open"
            Animation.cancel_all(self, "open_progress")
            self.status = "closing_with_animation"
            if animation:
                anim = Animation(
                    open_progress=0.0,
                    d=self.closing_time * self.open_progress,
                    t=self.closing_transition,
                )
                anim.bind(on_complete=self._check_state)
                anim.start(self)
            else:
                self.open_progress = 0

    def update_status(self, *args) -> None:
        status = self.status
        if status == "closed":
            self.state = "close"
        elif status == "opened":
            self.state = "open"
        elif self.open_progress == 1 and status == "opening_with_animation":
            self.status = "opened"
            self.state = "open"
        elif self.open_progress == 0 and status == "closing_with_animation":
            self.status = "closed"
            self.state = "close"
        elif status in (
            "opening_with_swipe",
            "opening_with_animation",
            "closing_with_swipe",
            "closing_with_animation",
        ):
            pass
        # if self.status == "closed":
        #     self.opacity = 0
        # else:
        #     self.opacity = 1

        if self._x is None and self._y is None:
            self._x = self.x
            self._y = self.y
        pw = self.parent.width
        ph = self.parent.height
        w = self.width
        h = self.height
        if self.anchor == "left":
            wb = pw - w
            self.x = (w - wb) * (self.open_progress - 1)
        elif self.anchor == "right":
            x = Window.width - self.width * self.open_progress
            self.x = (self._x - w) * (self.open_progress - 1)
        elif self.anchor == "top":
            self.y = (self._y - h) * (self.open_progress - 1)
        elif self.anchor == "bottom":
            self.y = max(h * (self.open_progress - 1), self.max_close_size - h)

    def get_dist_from_side(self, direction: float) -> float:
        if self.anchor in ["left", "bottom"]:
            return 0 if direction < 0 else direction
        elif self.anchor == "right":
            return 0 if direction > Window.width else Window.width - direction
        else:
            return 0 if direction > Window.height else Window.height - direction

    def _get_uid(self, prefix="bd"):
        return "{0}.{1}".format(prefix, self.uid)

    def on_touch_down(self, touch):
        if self.disable_swipe:
            return super().on_touch_down(touch)
        if not self.collide_point(*touch.pos):
            touch.ud[self._get_uid("cavoid")] = True
            return
        if self.disabled:
            return True
        if self._touch:
            return super().on_touch_down(touch)
        self._touch = touch
        uid = self._get_uid()
        touch.grab(self)
        touch.ud[uid] = {"mode": "unknown", "time": touch.time_start}
        self._change_touch_mode_ev = Clock.schedule_once(
            self._change_touch_mode, self.scroll_timeout / 1000.0
        )
        return True

    def on_touch_move(self, touch):
        if self.disable_swipe:
            return super().on_touch_move(touch)
        if self._get_uid("cavoid") in touch.ud:
            return
        if self._touch is not touch:
            super().on_touch_move(touch)
            return self._get_uid() in touch.ud
        if touch.grab_current is not self:
            return True
        ud = touch.ud[self._get_uid()]
        direction = self.anchor[0]
        if ud["mode"] == "unknown":
            if direction in "rl":
                distance = abs(touch.ox - touch.x)
            else:
                distance = abs(touch.oy - touch.y)
            if distance > self.scroll_distance:
                ev = self._change_touch_mode_ev
                if ev is not None:
                    ev.cancel()
                ud["mode"] = "scroll"
        else:
            if self.anchor in ["left", "right"]:
                d = touch.x
                od = touch.ox
                dd = touch.dx
            else:
                d = touch.y
                od = touch.oy
                dd = touch.dy
            if self.enable_swiping:
                if self.status == "opened":
                    if (
                        self.get_dist_from_side(od) >= self.swipe_edge_width
                        and abs(d - od) > self.swipe_distance
                        and self.collide_point(touch.ox, touch.oy)
                    ):
                        self.status = "closing_with_swipe"
                elif self.status == "closed" and self.collide_point(touch.ox, touch.oy):
                    if abs(d - od) > self.swipe_distance:
                        self.status = "opening_with_swipe"

            if self.status in ("opening_with_swipe", "closing_with_swipe"):
                self.open_progress = max(
                    min(
                        self.open_progress
                        + (dd if self.anchor in ["left", "bottom"] else -dd)
                        / self.width,
                        1,
                    ),
                    0,
                )
                return True
        return True

    def on_touch_up(self, touch):
        if self.disable_swipe:
            return super().on_touch_up(touch)
        if self._get_uid("cavoid") in touch.ud:
            return
        if self in [x() for x in touch.grab_list]:
            touch.ungrab(self)
            self._touch = None
            ud = touch.ud[self._get_uid()]
            if ud["mode"] == "unknown":
                ev = self._change_touch_mode_ev
                if ev is not None:
                    ev.cancel()
                super().on_touch_down(touch)
                Clock.schedule_once(partial(self._do_touch_up, touch), 0.1)
                if self.status == "opened":
                    if self.close_on_click and self.collide_point(touch.ox, touch.oy):
                        self.set_state("close", animation=True)
                elif self.status == "closed":
                    if self.open_on_click and self.collide_point(touch.ox, touch.oy):
                        self.set_state("open", animation=True)
            else:
                if self.status == "opening_with_swipe":
                    if self.open_progress < 0.8:
                        self.set_state("open", animation=True)
                    else:
                        self.set_state("close", animation=True)
                elif self.status == "closing_with_swipe":
                    if self.open_progress > 0.2:
                        self.set_state("close", animation=True)
                    else:
                        self.set_state("open", animation=True)
                elif self.status == "opened":
                    if self.close_on_click and self.collide_point(touch.ox, touch.oy):
                        self.set_state("close", animation=True)
                    elif not self.collide_point(touch.ox, touch.oy):
                        return False
                elif self.status == "closed":
                    return False
                return super().on_touch_up(touch)

        else:
            if self._touch is not touch and self.uid not in touch.ud:
                super().on_touch_up(touch)
        return self._get_uid() in touch.ud

    def _do_touch_up(self, touch, *largs):
        super().on_touch_up(touch)
        # don't forget about grab event!
        for x in touch.grab_list[:]:
            touch.grab_list.remove(x)
            x = x()
            if not x:
                continue
            touch.grab_current = x
            super().on_touch_up(touch)
        touch.grab_current = None

    def _check_state(self, *args):
        if self.state == "open":
            self.dispatch("on_open")
        elif self.state == "close":
            self.dispatch("on_close")

    def _change_touch_mode(self, *largs):
        if not self._touch:
            return
        uid = self._get_uid()
        touch = self._touch
        ud = touch.ud[uid]
        if ud["mode"] == "unknown":
            touch.ungrab(self)
            self._touch = None
            super().on_touch_down(touch)
            return

    def on_open(self):
        pass

    def on_close(self):
        pass
