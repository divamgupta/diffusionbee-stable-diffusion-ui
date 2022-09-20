

from pathlib import Path
import os

home_path = Path.home()

projects_root_path = os.path.join(home_path, ".diffusionbee")

if not os.path.isdir(projects_root_path):
    os.mkdir(projects_root_path)

import requests
import os
import hashlib
import zipfile
import random
import shutil
import time

def get_md5_file(fpath):
    return str(hashlib.md5(open(fpath, 'rb').read()).hexdigest())


defualt_downloads_root = os.path.join(projects_root_path, "downloads")


if not os.path.isdir(defualt_downloads_root):
    os.mkdir(defualt_downloads_root)


class ProgressBarDownloader(object):
    """Downloads a file and optionally shows a progressbar in the front-end. Also does not download if its already downloaded. Also supports checksum checking.
    Attributes:
        app_instance (AppInstance): The frontend app instance
        downloads_root (str): The root path where the downloaded file is stored. Defualt is the path for all projects.
        title (str): The title which will be shown in the progress bar modal in frontend.
    """

    def __init__(self, downloads_root=defualt_downloads_root,
                  title="Downloading"):
        super(ProgressBarDownloader, self).__init__()
         
        self.title = title
        self.downloads_root = downloads_root

    def is_already_downloaded(self, out_fname=None, md5_checksum=None):
        """Check if file is already downloaded, and matches the checksum
        Args:
            out_fname (str, optional): The output file name
            md5_checksum (str, optional): The md5 checksum
        Returns:
            bool: If the file is already downloaded
        """
        out_abs_path = os.path.join(self.downloads_root, out_fname)
        if not os.path.exists(out_abs_path):
            return False
        if md5_checksum is not None and get_md5_file(
                out_abs_path) != md5_checksum:
            return False
        return True

    def download(self, url, out_fname=None, md5_checksum=None,
                 verify_ssl=True, extract_zip=False, dont_use_cache=False):
        """Download the file
        Args:
            url (str): The url of the file from which to download
            out_fname (str, optional): The output file name
            md5_checksum (str, optional): The md5 checksum
            verify_ssl (bool, optional): If it should verify the ssl certificate or not.
            extract_zip (bool, optional): Extract the zip file as well.
            dont_use_cache (bool, optional): If set to true, then it will download from the beginning even if its already downloaded.
        Returns:
            str: the path of the downloaded file
        No Longer Raises:
            ValueError: Description
        """
        if out_fname is None:
            out_fname = url.split("/")[-1]

        out_abs_path = os.path.join(self.downloads_root, out_fname)

        # if(not verify_ssl) and md5_checksum is None:
        #     raise ValueError(
        #         "If you set verify_ssl=False, then you should have a md5 checksum")
        print("sdbk mlpr %d"%int(-1) )
        print("sdbk mltl Checking Model")
        
        if (not dont_use_cache) and self.is_already_downloaded(
                out_fname=out_fname, md5_checksum=md5_checksum):
            if extract_zip:
                if os.path.exists(out_abs_path.replace(".zip", "")):
                    # TODO , actually check if the extracted is valid, but then
                    # you might need spereate md5
                    return out_abs_path.replace(".zip", "")
            else:
                return out_abs_path

        with open(out_abs_path, "wb") as f:
            print("sdbk mltl " + self.title)
            response = requests.get(url, stream=True, verify=verify_ssl)
            total_length = response.headers.get('content-length')


            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                last_time = time.time()
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done_percentage = 100* (dl / total_length)

                    if time.time() - last_time > 0.1:
                        last_time = time.time()
                        print("sdbk mlpr %d"%int(done_percentage) ) # model loading percentage
                        print("sdbk mlms \"%s\""%("%.2fMB out of %.2fMB"%(dl/1000000 , total_length/1000000) ))

        print("sdbk mlpr %d"%int(-1) )
        print("sdbk mltl Checking Model")
        print("sdbk mlms")

        if md5_checksum is not None:
            assert(get_md5_file(out_abs_path) ==
                   md5_checksum), "The checksum for downloaded file failed."

        if extract_zip:
            print("sdbk mltl Extracting Model")

            assert out_abs_path.lower().endswith(".zip")
            with zipfile.ZipFile(out_abs_path, 'r') as zip_ref:
                extract_path = out_abs_path.replace(
                    ".zip", str(random.randint(0, 100000)))
                zip_ref.extractall(extract_path)
            out_abs_path = out_abs_path.replace(".zip", "")
            dest = shutil.move(extract_path, out_abs_path)


        return out_abs_path