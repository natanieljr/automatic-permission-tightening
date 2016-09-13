import os
import shutil
import subprocess
import logging
from shutil import copyfile

from consts import DROIDMATE_INLINE_APK

logger = logging.getLogger()


class ApkInliner(object):
    tmp_directory = None
    input_directory = None
    output_directory = None

    def set_tmp_directory(self, tmp_directory):
        logging.debug("Configuring temporary APK inliner directory: %s", tmp_directory)
        self.tmp_directory = tmp_directory
        self.input_directory = os.path.join(self.tmp_directory, "apks")

        logging.debug("Input directory: %s", self.input_directory)

        if os.path.exists(self.tmp_directory):
            shutil.rmtree(self.tmp_directory)

        os.mkdir(self.tmp_directory)
        os.mkdir(self.input_directory)

        assert os.path.exists(self.input_directory)

    def __run_droidmate(self, directory):
        command = DROIDMATE_INLINE_APK
        command[-1] = command[-1] % directory
        logging.debug("Executing DroidMate command: %s", command)
        signal = subprocess.call([command], shell=True)
        assert signal == 0

    def __copy_apks_to_tmp_folder(self, apks):
        logger.debug("Copying original APKs to temporary folder (from %s to %s)", os.path.dirname(apks[0].filename), self.input_directory)
        for apk in apks:
            file_name = os.path.basename(apk.filename)
            logger.debug("Copying %s", file_name)
            src = apk.filename
            dst = os.path.join(self.input_directory, file_name)
            copyfile(src, dst)

    def __copy_inlined_apks_to_output_folder(self):
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)
        os.mkdir(self.output_directory)
        assert os.path.exists(self.output_directory)

        logger.debug("Copying inlined APKs to output folder (from %s to %s)", self.input_directory, self.output_directory)
        for f in os.listdir(self.input_directory):
            if f.lower().endswith(".apk"):
                logger.debug("Copying %s", f)
                src = os.path.join(self.input_directory, f)
                dst = os.path.join(self.output_directory, f)
                copyfile(src, dst)

    def process(self, apks):
        assert self.output_directory is not None

        # Copy APKs to temporary directory
        self.__copy_apks_to_tmp_folder(apks)

        # DroidMate's Inline command requires a directory
        directory = self.input_directory
        self.__run_droidmate(directory)

        # Copy inlined APKs to output folder
        self.__copy_inlined_apks_to_output_folder()