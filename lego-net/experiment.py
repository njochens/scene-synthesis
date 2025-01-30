import evaluate
import os
import csv
from evaluate import DataPartition, RoomType, EncoderType, DenoisingMethod, Config, run_lego_net
from data.TDFront import TDFDataset
import data.TDFront as TDFront
from data.preprocess_TDFront import write_all_data_summary_npz
import numpy as np


def main():
    # Experiment name
    experiment_name = "tv-stand"
    # Path to original dataset
    original_dataset = "../Documents/datasets/3DFRONT_65347/processed_livingroom"
    # Scene to be edited
    old_scene_id = "0a77986b-5c04-41b9-8ee8-1ea301ccda3e_LivingDiningRoom-83131"
    # Root directory
    root_directory = "../Documents/datasets/LEGO_3D"

    # Experiment folder
    experiment_folder = f"{root_directory}/{experiment_name}"
    # Dataset name
    dataset_name = f"dataset_{experiment_name}"
    # New dataset directory
    data_dir = f"{experiment_folder}/{dataset_name}/processed_livingroom"
    # Name of edited scene
    new_scene_id = f"{experiment_name}-1"
    # Scene dir configuration
    Config.scene_dir = original_dataset
    # Experiment Folder
    output_folder = f"{experiment_folder}/output"
    

    # Load Scene
    data = np.load(f"{original_dataset}/{old_scene_id}/boxes.npz")

    print(data["class_labels"])

    chair_indices = []
    # Find TV-Stand
    for i, label in enumerate(data["class_labels"]):
        if label[19] == 1.0: # 19 is the one-hot position for tv-stand 
            tv_stand_index = i
        if label[10] == 1.0:
            table_index = i
        if label[13] == 1.0:
            chair_indices.append(i)
    
    # Edit Data
    jids = data["jids"].tolist()
    class_labels = data["class_labels"].tolist()
    translations = data["translations"].tolist()
    sizes = data["sizes"].tolist()
    angles = data["angles"].tolist()

    #jids         = [jids[tv_stand_index]]
    #class_labels = [class_labels[tv_stand_index]]
    #translations = [translations[tv_stand_index]]
    #sizes        = [sizes[tv_stand_index]]
    #angles       = [angles[tv_stand_index]]

    print(chair_indices)
    translations[table_index][2] =- 0.2
    translations[table_index][0] =+ 0.2
    translations[chair_indices[1]][2] =- 0.2
    translations[chair_indices[1]][0] =+ 0


    #data_dict = {key: data[key] for key in data if (key != "class_labels" and key != "translations" and key != "sizes" and key != "angles" and key != "jids")}
    data_dict = {key: data[key] for key in data}

    # Save Scene File
    #np.savez(f"{data_dir}/filename_{new_scene_id}/boxes.npz",
    #         **data_dict,
    #         jids = jids,
    #         class_labels=class_labels,
    #         translations=translations,
    #         sizes=sizes,
    #         angles=angles)

    np.savez(f"{data_dir}/filename_{new_scene_id}/boxes.npz", **data_dict)

    # Create and save CSV
    with open(f"{experiment_folder}/{dataset_name}/{RoomType.LIVING_ROOM}_threed_front_splits.csv", "w", newline="") as file:
        csv.writer(file).writerow([f"{new_scene_id}", "test"])


    # Visualize Original Scene
    tdf = TDFDataset(RoomType.LIVING_ROOM, use_augment = False)
    tdf.scene_dir = Config.scene_dir
    input, scenepath = tdf.read_one_scene(scenepath = old_scene_id)
    tdf.visualize_tdf_2d(input, f"{output_folder}/original", title = f"Original", traj=None, scenepath=scenepath, show_corner=False)

    # Visualize Edited Scene
    TDFront.data_dir = f"{experiment_folder}/{dataset_name}"
    print("DATADIR", TDFront.data_dir)
    tdf = TDFDataset(RoomType.LIVING_ROOM, use_augment = False)
    tdf.scene_dir = data_dir
    input, scenepath = tdf.read_one_scene(scenepath = f"filename_{new_scene_id}")
    tdf.visualize_tdf_2d(input, f"{output_folder}/edited", title = f"Edited", traj=None, scenepath=scenepath, show_corner=False)
    write_all_data_summary_npz(tdf)
    write_all_data_summary_npz(tdf, trainval=True)
    import shutil
    shutil.copy(f"{data_dir}/data_tv_ctr.npz", f"{data_dir}/data_tv_ctr_livingroomonly.npz")
    shutil.copy(f"{data_dir}/data_test_ctr.npz", f"{data_dir}/data_test_ctr_livingroomonly.npz")

    # Run LEGO-Net
    evaluate.Config.scene_dir = data_dir
    run_lego_net(f"filename_{new_scene_id}", output_folder)
  

if __name__ == '__main__':
    main()

