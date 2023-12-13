from .applets import AppletBase
import json

class MergeLora(AppletBase):

    applet_name = "prompt_seed_interpolate"
    applet_title = "Interpolate Prompts and Seeds"

    def get_input_form(self):
        return []
    
    def run(self , params ):
        self.update_state("outputs" , [] )