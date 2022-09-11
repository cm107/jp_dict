from __future__ import annotations
import imghdr
import os
from typing import Any, Callable, Union, overload
from urllib.error import URLError
from bs4 import BeautifulSoup
import requests
import json
from imgurpython import ImgurClient
from datetime import datetime
import logging
from tqdm import tqdm
import glob

class ImageBackup:
    def __init__(self, unique_name: str=None, urls: list[str]=None, missing: bool=False):
        self.unique_name = unique_name
        self.urls = urls if urls is not None else []
        self.missing = missing

        self.uploaded_image_info: dict[str, Any] = None

    #region Dunder Methods
    def __str__(self) -> str:
        param_str = f'unique_name={self.unique_name}'
        if len(self.urls) > 0:
            if len(self.urls) == 1:
                param_str += f', urls={self.original_url}'
            else:
                param_str += f', urls=[..., {self.working_url}]'
        if self.was_uploaded:
            param_str += f', was_uploaded={self.was_uploaded}'
        return f'ImageBackup({param_str})'
    
    def __repr__(self) -> str:
        return self.__str__()

    def __key(self) -> tuple:
        # return tuple([self.__class__] + list(self.__dict__.values()))

        # Because unique_name should be unique, it should be enough to use just that.
        # The other class data shouldn't be used for identification.
        return tuple([self.__class__] + list([self.unique_name]))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        return NotImplemented
    #endregion

    #region Serialization
    def to_dict(self) -> dict[str, Any]:
        return dict(
            unique_name=self.unique_name,
            urls=self.urls,
            missing=self.missing,
            uploaded_image_info=self.uploaded_image_info
        )
    
    @staticmethod
    def from_dict(item_dict: dict[str, Any]) -> ImageBackup:
        late_init_dict = {}
        for key in ['uploaded_image_info']:
            late_init_dict[key] = item_dict.pop(key)
        obj = ImageBackup(**item_dict)
        for key, val in late_init_dict.items():
            setattr(obj, key, val)
        return obj
    
    def save(self, path: str):
        json.dump(self.to_dict(), open(path, 'w'), indent=2, ensure_ascii=False)
    
    @staticmethod
    def load(path: str) -> ImageBackup:
        if not os.path.isfile(path):
            raise FileNotFoundError(f'ImageBackup save not found: {path}')
        return ImageBackup.from_dict(json.load(open(path, 'r')))
    
    @staticmethod
    def save_batch(batch: list[ImageBackup], path: str):
        json.dump([val.to_dict() for val in batch], open(path, 'w'), indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_batch(path: str) -> list[ImageBackup]:
        if not os.path.isfile(path):
            raise FileNotFoundError(f'ImageBackup batch save not found: {path}')
        return [ImageBackup.from_dict(item_dict) for item_dict in json.load(open(path, 'r'))]
    #endregion

    @property
    def original_url(self) -> str:
        if len(self.urls) > 0:
            return self.urls[0]
        else:
            return None
    
    @property
    def working_url(self) -> str:
        if len(self.urls) > 0:
            return self.urls[-1]
        else:
            return None
    
    @property
    def was_uploaded(self) -> bool:
        return self.uploaded_image_info is not None
    
    def download_image(self, logger: logging.Logger=None) -> tuple[int, bytes]:
        printer = logger.error if logger is not None else print
        try:
            response = requests.get(self.working_url, timeout=5)
        except requests.exceptions.ConnectionError as e:
            printer(f"Request connection error. Failed to download image from {self.working_url}")
            printer(e)
            return -1, None
        except requests.exceptions.ReadTimeout as e:
            printer(f"Request timeout. Failed to download image from {self.working_url}")
            printer(e)
            return -1, None
        data = response.content if response.status_code == 200 else None
        return response.status_code, data
    
    def download_image_and_retry(
        self, logger: logging.Logger=None,
        max_retry_count: int=5
    ) -> tuple[bool, bytes]:
        link_is_working = True
        result = None
        for retry_count in range(max_retry_count):
            status_code, data = self.download_image(logger=logger)
            link_is_working = status_code == 200
            if not link_is_working:
                logger.info(f"Attempt {retry_count}: Failed to confirm image at {self.working_url}")
                retry_count += 1
            else:
                if retry_count > 0:
                    logger.info(f"Attempt {retry_count}: Successfully confirmed image at {self.working_url}")
                result = data
                break
        return link_is_working, result

    def save_image(self, save_folder: str, logger: logging.Logger=None):
        status_code, data = self.download_image(logger=logger)
        if status_code != 200:
            printer = logger.error if logger is not None else print
            printer(f"Failed to download image from working_url. Status code: {status_code}\n\tunique_name: {self.unique_name}, working_url: {self.working_url}")
            self.missing = True
        else:
            # https://stackoverflow.com/a/72867586/13797085
            extension = imghdr.what(file=None, h=data)
            if extension is not None:
                save_path = f"{save_folder}/{self.unique_name}.{extension}"
            else:
                save_path = f"{save_folder}/{self.unique_name}"
            with open(save_path, 'wb') as f:
                f.write(data)
            self.missing = False
            printer = logger.info if logger is not None else print
            printer(f"Created a local save of {self.unique_name}")

class ImageBackupHandler:
    def __init__(
        self,
        imgur_credentials: Union[str, dict[str, str]],
        dump_folder: str='dump',
        save_log: bool=True, silent: bool=True
    ):
        self.dump_folder = dump_folder
        os.makedirs(self.dump_folder, exist_ok=True)
        self.logger = self._init_logger(
            log_dir=f"{self.dump_folder}/logs" if save_log else None,
            silent=silent
        )
        self.client = self._setup_imgur_client(imgur_credentials)
        self.logger.info("Setup Imgur Client")
        self.logger.info(f"Dumping To Directory: {dump_folder}")
        self.backups: list[ImageBackup] = []
        self._meta_filename = 'meta.json'
        self.missing_unique_names: list[str] = []
        self.missing_urls: list[str] = []
        self._missing_filename = 'missing.json'

    #region Dunder Methods
    def __len__(self) -> int:
        return len(self.backups)
    
    @overload
    def __getitem__(self, idx: int) -> ImageBackup: ...

    @overload
    def __getitem__(self, idx: slice) -> list[ImageBackup]: ...

    def __getitem__(self, idx: Union[int, slice]) -> Union[ImageBackup, list[ImageBackup]]:
        if type(idx) is slice:
            result: list[ImageBackup] = []
            for i in range(
                idx.start if idx.start is not None else 0,
                idx.stop if idx.stop is not None else len(self),
                idx.step if idx.step is not None else 1
            ):
                result.append(self.__getitem__(i))
            return (result)
        elif type(idx) is not int:
            raise TypeError
        return self.backups[idx]

    def __iter__(self) -> ImageBackupHandler:
        self.n = 0
        return self
    
    def __next__(self) -> ImageBackup:
        if self.n < len(self):
            self.n += 1
            return self[self.n-1]
        else:
            raise StopIteration
    #endregion

    #region Serialization
    @property
    def meta_path(self) -> str:
        return f"{self.dump_folder}/{self._meta_filename}"

    @property
    def missing_path(self) -> str:
        return f"{self.dump_folder}/{self._missing_filename}"

    def save_missing(self):
        item_dict = {name: url for name, url in zip(self.missing_unique_names, self.missing_urls)}
        json.dump(item_dict, open(self.missing_path, 'w'), ensure_ascii=False, indent=2)

    def load_missing(self):
        item_dict: dict = json.load(open(self.missing_path, 'r'))
        self.missing_unique_names = list(item_dict.keys())
        self.missing_urls = list(item_dict.values())

    def save(self):
        ImageBackup.save_batch(self.backups, path=self.meta_path)
        self.logger.info(f"Saved meta. Number of image backups: {len(self.backups)}")
        self.save_missing()
        self.logger.info(f"Saved missing meta. Number of missing backups: {len(self.missing_unique_names)}")

    def load(self):
        if os.path.isfile(self.meta_path):
            self.backups = ImageBackup.load_batch(self.meta_path)
            self.logger.info(f"Loaded meta. Number of image backups: {len(self.backups)}")
        if os.path.isfile(self.missing_path):
            self.load_missing()
            self.logger.info(f"Loaded missing meta. Number of missing image backups: {len(self.missing_unique_names)}")
    #endregion

    def _setup_imgur_client(self, credentials: Union[str, dict[str, str]], authenticate: bool=False) -> ImgurClient:
        if type(credentials) is str:
            if not os.path.isfile(credentials):
                raise FileNotFoundError(f"Couldn't find imgur credentials at: {credentials}")
            imgur_credentials = json.load(open(credentials, 'r'))
        elif type(credentials) is dict:
            imgur_credentials = credentials
        else:
            raise TypeError
        client = ImgurClient(**imgur_credentials)
        if authenticate:
            authorization_url = client.get_auth_url('pin')
            print(f"Go to the following URL: {authorization_url}")
            pin = input("Enter pin code: ")
            credentials = client.authorize(pin, 'pin')
            client.set_user_auth(credentials['access_token'], credentials['refresh_token'])
            print("Authentication successful!")
            print(f"\tAccess token:  {credentials['access_token']}")
            print(f"\tRefresh token: {credentials['refresh_token']}")
        return client

    def _upload_image(
        self,
        image_path: str, album=None,
        name: str='', title: str='', description: str='',
        anon: bool=True
    ) -> dict[str: Any]:
        config = dict(album=album, name=name, title=title, description=description)
        image_info = self.client.upload_from_path(image_path, config=config, anon=anon)
        return image_info

    @staticmethod
    def _init_logger(log_dir: str=None, silent: bool=True) -> logging.Logger:
        handlers = []
        if log_dir is not None:
            os.makedirs(log_dir, exist_ok=True)
            handlers.append(logging.FileHandler(
                filename=f"{log_dir}/{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.log",
                mode='a'
            ))
            print("Added logging.FileHandler")
        if not silent:
            handlers.append(logging.StreamHandler())
            print("Added logging.StreamHandler")
        logging.basicConfig(
            format='[%(asctime)s:%(msecs)d %(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG,
            handlers=handlers
        )
        return logging.getLogger('ImageBackupHandler Logger')

    def find(self, unique_name: str) -> ImageBackup:
        for backup in self:
            if backup.unique_name == unique_name:
                return backup
        return None

    def contains(self, unique_name: str) -> bool:
        return self.find(unique_name) is not None

    def process(self, url: str, unique_name: str): # TODO: Need to combine with anki logic.
        if not self.contains(unique_name):
            backup = ImageBackup(unique_name, urls=[url])
            backup.save_image(self.dump_folder, logger=self.logger)
            self.logger.info(f'Created new backup: {backup}')
            self.backups.append(backup)
    
    @staticmethod
    def _parse_img_src(text: str) -> list[str]:
        """
        Returns a list of all img tag strings in text.
        Example:
        >>> text = 'Cool Image: <img src="URL0"><br>Another cool image: <img src="URL1">'
        >>> print(parse_img_tags(text))
            ['URL0', 'URL1']
        """
        soup = BeautifulSoup(text, features="lxml")
        tags = soup.findAll('img')
        return [tag['src'] for tag in tags]

    def process_with_anki(
        self, text: str, update_text: Callable[[str],], unique_name_prefix: str,
        missing_map: dict[str, str]=None, max_retry_count: int=5
    ) -> bool:
        """Replaces text in anki field.

        Args:
            text (str): new text
            update_text (Callable[[str],]):
                Function that updates anki field.
                Input parameter corresponds to new text after replacement.
            unique_name_prefix (str):
                Unique name that can be used for the sake of distinguishing
                between different cards/fields.
                Since there can be multiple images in any given field, a number
                will be appended to the end of this string when determining
                the actual unique_name.
                Example: unique_name_prefix = f"{parsed_fields.writing}-{parsed_fields.unique_id}-"
            missing_map (dict[str, str]):
                There may be missing urls in the existing meta.
                Missing urls are urls that were broken before they could be backed up locally.
                We cannot recover these images, but we can replace them with new ones.
                Specify the old url as the key and the new url as the value.
        
        Returns:
            True if the field was modified. False otherwise.
        """
        new_text = text
        img_urls = self._parse_img_src(text)
        updated_unique_names: list[str] = []
        
        # TODO: Modularize this?
        relevant_paths = glob.glob(f"{self.dump_folder}/{unique_name_prefix}*")
        existing_unique_names = [os.path.splitext(path[len(f"{self.dump_folder}/"):])[0] for path in relevant_paths]
        relevant_existing_backups: list[ImageBackup] = []
        for existing_unique_name in existing_unique_names:
            existing_backup = self.find(existing_unique_name)
            if existing_backup is None:
                msg = f"Failed to find existing_backup match for unique_name: {existing_unique_name}"
                self.logger.error(msg)
                raise Exception(msg)
            relevant_existing_backups.append(existing_backup)
        
        for img_url in img_urls:
            if img_url in self.missing_urls:
                missing_idx = self.missing_urls.index(img_url)
                unique_name = self.missing_unique_names[missing_idx]
                if missing_map is not None and (img_url in missing_map.keys() or unique_name in missing_map.keys()):
                    if img_url in missing_map.keys():
                        new_url = missing_map[img_url]
                    else:
                        new_url = missing_map[unique_name]
                    backup = self.find(unique_name)
                    backup.urls.append(new_url)
                    backup.save_image(self.dump_folder, logger=self.logger)
                    if backup.missing:
                        msg = f"{backup.unique_name} is still missing after replacing url.\n\told_url: {img_url}\n\tnew_url: {new_url}"
                        self.logger.error(msg)
                        raise URLError(msg)
                    new_text = new_text.replace(img_url, new_url)
                    del self.missing_unique_names[missing_idx]
                    del self.missing_urls[missing_idx]
                    updated_unique_names.append(unique_name)

                    self.logger.info(f"Successfully replaced url for {backup.unique_name}.\n\told_url: {img_url}\n\tnew_url: {new_url}")
                    continue
                else:
                    # Check the missing url again anyway. It might have simply timed out last time.
                    backup = self.find(unique_name)
                    assert backup.missing, f"Found missing that wasn't actually missing. {backup.unique_name=}"
                    backup.save_image(self.dump_folder, logger=None)
                    if not backup.missing:
                        del self.missing_unique_names[missing_idx]
                        del self.missing_urls[missing_idx]
                        self.logger.info(f"Was able to download image on repeated attempt. Missing status updated for {backup.unique_name}")
                    else:
                        self.logger.info(f"Repeated attempt to download missing, but still missing for {backup.unique_name}")
                    continue
                        
            existing_backup: ImageBackup = None
            for relevant_existing_backup in relevant_existing_backups:
                if relevant_existing_backup.working_url == img_url:
                    existing_backup = relevant_existing_backup
                    break
            if existing_backup is None: # Not yet backed up.
                i = len(relevant_existing_backups)
                i_str = str(i)
                while len(i_str) < 2:
                    i_str = f"0{i_str}"
                unique_name = f"{unique_name_prefix}{i_str}"
                backup = ImageBackup(unique_name, urls=[img_url])
                backup.save_image(self.dump_folder, logger=self.logger)
                self.logger.info(f'Created new backup: {backup}')
                self.backups.append(backup)
                relevant_existing_backups.append(backup)
                if backup.missing:
                    self.missing_unique_names.append(backup.unique_name)
                    self.missing_urls.append(img_url)
            else:
                backup = existing_backup
                if backup.missing: # Shouldn't be possible?
                    self.logger.warning(f"Link for {backup.unique_name} is missing. {backup.working_url=}")
                    continue
                else:
                    retry_count = 0 # TODO: Need to modularize this.
                    link_is_working = True
                    while retry_count < max_retry_count:
                        status_code, data = backup.download_image(logger=self.logger)
                        link_is_working = status_code == 200
                        if not link_is_working:
                            self.logger.info(f"Attempt {retry_count}: Failed to confirm image at {backup.working_url}")
                            retry_count += 1
                        else:
                            if retry_count > 0:
                                self.logger.info(f"Attempt {retry_count}: Successfully confirmed image at {backup.working_url}")
                            break
                    # link_is_working, data = backup.download_image_and_retry(
                    #     logger=self.logger, max_retry_count=max_retry_count
                    # )
                    if link_is_working:
                        continue
                    else: # TODO: Need to add to a retry queue and try again later.
                        # Upload local copy of image to imgur.
                        self.logger.warning(f"Link for {backup.unique_name} is broken. {backup.working_url=}")
                        matches = glob.glob(f"{self.dump_folder}/{backup.unique_name}.*")
                        if len(matches) == 0:
                            msg = f"Failed to find local copy of {backup.unique_name} in dump folder. Was it accidentally deleted?"
                            self.logger.error(msg)
                            raise FileNotFoundError(msg)
                        elif len(matches) > 1:
                            self.logger.warning(f"Found the same local copy of {backup.unique_name} in dump folder with different extensions. Did someone tamper with the images?")
                        local_path = matches[0]
                        if not os.path.isfile(local_path):
                            msg0 = f"Couldn't find local copy of {backup.unique_name} at: {local_path}"; self.logger.error(msg0)
                            msg1 = f"Please confirm that dump_dir is correct.\n\tdump_dir: {self.dump_folder}"; self.logger.error(msg1)
                            raise FileNotFoundError(f"{msg0}\n{msg1}")
                        image_info = self._upload_image(
                            image_path=local_path,
                            name=backup.unique_name,
                            title=backup.unique_name,
                            description=f'Backup of {backup.unique_name} on {datetime.now()}'
                        )
                        backup.uploaded_image_info = image_info
                        new_url = image_info['link']
                        new_text = new_text.replace(backup.working_url, new_url)
                        backup.urls.append(new_url)

                        # Confirm that the new link is working.
                        status_code, img = backup.download_image(logger=self.logger)
                        if status_code != 200:
                            msg = f"Uploaded backup of {backup.unique_name} to imgur, but the new url doesn't seem to be working.\n\tnew_url: {new_url}"
                            self.logger.error(msg)
                            raise URLError(msg)
                        else:
                            updated_unique_names.append(backup.unique_name)
                            self.logger.info(f"Successfully uploaded local copy of {backup.unique_name} to imgur.\n\tnew_url: {new_url}")
        if new_text != text:
            update_text(new_text)
            if len(updated_unique_names) > 0:
                self.logger.info(f"Updated image urls for the following unique names: {updated_unique_names}")
            return True
        else:
            return False
    
    def reupload_images_for_broken_links(self):
        pbar = tqdm(total=len(self), unit='backup(s)', leave=True)
        self.logger.info('Checking for broken links.')
        reupload_summary = {}
        for backup in self:
            pbar.set_description(f'Checking Backup: {backup.unique_name}')
            status_code, img = backup.download_image(logger=self.logger)
            if status_code != 200: # Broken Link. Need to upload local copy.
                # Upload local copy of image to imgur.
                self.logger.warning(f"Link for {backup.unique_name} is broken. {backup.working_url=}")
                matches = glob.glob(f"{self.dump_folder}/{backup.unique_name}.*")
                if len(matches) == 0:
                    msg = f"Failed to find local copy of {backup.unique_name} in dump folder. Was it accidentally deleted?"
                    self.logger.error(msg)
                    raise FileNotFoundError(msg)
                elif len(matches) > 1:
                    self.logger.warning(f"Found the same local copy of {backup.unique_name} in dump folder with different extensions. Did someone tamper with the images?")
                local_path = matches[0]
                if not os.path.isfile(local_path):
                    msg0 = f"Couldn't find local copy of {backup.unique_name} at: {local_path}"; self.logger.error(msg0)
                    msg1 = f"Please confirm that dump_dir is correct.\n\tdump_dir: {self.dump_folder}"; self.logger.error(msg1)
                    raise FileNotFoundError(f"{msg0}\n{msg1}")
                image_info = self._upload_image(
                    image_path=local_path,
                    name=backup.unique_name,
                    title=backup.unique_name,
                    description=f'Backup of {backup.unique_name} on {datetime.now()}'
                )
                backup.uploaded_image_info = image_info
                new_url = image_info['link']
                backup.urls.append(new_url)

                # Confirm that the new link is working.
                status_code, img = backup.download_image(logger=self.logger)
                if status_code != 200:
                    msg = f"Uploaded backup of {backup.unique_name} to imgur, but the new url doesn't seem to be working.\n\tnew_url: {new_url}"
                    self.logger.error(msg)
                    raise URLError(msg)
                else:
                    self.logger.info(f"Successfully uploaded local copy of {backup.unique_name} to imgur.\n\tnew_url: {new_url}")
                    reupload_summary[backup.unique_name] = new_url
            pbar.update()
        pbar.close()
        if len(reupload_summary) > 0:
            print_str = ''
            for key, val in reupload_summary.items():
                print_str += f"\n\t{key}->{val}"
            self.logger.info(f"The following broken links were fixed:{print_str}")

    @staticmethod
    def img_download_test():
        # https://stackoverflow.com/a/72867586/13797085
        gif_url = 'https://media.tenor.com/images/eff22afc2220e9df92a7aa2f53948f9f/tenor.gif'
        img_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwXRq7zbWry0MyqWq1Rbq12g_oL-uOoxo4Yw&usqp=CAU'
        for url, save_basename in [
            (gif_url, 'gif_download_test'),
            (img_url, 'img_download_test')
        ]:
            response = requests.get(url)
            if response.status_code != 200:
                raise URLError
            extension = imghdr.what(file=None, h=response.content)
            save_path = f"{save_basename}.{extension}"
            with open(save_path, 'wb') as f:
                f.write(response.content)

    @staticmethod
    def debug():
        imgur_credentials = '/home/clayton/workspace/prj/data_keep/data/study/jp_dict_data/imgur_credentials.json'
        dump_folder = 'test_dump'

        if os.path.isdir(dump_folder):
            # Remove existing directory for test.
            import shutil
            shutil.rmtree(dump_folder)

        handler = ImageBackupHandler(
            imgur_credentials=imgur_credentials,
            dump_folder=dump_folder,
            save_log=True, silent=False
        )

        test_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwXRq7zbWry0MyqWq1Rbq12g_oL-uOoxo4Yw&usqp=CAU'
        handler.process(url=test_url, unique_name='test0')

        print("Using fake url to represent broken link.")
        fake_url = 'https://i.imgur.com/Wb23rt5tgwsldkfYVS.jpeg'
        handler[0].urls.append(fake_url) # The fake url to represent broken link.
        handler.reupload_images_for_broken_links()
