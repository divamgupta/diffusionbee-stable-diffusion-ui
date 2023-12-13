from tdict import TDict
from .extra_model_utils import add_lora_ti_weights, clip_skip_2_patch_weights


def load_weights_model(model_container, weights_config):
    assert model_container.model_config[0] == "SD_normal"
    assert model_container.model_type == "SD_normal"

    if model_container.weights_config == weights_config:
        return

    tdict_path, second_tdict_path, weight_additions = weights_config
    cur_tdict_path, cur_second_tdict_path, cur_weight_additions = model_container.weights_config

    tdict_1 = None

    if tdict_path == cur_tdict_path and second_tdict_path == cur_second_tdict_path and cur_weight_additions == ():
        # the main tdicts are already loaded, just load the additional weights
        pass 
    else:
        if second_tdict_path is not None:
            tdict2 = TDict(second_tdict_path)
        else:
            tdict2 = None
        tdict_1 = TDict(tdict_path)
        print("[SD] Loading weights")
        model_container.model.load_from_tdict(tdict_1, tdict2 )
        model_container.weights_config = tdict_path, second_tdict_path, ()

    if weight_additions is not None and weight_additions != ():
        if tdict_1 is None:
            tdict_1 = TDict(tdict_path)
        
        print("[SD] Loading LoRA weights")
        extra_weights = add_lora_ti_weights(tdict_1 , weight_additions )
        extra_weights = clip_skip_2_patch_weights(tdict_1 , weight_additions, extra_weights )


        model_container.model.load_from_state_dict(extra_weights )
        model_container.weights_config = tdict_path, second_tdict_path, extra_weights

def create_sd_model_with_weights(ModelInterfaceClass, model_container, model_config, weights_config):
    model_type, model_name, dtype = model_config
    tdict_path, second_tdict_path, weight_additions = weights_config

    assert model_type == "SD_normal"

    if model_container.model_config != model_config:
        model_container.reset()
        print("[SD] Creating model interface")
        assert tdict_path is not None

        if second_tdict_path is not None:
            tdict2 = TDict(second_tdict_path)
        else:
            tdict2 = None

        model_container.model = ModelInterfaceClass(TDict(tdict_path ) , dtype=dtype, model_name=model_name , second_tdict=tdict2)
        model_container.model_type = "SD_normal"
        model_container.model_config = model_type, model_name, dtype
        model_container.weights_config = tdict_path, second_tdict_path, ()

    load_weights_model(model_container , weights_config)


