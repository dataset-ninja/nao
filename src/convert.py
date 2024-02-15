import os
import shutil
from collections import defaultdict
from urllib.parse import unquote, urlparse

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import get_file_name, get_file_size
from supervisely.io.json import load_json_file
from tqdm import tqdm

import src.settings as s


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    ### Function should read local dataset and upload it to Supervisely project, then return project info.###
    dataset_path = "/home/alex/DATASETS/TODO/NAO/images-20231225T143843Z-001/images"
    batch_size = 30

    train_anns = "/home/alex/DATASETS/TODO/NAO/annotations-20231225T151942Z-001/annotations/instances_train.json"
    val_anns = "/home/alex/DATASETS/TODO/NAO/annotations-20231225T151942Z-001/annotations/instances_validation.json"
    test_anns = "/home/alex/DATASETS/TODO/NAO/annotations-20231225T151942Z-001/annotations/instances_test.json"

    ds_name_to_anns = {"train": train_anns, "val": val_anns, "test": test_anns}

    def create_ann(image_path):
        labels = []

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        ann_data = image_id_to_ann_data[get_file_name(image_path)]
        for curr_ann_data in ann_data:
            l_tags = []
            obj_class = category_id_to_classes.get(curr_ann_data[0])

            super_value = name_to_super.get(obj_class.name)
            super_tag = sly.Tag(super_meta, value=super_value)
            l_tags.append(super_tag)

            bbox_coord = curr_ann_data[1]
            rectangle = sly.Rectangle(
                top=int(bbox_coord[1]),
                left=int(bbox_coord[0]),
                bottom=int(bbox_coord[1] + bbox_coord[3]),
                right=int(bbox_coord[0] + bbox_coord[2]),
            )
            label_rectangle = sly.Label(rectangle, obj_class, tags=l_tags)
            labels.append(label_rectangle)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    obj_classes_names = []
    category_id_to_classes = {}
    name_to_super = {}

    super_meta = sly.TagMeta("supercategory", sly.TagValueType.ANY_STRING)

    meta = sly.ProjectMeta(tag_metas=[super_meta])

    for ds_name, ann_path in ds_name_to_anns.items():

        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        json_ann = load_json_file(ann_path)
        image_id_to_name = {}
        image_id_to_ann_data = defaultdict(list)

        categories = json_ann["categories"]
        for category in categories:
            if category["name"] not in obj_classes_names:
                if name_to_super.get(category["name"]) is None:
                    name_to_super[category["name"]] = category["supercategory"]
                obj_classes_names.append(category["name"])
                obj_class = sly.ObjClass(category["name"], sly.Rectangle)
                meta = meta.add_obj_class(obj_class)
                category_id_to_classes[category["id"]] = obj_class
                api.project.update_meta(project.id, meta.to_json())

        images_data = json_ann["images"]
        for image_data in images_data:
            image_id_to_name[image_data["_image_id"]] = image_data["file_name"]

        annotations = json_ann["annotations"]
        for ann in annotations:
            image_id_to_ann_data[ann["_image_id"]].append([ann["category_id"], ann["bbox"]])

        progress = sly.Progress("Create dataset {}".format(ds_name), len(image_id_to_ann_data))

        images_names = list(image_id_to_ann_data.keys())

        for images_names_batch in sly.batched(images_names, batch_size=batch_size):
            img_pathes_batch = [
                os.path.join(dataset_path, im_name + ".jpg") for im_name in images_names_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in img_pathes_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(images_names_batch))

    return project
