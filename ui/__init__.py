# from kivy.properties import BooleanProperty
# from kivy.uix.widget import Widget, WidgetException
#
# Widget.__events__ = (
#     'on_motion', 'on_touch_down', 'on_touch_move', 'on_touch_up',
#     'on_kv_post', 'on_ancestor_dead', 'on_ancestor_alive'
# )
#
#
# def add_widget(self, widget, index=0, canvas=None):
#     if not isinstance(widget, Widget):
#         raise WidgetException(
#             'add_widget() can be used only with instances'
#             ' of the Widget class.')
#
#     widget = widget.__self__
#     if widget is self:
#         raise WidgetException(
#             'Widget instances cannot be added to themselves.')
#     parent = widget.parent
#     # Check if the widget is already a child of another widget.
#     if parent:
#         raise WidgetException('Cannot add %r, it already has a parent %r'
#                               % (widget, parent))
#     widget.parent = parent = self
#     # Child will be disabled if added to a disabled parent.
#     widget.inc_disabled(self._disabled_count)
#
#     canvas = self.canvas.before if canvas == 'before' else \
#         self.canvas.after if canvas == 'after' else self.canvas
#
#     if index == 0 or len(self.children) == 0:
#         self.children.insert(0, widget)
#         canvas.add(widget.canvas)
#     else:
#         canvas = self.canvas
#         children = self.children
#         if index >= len(children):
#             index = len(children)
#             next_index = canvas.indexof(children[-1].canvas)
#         else:
#             next_child = children[index]
#             next_index = canvas.indexof(next_child.canvas)
#             if next_index == -1:
#                 next_index = canvas.length()
#             else:
#                 next_index += 1
#
#         children.insert(index, widget)
#         # We never want to insert widget _before_ canvas.before.
#         if next_index == 0 and canvas.has_before:
#             next_index = 1
#         canvas.insert(next_index, widget.canvas)
#     for type_id in widget.motion_filter:
#         self.register_for_motion_event(type_id, widget)
#     widget.fbind('motion_filter', self._update_motion_filter)
#     for child in widget.walk():
#         child.dispatch("on_ancestor_alive", widget)
#     widget.dec_disabled(self._disabled_count)
#
#
# def remove_widget(self, widget):
#     if widget not in self.children:
#         return
#     self.children.remove(widget)
#     if widget.canvas in self.canvas.children:
#         self.canvas.remove(widget.canvas)
#     elif widget.canvas in self.canvas.after.children:
#         self.canvas.after.remove(widget.canvas)
#     elif widget.canvas in self.canvas.before.children:
#         self.canvas.before.remove(widget.canvas)
#     for type_id in widget.motion_filter:
#         self.unregister_for_motion_event(type_id, widget)
#     widget.funbind('motion_filter', self._update_motion_filter)
#     widget.parent = None
#     for child in widget.walk():
#         child.dispatch("on_ancestor_dead")
#     widget.dec_disabled(self._disabled_count)
#
#
# def on_ancestor_dead(self):
#     pass
#
#
# def on_ancestor_alive(self, *args):
#     pass
#
#
# Widget.on_ancestor_dead = on_ancestor_dead
# Widget.on_ancestor_alive = on_ancestor_alive
# Widget.remove_widget = remove_widget
# Widget.add_widget = add_widget
