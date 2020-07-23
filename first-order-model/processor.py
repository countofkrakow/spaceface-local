import matplotlib
matplotlib.use('Agg')
import os, sys
import cv2
import yaml
from tqdm import tqdm
import boto3
import imageio
import numpy as np
from skimage.transform import resize
from skimage import img_as_ubyte
import torch
from sync_batchnorm import DataParallelWithCallback
from modules.generator import OcclusionAwareGenerator
from modules.keypoint_detector import KPDetector
from animate import normalize_kp
from scipy.spatial import ConvexHull
from faced import FaceDetector
from demo import make_animation
import face_alignment

log_dir = 'log'
cfg_path = 'config/vox-adv-256.yaml'
model_path = 'vox-adv-cpk.pth.tar'

def load_checkpoints(config_path, checkpoint_path):

    with open(config_path) as f:
        config = yaml.load(f)

    generator = OcclusionAwareGenerator(**config['model_params']['generator_params'],
                                        **config['model_params']['common_params'])
    generator.cuda()

    kp_detector = KPDetector(**config['model_params']['kp_detector_params'],
                             **config['model_params']['common_params'])
    kp_detector.cuda()

    checkpoint = torch.load(checkpoint_path)

    generator.load_state_dict(checkpoint['generator'])
    kp_detector.load_state_dict(checkpoint['kp_detector'])

    generator = DataParallelWithCallback(generator)
    kp_detector = DataParallelWithCallback(kp_detector)

    generator.eval()
    kp_detector.eval()

    return generator, kp_detector

def crop_video(path, frame_num, driving_video, crop_scale=2.5):
    face_detector = FaceDetector()

    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) # float
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
    cap.release()

    bboxes = face_detector.predict(driving_video[frame_num])
    x, y, w, h, _ = max(bboxes, key=lambda x: x[4])

    new_x = x - crop_scale * w // 2
    new_y = y - crop_scale * w // 2
    start_x = int(max(new_x, 0))
    start_y = int(max(new_y, 0))
    end_x = int(min(width - 1, start_x + crop_scale * w))
    end_y = int(min(height - 1, start_y + crop_scale * w))
    cropped_video = [frame[start_y:end_y, start_x:end_x] for frame in driving_video]
    return cropped_video


def find_best_frame(source, driving, cpu=False):
    import face_alignment

    def normalize_kp(kp):
        kp = kp - kp.mean(axis=0, keepdims=True)
        area = ConvexHull(kp[:, :2]).volume
        area = np.sqrt(area)
        kp[:, :2] = kp[:, :2] / area
        return kp

    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=True,
                                      device='cpu' if cpu else 'cuda')
    kp_source = fa.get_landmarks(255 * source)[0]
    kp_source = normalize_kp(kp_source)
    norm  = float('inf')
    frame_num = 0
    for i, image in tqdm(enumerate(driving)):
        kp_driving = fa.get_landmarks(255 * image)[0]
        kp_driving = normalize_kp(kp_driving)
        new_norm = (np.abs(kp_source - kp_driving) ** 2).sum()
        if new_norm < norm:
            norm = new_norm
            frame_num = i
    return frame_num

if __name__ == '__main__':
    SRC_IMG = os.environ['img']
    SRC_VIDEO = os.environ['video']
    RESULT_VIDEO = 'result.mp4'
    OUT_BUCKET = 'spaceface-out'
    crop_scale = 2.5

    with open(cfg_path) as f:
        cfg = yaml.load(f)
    os.makedirs(log_dir, exist_ok=True)

    source_image = imageio.imread(SRC_IMG)
    reader = imageio.get_reader(SRC_VIDEO)
    fps = int(reader.get_meta_data()['fps'])
    driving_video = []
    try:
        for im in reader:
            driving_video.append(im)
    except RuntimeError:
        pass
    reader.close()


    bf = find_best_frame(source_image, driving_video)
    driving_video = crop_video(SRC_VIDEO, bf, driving_video)

    # Resize input
    source_image = resize(source_image, (256, 256))[..., :3]
    driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]

    print("c")
    generator, kp_detector = load_checkpoints(config_path=cfg_path, checkpoint_path=model_path)

    predictions = make_animation(source_image, driving_video, generator, kp_detector, relative=True)

    res_fname = 'result.mp4'
    imageio.mimsave(res_fname, [img_as_ubyte(frame) for frame in predictions], fps=fps)
    fname = 'crop.mp4'
    writer = imageio.get_writer(fname, fps=fps)
    for img in driving_video:
        writer.append_data(img)

    writer.close()
    s3 = boto3.client('s3')
    s3.upload_file(res_fname, OUT_BUCKET, res_fname)
    # s3.upload_file(RESULT_VIDEO, OUT_BUCKET, RESULT_VIDEO)
    s3.upload_file(fname, OUT_BUCKET, fname)
