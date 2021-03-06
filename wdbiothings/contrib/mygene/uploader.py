import json
import os

import biothings.dataload.uploader as uploader
import requests
from wdbiothings.local import JENKINS_TOKEN, JENKINS_URL

class MyGeneUploader(uploader.BaseSourceUploader):
    name = "mygene"
    main_source = "mygene"
    keep_archive = 1

    def load_data(self, data_folder):
        with open(os.path.join(data_folder, "mygene.json")) as f:
            for line in f:
                doc = json.loads(line)
                yield doc

    def post_update_data(self, *args, **kwargs):
        super().post_update_data(*args, **kwargs)
        self.logger.info("done uploading mygene")

        jobs = ['GeneBot_AGR', 'GeneBot_Homo_sapiens']
        for job in jobs:
            params = {'token': JENKINS_TOKEN,  'job': job }
            url = JENKINS_URL + "buildByToken/buildWithParameters"
            r = requests.get(url, params=params)
            self.logger.info("job {} triggered: {}".format(job, r.text))

    @classmethod
    def get_mapping(cls):
        return {}


class MyGeneSourcesUploader(uploader.BaseSourceUploader):
    name = "mygene_sources"
    main_source = "mygene_sources"
    keep_archive = 1

    def load_data(self, data_folder):
        with open(os.path.join(data_folder, "metadata.json")) as f:
            d = json.load(f)
        for doc in [d['src_version']]:
            yield doc

    @classmethod
    def get_mapping(cls):
        return {}
