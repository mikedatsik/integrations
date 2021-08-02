from ftrack_connect_pipeline_qt import constants
from ftrack_connect_pipeline_qt.client.widgets.experimental import BaseUIWidget
from ftrack_connect_pipeline_qt.ui.utility.widget.accordion import AccordionWidget

class AccordionStepWidget(BaseUIWidget):
    '''Widget representation of a boolean'''
    def __init__(self, name, fragment_data, parent=None):
        '''Initialise JsonBoolean with *name*, *schema_fragment*,
        *fragment_data*, *previous_object_data*, *widget_factory*, *parent*'''

        self.step_optional = False

        super(AccordionStepWidget, self).__init__(
            name, fragment_data, parent=parent
        )

    def pre_build(self):
        self.step_optional = self.fragment_data.get('optional')

    def build(self):
        self._widget = AccordionWidget(
            title=self.name, checkable=self.step_optional
        )

    def parent_widget(self, step_widget):
        if self.widget:
            if hasattr(step_widget, 'widget'):
                self.widget.add_widget(step_widget.widget)
            else:
                self.widget.add_widget(step_widget)
        else:
            self.logger.error("Please create a widget before parent")