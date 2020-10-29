# Space Face

## Building docker images

To build an image, install docker, cd into face_generate, and run:

```bash
docker build -t spaceface_processor -f processor_docker/Dockerfile .
```

After the container is build, run this to run the container:

```bash
docker run -p 127.0.0.1:80:80/tcp --env-file=processor_docker/env.list spaceface_processor
```

SpaceFace is an app for neural face editing.
For more information, the notebooks contain the basic idea of this project.

Models used:
* InterFaceGan - for face manipulation
* StyleGan2 - for encoding latent vectors

## script for resizing images

1. watch episode of rick and morty. along the way, screenshot faces and stuff, making sure each screenshot is aboeve 512x512 (my screenshot tool previews the size of the area im screenshotting), and approximately square
2. install imagemagick and parallel (or run `nix-shell -p imagemagick7 -p parallel` )
3. go to the folder with screenshots and run:
```
find . -name '*.png' | parallel 'BASENAME="$(basename {})"; DD="$(identify -format "%[fx:min(w,h)]" $BASENAME)"; convert $BASENAME -alpha off -gravity center -crop ${DD}x${DD}+0+0 +repage -resize 512x512 512-$BASENAME'

```
Now, 
- All foo.png have been cropped to square from original AxB dimensions to CxC where C=min(A,B)
- then they were all resized to 512x512
- then saved as 512-foo.png
