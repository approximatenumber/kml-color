docker stop kml-color
docker run -it --rm -p 8888:8888 -v ${PWD}/app/uploads:/app/uploads -d --name kml-color kml-color
