FROM python:latest

RUN mkdir -p /app
RUN mkdir -p /app/frontend/results /app/frontend/uploads

COPY api/ /app/api
COPY api/data/ /app/data
COPY api/libdarknet/ /app/api/libdarknet
COPY frontend/ /app/frontend

COPY LICENSE /app/
COPY Makefile.patch /app/

# CHECK IF WE HAVE A GPU
#    RUN apt update && apt install lshw -yy
#    RUN lshw -c display | grep -i NVIDIA && touch GPUFLAG || echo "===== NO GPU ====="
#    RUN echo AFTER lshw; ls -l GPUFLAG
# CUDA Toolkit: https://yolovision.blob.core.windows.net/cuda/cuda-repo-ubuntu1604-9-2-local_9.2.88-1_amd64.deb

RUN git clone --depth 1 https://github.com/pjreddie/darknet
WORKDIR darknet
RUN patch -p1 Makefile < /app/Makefile.patch
RUN rm /app/Makefile.patch

RUN make && \
    echo '______ libdarknet ______' && \
    echo 'ldd: ' && \
    du -sh libdarknet.so && \
    ldd libdarknet.so && \
    echo '________________________' && \
    cp -v libdarknet.so /app/api/libdarknet/

RUN git clone --depth 1 https://github.com/snobu/falcon
WORKDIR falcon
RUN python setup.py install

RUN pip install colorama simplejson gunicorn

RUN echo Downloading weights.. && curl -s -o /app/api/libdarknet/yolov3.weights \
    http://yolovision.blob.core.windows.net/weights/yolov3.weights

WORKDIR /app/api
CMD gunicorn app:api -b 0.0.0.0 2>&1

EXPOSE 8000
