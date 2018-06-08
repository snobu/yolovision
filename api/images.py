import io
import os
import uuid
import mimetypes
import json
import falcon

import detector

class Resource(object):

    _CHUNK_SIZE_BYTES = 4096

    # The resource object must now be initialized with a path used during POST
    def __init__(self, storage_path):
        #self._upload_path = 'storage_path'
        self._upload_path = '../frontend/uploads'
        self._results_path = '../frontend/results'

    def on_post(self, req, resp):
        ext = mimetypes.guess_extension(req.content_type, strict=True)
        # Because Python's mimetypes insists on being silly
        if ext == '.jpe': ext = '.jpg'
        print('\n[DEBUG] GUESSED EXTENSION FROM MIME TYPE: ', ext)
        if ext not in ['.jpg', '.jpeg', '.png']:
           resp.status = falcon.HTTP_400 # Bad Request
           resp.body = '{ "error" : "Bad MIME type. Try another image." }'
           #return

        session_id = uuid.uuid4()
        name = '{session_id}{ext}'.format(session_id=session_id, ext=ext)
        image_path = os.path.join(self._upload_path, name)

        with io.open(image_path, 'wb') as image_file:
            while True:
                chunk = req.stream.read(self._CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                image_file.write(chunk)

        # Here comes the detection step,
        # Fuggedaboutit.
        print('[DEBUG] Running image through darknet...')
        print('--------------------------')
        print('image_path =', str(image_path))
        print('results/' + str(session_id) + '.png')
        print('--------------------------')
        results = detector.detect(bytes(image_path, 'ascii'),
            self._results_path + '/{session_id}'.format(session_id=session_id))

        resp.status = falcon.HTTP_200
        resp.location = '/results/' + str(session_id) + '.png'
        print(results)
        resp.body = results