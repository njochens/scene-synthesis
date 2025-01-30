import enum
import os
import torch
import numpy as np

from data.TDFront import TDFDataset
from model.models import TransformerWrapper
import train
from train import denoise_1scene, load_checkpoint


class DataPartition(str, enum.Enum):
    TRAINVAL = 'trainval'
    TEST = 'test'
    ALL = 'all'


class RoomType(str, enum.Enum):
    BEDROOM = "bedroom"
    LIVING_ROOM = "livingroom"


class EncoderType(str, enum.Enum):
    POINTNET = "pointnet"
    RESNET = "resnet"
    POINTNET_SIMPLE = "pointnet_simple"


class DenoisingMethod(str, enum.Enum):
    DIRECT_ONCE = 'direct_map_once'
    DIRECT = 'direct_map'
    GRAD = 'grad_nonoise'
    GRAD_NOISE = 'grad_noise'


class Config:

    model_path: str = "/home/Documents/weights/LEGO-Net_livingroom_409_livonly0_aug1_MSE+L1_pointnet_simple_0050000iter.pt"

    scene_dir: str = "../Documents/datasets/3DFRONT_65347/processed_livingroom_augmented/"

    two_branch: bool = False  # ???
    denoise_steer_away: bool = False

    room_type: RoomType = RoomType.LIVING_ROOM  # room type
    encoder_type: EncoderType = EncoderType.POINTNET_SIMPLE  # fp encoder type
    data_partition: DataPartition = DataPartition.TEST


class BetterTDFDataset(TDFDataset):
    def _gen_3dfront_batch_preload(
        self,
        *args,
        data_partition='test',
        random_idx=None,
        **kwargs
    ):
        if random_idx is not None:
            data = self.data_tv
            if data_partition == 'test':
                print("BETTER TDF TEST CASE")
                print('self.data_test["scenedirs"]', self.data_test["scenedirs"])
                data = self.data_test
            elif data_partition == 'all':
                print("BETTER TDF ALL CASE")
                data = dict(self.data_tv)
                data_test = dict(self.data_test)
                for key in data:
                    data[key] = np.concatenate(
                        [data[key], data_test[key]], axis=0)
            else:
                print("BETTER TDF TRAIN CASE")
                    
            print("!!!", data["scenedirs"], "und", random_idx, "müssen sich überschneiden")
            random_idx = [i for i, v in enumerate(data['scenedirs']) if v in random_idx]  # noqa
            print("BETTER TDF random_idx 2", random_idx)
        return TDFDataset._gen_3dfront_batch_preload(
            self, *args, **kwargs, data_partition=data_partition, random_idx=random_idx)


def create_model():
    tdf = BetterTDFDataset(
        Config.room_type.value,
        use_augment=False,
        livingroom_only=False,
    )
    n_obj, pos_d, ang_d, siz_d, cla_d, invsha_d, maxnfpoc, nfpbpn = tdf.maxnobj, tdf.pos_dim, tdf.ang_dim, tdf.siz_dim, tdf.cla_dim, 0, tdf.maxnfpoc, tdf.nfpbpn  # shape = size+class


    # From train.main
    train.n_obj, train.pos_d, train.ang_d, train.siz_d, train.cla_d, train.invsha_d, train.maxnfpoc, train.nfpbpn = n_obj, pos_d, ang_d, siz_d, cla_d, invsha_d, maxnfpoc, nfpbpn
    train.tdf = tdf
    train.max_iter = 1500

    input_d = pos_d + ang_d + siz_d + cla_d + invsha_d
    out_d = pos_d + ang_d
    sha_code = True if input_d > pos_d else False
    subtract_f = True

    transformer_config = {"pos_dim": pos_d, "ang_dim": ang_d, "siz_dim": siz_d, "cla_dim": cla_d,
                          "maxnfpoc": maxnfpoc, "nfpbpn": nfpbpn,
                          "invsha_d": invsha_d, "use_invariant_shape": (invsha_d > 0),
                          "ang_initial_d": 128, "siz_initial_unit": None, "cla_initial_unit": [128, 128],
                          "invsha_initial_unit": [128, 128], "all_initial_unit": [512, 512], "final_lin_unit": [256, out_d],
                          "use_two_branch": Config.two_branch, "pe_numfreq": 32, "pe_end": 128,
                          "use_floorplan": True, "floorplan_encoder_type": Config.encoder_type.value}
    model = TransformerWrapper(**transformer_config)


    if torch.cuda.device_count():
        model = torch.nn.DataParallel(model)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train.args = {
        "device": device,
        "train_batch_size": 128,
        "loss_func": None,
        "train": False,
        "data_type": "3dfront",
        "room_type": Config.room_type.value,
        "log": False,
        "logfile": "/dev/null"
        }

    train.gpucount = torch.cuda.device_count()

    train.adjust_parameters()

    model=load_checkpoint(model, Config.model_path)  # updates model, optimizer, start_epoch

    model = model.to(device)

    train.model = model

    return tdf, model, device


def evaluate(
    dataset: TDFDataset,
    model,
    scene_id: str,
    model_name: str,
    noise_level: float,
    angle_noise_level: float,
    denoise_method: DenoisingMethod,
    save_dir: str,
    device,
):
    fpprefix = 'placeholder'

    predict_absolute_pos = True
    predict_absolute_ang = True
    replica = ''

    de_padding_mask, de_scenepaths, de_fpoc, de_nfpc, de_fpmask, de_fpbpn = None, None, None, None, None, None

    scene_ids = [scene_id]
    print("MACH KEINE SZENE", scene_ids)

    de_input, de_label, de_padding_mask, de_scenepaths, de_fpoc, de_nfpc, de_fpmask, de_fpbpn = dataset.gen_3dfront(
        len(scene_ids),
        random_idx=scene_id,
        data_partition=Config.data_partition.value,
        use_emd=True,
        abs_pos=predict_absolute_pos,
        abs_ang=predict_absolute_ang,
        use_floorplan=True,
        noise_level_stddev=.1,
        angle_noise_level_stddev=np.pi / 12,
        weigh_by_class=False,
        within_floorplan=True,
        no_penetration=True,
        pen_siz_scale=0.92,
        replica=replica,
    )

    de_padding_mask = torch.tensor(de_padding_mask).to(device)
    de_fpoc, de_nfpc, de_fpmask, de_fpbpn = torch.tensor(de_fpoc).float().to(device), torch.tensor(de_nfpc).int(
    ).to(device), torch.tensor(de_fpmask).float().to(device), torch.tensor(de_fpbpn).float().to(device)
    de_input, de_label = torch.tensor(de_input).float().to(
        device), torch.tensor(de_label).float().to(device)

    # Visualizing and saving scene's initial state
    vis_input = de_input.detach().clone().cpu()
    initials, groundtruths = [], []

    model.eval()
    with torch.no_grad():
        p_m = None if de_padding_mask is None else de_padding_mask.detach().clone()
        fpoc = None if de_fpoc is None else de_fpoc.detach().clone()
        nfpc = None if de_nfpc is None else de_nfpc.detach().clone()
        fpmask = None if de_fpmask is None else de_fpmask.detach().clone()
        fpbpn = None if de_fpbpn is None else de_fpbpn.detach().clone()

        sp = os.path.join(Config.scene_dir, scene_id)
        pm = p_m[0:1] if p_m is not None else None  # noqa
        oc = fpoc[0:1] if fpoc is not None else None
        nc = nfpc[0:1] if nfpc is not None else None
        m = fpmask[0:1] if fpmask is not None else None
        bpn = fpbpn[0:1] if fpbpn is not None else None

        traj, break_idx, pos_disp_size, ang_disp_pi_size, perobj_distmoved = denoise_1scene(
            torch.Tensor(de_input),
            {
                'model_type': 'Transformer',
                'predict_absolute_pos': predict_absolute_pos,
                'predict_absolute_ang': predict_absolute_ang,
                'device': device,
                'replica': replica,
            },
            "3dfront",
            denoise_method.value,
            save_dir, f"{scene_id}_{fpprefix}-{denoise_method.value}",
            f"{scene_id} {fpprefix} ({denoise_method.value})",
            device,
            True,
            scenepath=sp,
            padding_mask=pm,
            fpoc=oc,
            nfpc=nc,
            fpmask=m,
            fpbpn=bpn,
            steer_away=Config.denoise_steer_away,
        )

    return np.array([traj]), np.array([perobj_distmoved])


def save(
    trajs,
    perobj_distmoveds,
    noise_level: float,
    angle_noise_level: float,
    model_name: str,
    save_dir: str,
    denoise_method: DenoisingMethod,
    scene_id: str,
):
    model_results = {}
    noise_perobj_distmoveds = []

    model_results[f"{denoise_method.value}_trajs"] = trajs
    # [nscene,]
    model_results[f"{denoise_method.value}_perobj_distmoveds"] = perobj_distmoveds  # noqa
    noise_perobj_distmoveds.append(np.mean(perobj_distmoveds))

    base_str = f"pos{round(noise_level, 4)}_ang{round(angle_noise_level / np.pi * 180, 2)}_{model_name}"  # noqa

    save_results = True
    if save_results:
        saveres_fp = os.path.join(
            save_dir,
            f'{base_str}_res',
        )

        random_mass_denoising = False
        if random_mass_denoising:
            saveres_fp = os.path.join(
                save_dir,
                f'{base_str}_log',
            )

        np.savez_compressed(
            saveres_fp,
            scene_id=scene_id,
            noise_level=np.array([noise_level, angle_noise_level]),
            **model_results
        )


def run_lego_net(scene_id, save_dir):
    noise_level: float = 0.3
    angle_noise_level: float = np.pi / 4
    denoise_method: DenoisingMethod = DenoisingMethod.DIRECT
    model_name: str = "liv0.1-with_steer"

    os.makedirs(save_dir, exist_ok=True)

    dataset, model, device = create_model()

    trajs, perobj_distmoveds = evaluate(
        dataset,
        model,
        noise_level=noise_level,
        angle_noise_level=angle_noise_level,
        model_name=model_name,
        denoise_method=denoise_method,
        device=device,
        save_dir=save_dir,
        scene_id=scene_id,
    )

    save(
        trajs,
        perobj_distmoveds,
        model_name=model_name,
        scene_id=scene_id,
        noise_level=noise_level,
        angle_noise_level=angle_noise_level,
        denoise_method=denoise_method,
        save_dir=save_dir,
    )

def main():
    scene_id: str = 'd19b8b80-a9af-477a-bf3f-41cd20cf840b_LivingRoom-21372_0'
    save_dir = '../Documents/results'

    tdf = TDFDataset(RoomType.LIVING_ROOM, use_augment = True)
    input, scenepath = tdf.read_one_scene(scenepath = scene_id)
    tdf.visualize_tdf_2d(input, f"TDFront_{scene_id}", f"Original", traj=None, scenepath=scenepath, show_corner=False)

    noise_level: float = 0.3
    angle_noise_level: float = np.pi / 4
    denoise_method: DenoisingMethod = DenoisingMethod.DIRECT

    model_name: str = "liv0.1-with_steer"

    
    os.makedirs(save_dir, exist_ok=True)

    dataset, model, device = create_model()

    trajs, perobj_distmoveds = evaluate(
        dataset,
        model,
        noise_level=noise_level,
        angle_noise_level=angle_noise_level,
        model_name=model_name,
        denoise_method=denoise_method,
        device=device,
        save_dir=save_dir,
        scene_id=scene_id,
    )

    save(
        trajs,
        perobj_distmoveds,
        model_name=model_name,
        scene_id=scene_id,
        noise_level=noise_level,
        angle_noise_level=angle_noise_level,
        denoise_method=denoise_method,
        save_dir=save_dir,
    )


if __name__ == '__main__':
    main()
