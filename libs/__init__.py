# This package is for additional application modules.
from kivy.clock import Clock, triggered
from kivy.core.text import DEFAULT_FONT
from kivy.metrics import sp

from components.label import CustomLabel
from libs.decorator import android_only

lbl = None


def shorten_text(
    text,
    lbl_width,
    lines=1,
    suffix="... See more",
    font_size=sp(12),
    font_name=DEFAULT_FONT,
):
    """
    Used to shorten text in kivy to number of lines you want unlike kivy which only shortens for
    one line

    :param font_name:
    :param text: text to shorten
    :param lbl_width: width of the original label containing the text to shorten
    :param lines: number of lines to shorten to
    :param suffix: suffix to add at the end of the text (e.g "suffix=.... see more")
    :param font_size: font_size of the original label containing the text to shorten
    :return: returns shorten text
    """
    global lbl
    if not lbl:
        lbl = CustomLabel(markup=True)
    text = text.split("\n")[0]
    lbl.text = text
    lbl.adaptive_width = True
    lbl.font_name = font_name
    lbl.font_size = font_size
    lbl.texture_update()
    text_width = lbl.width
    new_text = text
    t = 0
    lbl_width *= lines
    if lbl_width <= 0:
        lbl.adaptive_width = False
        return ""
    while text_width > lbl_width:
        new_text = new_text.split(" ")
        del new_text[-1]
        new_text = " ".join(new_text)
        lbl.text = new_text
        lbl.texture_update()
        text_width = lbl.width
        if text_width == t:
            lbl.adaptive_width = False
            return ""
        t = text_width
    lbl.adaptive_width = False
    return new_text + suffix


def compute_text_size(
    text,
    font_size,
    padding,
    widget_width,
    force_width=False,
    font_name=DEFAULT_FONT,
    halign="left",
):
    global lbl
    if not isinstance(padding, list) or len(padding) < 4:
        raise TypeError("padding must be a list and of length 4")
    if not lbl:
        lbl = CustomLabel(markup=True)
    lbl.adaptive_size = True
    lbl.halign = halign
    lbl.text = text
    lbl.font_size = font_size
    lbl.padding = padding
    lbl.font_name = font_name
    if force_width:
        lbl.adaptive_size = False
        lbl.width = widget_width
        lbl.texture_update()
        lbl.halign = "left"
        return lbl.texture_size
    lbl.texture_update()
    width = lbl.texture_size[0]
    if width > (widget_width - (padding[0] + padding[2])):
        lbl.adaptive_size = False
        lbl.width = widget_width
        lbl.texture_update()
    lbl.adaptive_size = False
    lbl.halign = "left"
    return lbl.texture_size


def get_dict_pos(lst, key, value):
    return next((index for (index, d) in enumerate(lst) if d[key] == value), None)


def search_dict(search_term, data_key, data, case_sensitive=False):
    if case_sensitive:
        a = filter(lambda search_found: search_term in search_found[data_key], data)
    else:
        a = filter(
            lambda search_found: search_term.lower() in search_found[data_key].lower(),
            data,
        )
    return list(a)


@triggered(0, interval=True)
def push_up_textinput(
    widget,
    scrollview=None,
    child=None,
    default_pad=None,
    focus=False,
    style="padding",
    cut_off=0,
):
    if default_pad is None:
        default_pad = [0, 0, 0, 0]
    from kvdroid.tools import check_keyboad_visibility_and_get_height

    visible, height = check_keyboad_visibility_and_get_height()
    if focus and not visible:
        return
    if style == "padding":
        widget.padding = (
            [*default_pad[:3], height + (default_pad[-1] / 2)] if focus else default_pad
        )
        if child and scrollview and focus:
            Clock.schedule_once(lambda _: scrollview.scroll_to(child))
    else:
        widget.y = height - cut_off if focus else 0
    push_up_textinput.cancel()
