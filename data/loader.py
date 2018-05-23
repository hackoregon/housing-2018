from data.loaders.jchs_data_2017 import load_data as load_jchs_data
from data.loaders.hud_homelessness import load_data as load_hud_data
from data.loaders.urbaninstitute_rentalcrisis import load_data as load_urbaninstitute_data
from data.loaders.policy_inventory import load_data as load_policy_data

load_jchs_data()
load_hud_data()
load_urbaninstitute_data()
load_policy_data()
