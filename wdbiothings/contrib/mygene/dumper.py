import os
from datetime import datetime
from mygene import MyGeneInfo
import biothings
import requests
from biothings.dataload.dumper import HTTPDumper
from wdbiothings import config
from wdbiothings.config import DATA_ARCHIVE_ROOT
import json
from dateutil import parser as du

biothings.config_for_app(config)


class MyGeneDumper(HTTPDumper):
    SRC_NAME = "mygene"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SCHEDULE = "0 4 * * 0" # “At 04:00 on Sunday.”

    taxids = "559292,123,10090,9606"
    params = dict(q="__all__", species=taxids, entrezonly="true", size="1000",
                  fields="entrezgene,ensembl,locus_tag,genomic_pos,name,symbol,uniprot,refseq,taxid," +
                         "type_of_gene,genomic_pos_hg19,MGI,SGD,HGNC")

    def __init__(self, src_name=None, src_root_folder=None, no_confirm=True, archive=True):
        super().__init__(src_name, src_root_folder, no_confirm, archive)
        print(self.src_doc)
        self.current_timestamp = datetime.strptime(self.src_doc["release"], "%Y%m%d") if self.src_doc.get('release', False) else None
        print(self.current_timestamp)
        self.new_timestamp = None

    def create_todump_list(self, force=False):
        if force or self.remote_is_newer():
            self.release = self.new_timestamp.strftime("%Y%m%d")
            self.to_dump = [{"remote": 'http://mygene.info/v3/query/',
                             "local": os.path.join(self.new_data_folder, "mygene.json")}]
            self.logger.info(
                "remote ({}) is newer than current ({})".format(self.new_timestamp, self.current_timestamp))
        else:
            self.logger.info(
                "remote ({}) is not newer than current ({})".format(self.new_timestamp, self.current_timestamp))

    def remote_is_newer(self):
        mygene_metadata = requests.get("http://mygene.info/v3/metadata").json()
        self.new_timestamp = du.parse(mygene_metadata['timestamp'])
        if self.current_timestamp is None or self.new_timestamp > self.current_timestamp:
            return True

    def download(self, remoteurl, localfile):
        """
        Use mygene client to do download
        :param remoteurl:
        :param localfile:
        :return:
        """
        self.prepare_local_folders(localfile)
        self.logger.debug("Downloading '%s'" % remoteurl)

        mg = MyGeneInfo()
        params = self.params
        q = mg.query(params['q'], fields=params['fields'], species=params['species'],
                     size=1000, fetch_all=True, entrezonly=True)
        d = list(q)
        with open(localfile, 'w') as f:
            json.dump(d, f)


class MyGeneSourcesDumper(MyGeneDumper):
    SRC_NAME = "mygene_sources"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def create_todump_list(self, force=False):
        if force or self.remote_is_newer():
            self.release = self.new_timestamp.strftime("%Y%m%d")
            self.to_dump = [{"remote": 'http://mygene.info/v3/metadata',
                             "local": os.path.join(self.new_data_folder, "metadata.json")}]
            self.logger.info(
                "remote ({}) is newer than current ({})".format(self.new_timestamp, self.current_timestamp))
        else:
            self.logger.info(
                "remote ({}) is not newer than current ({})".format(self.new_timestamp, self.current_timestamp))

    def download(self, remoteurl, localfile):
        self.prepare_local_folders(localfile)
        self.logger.debug("Downloading '%s'" % remoteurl)

        d = self.client.get(remoteurl).json()
        print(remoteurl)
        print(localfile)

        with open(localfile, 'w') as f:
            json.dump(d, f)

def main():
    dumper = MyGeneSourcesDumper()
    dumper.dump(force=True)


if __name__ == "__main__":
    main()
