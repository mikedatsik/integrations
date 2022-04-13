# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack
import logging

from Qt import QtWidgets

from ftrack_connect_pipeline_qt.ui.client import BaseUIWidget
from ftrack_connect_pipeline_qt.ui.utility.widget.base.accordion_base import (
    AccordionBaseWidget,
)


class PluginAccordion(AccordionBaseWidget):
    @property
    def options_widget(self):
        return self._options_button

    def __init__(self, title=None, checkable=False, parent=None):
        super(PluginAccordion, self).__init__(
            AccordionBaseWidget.SELECT_MODE_NONE,
            AccordionBaseWidget.CHECK_MODE_CHECKBOX
            if checkable
            else AccordionBaseWidget.CHECK_MODE_CHECKBOX_DISABLED,
            visible=False,
            title=title,
            parent=parent,
        )

    def init_header_content(self, header_widget, collapsed):
        '''Add publish related widgets to the accordion header'''
        header_layout = QtWidgets.QHBoxLayout()
        header_widget.setLayout(header_layout)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.addStretch()

    def on_collapse(self, collapsed):
        '''Callback on accordion collapse/expand.'''
        pass

    def update_input(self, message, status):
        '''(Override)'''
        pass


class AccordionPluginContainerWidget(BaseUIWidget):
    '''Widget representation of a boolean'''

    def __init__(self, name, fragment_data, parent=None):
        '''Initialise JsonBoolean with *name*, *schema_fragment*,
        *fragment_data*, *previous_object_data*, *widget_factory*, *parent*'''
        super(AccordionPluginContainerWidget, self).__init__(
            name, fragment_data, parent=parent
        )

    def build(self):
        self._widget = PluginAccordion(
            title=self.name, checkable=True, parent=self.parent
        )

    def parent_widget(self, widget):
        if self.widget:
            widget = (
                widget.widget if isinstance(widget, BaseUIWidget) else widget
            )
            self.widget.add_widget(widget)
        else:
            self.logger.error("Please create a widget before parent")
