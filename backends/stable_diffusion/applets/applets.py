import json

def update_state_raw(key , val ):
    print( "utds " +  key + "___U_P_D_A_T_E___" + json.dumps(val))


registered_applets = {}

def register_applet(model_container, applet_cls):
    applet_name = applet_cls.applet_name
    applet = applet_cls()
    applet.init_applet(model_container)
    registered_applets[applet_name] = applet

def run_applet(applet_name , params_dict):
    registered_applets[applet_name].run(params_dict)


class AppletBase:

    applet_name = None
    applet_title = None
    is_stop_avail = False
    applet_description = ""
    applet_icon = "file"
    applet_icon_fname = None
    
    def run(self, params):
        raise NotImplementedError("base cls")

    def get_input_form(self):
        return []
    
    def update_output( self, key , val ):
        self.update_state( "outputs." + key , val)

    def update_state(self , key  , val ):
        key = "registered_ext_applets." + self.applet_name + "." +  key
        update_state_raw(key , val)

    def init_applet(self, model_container):

        self.model_container = model_container

        update_state_raw( "registered_ext_applets." + self.applet_name , {})
        update_state_raw( "registered_ext_applets." + self.applet_name + ".id" ,  self.applet_name)
        update_state_raw( "registered_ext_applets." + self.applet_name + ".title" ,  self.applet_title)
        update_state_raw( "registered_ext_applets." + self.applet_name + ".description" ,  self.applet_description)
        update_state_raw( "registered_ext_applets." + self.applet_name + ".icon" ,  self.applet_icon )
        if self.applet_icon_fname is not None:
            update_state_raw( "registered_ext_applets." + self.applet_name + ".img_icon" ,  self.applet_icon_fname )        
        update_state_raw( "registered_ext_applets." + self.applet_name + ".home_category" ,  "misc")
        update_state_raw( "registered_ext_applets." + self.applet_name + ".inputs" ,   self.get_input_form() )
        update_state_raw( "registered_ext_applets." + self.applet_name + ".outputs" ,   [] )
        update_state_raw( "registered_ext_applets." + self.applet_name + ".is_stop_avail" ,   self.is_stop_avail )


        
