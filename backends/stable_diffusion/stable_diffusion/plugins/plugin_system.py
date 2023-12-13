

class StableDiffusionPluginMixin:

    def plugin_system_init(self):
        self.hooks = {}

        

    def register_hook(self, fn_name , fn_stage, function):
        hook_ident = fn_name + "_" + fn_stage
        print("[SD] registered" , hook_ident)
        if hook_ident not in self.hooks:
            self.hooks[hook_ident] = []
        self.hooks[hook_ident].append(function)

    def run_plugin_hook( self, fn_name , fn_stage, sd_run, *args , **kwargs ):
        hook_ident = fn_name + "_" + fn_stage
        if hook_ident not in self.hooks:
            return
        for fn in self.hooks[hook_ident]:
            fn(sd_run , *args , **kwargs)

    def add_plugin(self , plugin_class):
        plugin_object = plugin_class(parent=self)
        hooks_list = [method for method in dir(plugin_object) if method.startswith('hook_')]

        print(hooks_list)

        for hook in hooks_list:
            hook_stage = hook.split("_")[1]
            hook_fn_name = "_".join(hook.split("_")[2:])

            hook_fn = getattr(plugin_object , hook)

            self.register_hook(hook_fn_name , hook_stage , hook_fn )

    
