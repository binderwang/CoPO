from copo.algo_ippo.ippo import DEFAULT_IPPO_CONFIG, get_ippo_config
from copo.callbacks import MultiAgentDrivingCallbacks
from copo.train.train import train
from copo.train.utils import get_train_parser
from copo.utils import validate_config_add_multiagent, get_rllib_compatible_env
from metadrive.envs.marl_envs import MultiAgentRoundaboutEnv
from ray import tune
from ray.rllib.agents.ppo.ppo import PPOTrainer, PPOTFPolicy, validate_config as PPO_valid, DEFAULT_CONFIG as PPO_CONFIG
from ray.tune.utils import merge_dicts

IPPOTrainer = PPOTrainer.with_updates(
    name="IPPO",
    default_config=merge_dicts(PPO_CONFIG, DEFAULT_IPPO_CONFIG),
    validate_config=lambda c: validate_config_add_multiagent(c, PPOTFPolicy, PPO_valid)
)

if __name__ == "__main__":
    args = get_train_parser().parse_args()
    exp_name = args.exp_name or "TEST"

    # Setup config
    stop = int(500_0000)

    config = dict(
        # ===== Environmental Setting =====
        # We can grid-search the environmental parameters!
        env=get_rllib_compatible_env(MultiAgentRoundaboutEnv),
        env_config=dict(start_seed=tune.grid_search([5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000]), ),

        # ===== Resource =====
        # So we need 2 CPUs per trial, 0.25 GPU per trial!
        num_gpus=0.25 if args.num_gpus != 0 else 0,
    )

    # Launch training
    train(
        IPPOTrainer,
        exp_name=exp_name,
        keep_checkpoints_num=5,
        stop=stop,
        config=get_ippo_config(config),
        num_gpus=args.num_gpus,
        num_seeds=1,
        test_mode=args.test,
        custom_callback=MultiAgentDrivingCallbacks,

        # fail_fast='raise',
        # local_mode=True
    )
