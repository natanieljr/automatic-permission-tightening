import os
import shutil
import subprocess
import logging
from shutil import copyfile
from auxiliar import mkdir

from consts import DROIDMATE_INLINE_APK

logger = logging.getLogger()


class ApkInliner(object):
    tmp_directory = None
    input_directory = None
    output_directory = None

    def set_tmp_directory(self, tmp_directory):
        """
        Configure the working directories for the APK inlining process
        :param tmp_directory: Temporary directory to store files
        :return:
        """
        logging.debug("Configuring temporary APK inliner directory: %s", tmp_directory)
        self.tmp_directory = tmp_directory
        self.input_directory = os.path.join(self.tmp_directory, "apks")

        logging.debug("Input directory: %s", self.input_directory)

        if os.path.exists(self.tmp_directory):
            shutil.rmtree(self.tmp_directory)

        mkdir(self.tmp_directory)
        mkdir(self.input_directory)

    def __run_droidmate(self):
        """
        Execute DroidMate with -inline command to inline all original APKs
        :param directory: Directory containing the original APKs
        :return:
        """
        command = DROIDMATE_INLINE_APK
        command[-1] = command[-1] % self.input_directory
        logging.debug("Executing DroidMate command: %s", command)
        signal = subprocess.call([command], shell=True)
        assert signal == 0

    def __copy_apks_to_tmp_folder(self, apks):
        """
        Copy the original APKs to the temporary directory to be processed
        :param apks: List of APKs to be copied
        :return:
        """
        logger.debug("Copying original APKs to temporary folder (from %s to %s)", os.path.dirname(apks[0].filename), self.input_directory)
        for apk in apks:
            file_name = apk.get_basename()
            logger.debug("Copying to temporary: %s", file_name)
            src = apk.filename
            dst = os.path.join(self.input_directory, file_name)
            copyfile(src, dst)

    def __copy_inlined_apks_to_output_folder(self):
        """
        Copy the inlined APKs to the output directory
        :return:
        """
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)
        os.mkdir(self.output_directory)
        assert os.path.exists(self.output_directory)

        logger.debug("Copying inlined APKs to output folder (from %s to %s)", self.input_directory, self.output_directory)
        for f in os.listdir(self.input_directory):
            if f.lower().endswith(".apk"):
                logger.debug("Copying to output %s", f)
                src = os.path.join(self.input_directory, f)
                dst = os.path.join(self.output_directory, f)
                copyfile(src, dst)

    def create_apk_mapping(self, apks):
        """
        Maps original APKs and inlined APKs
        :param apks: List of APKs to be inlined
        :return: Dictonary mapping each APK to an inlined APK
        """
        mapping = {}
        for apk in apks:
            file_name = apk.get_basename().replace('.apk', '-inlined.apk')
            if os.path.exists(os.path.join(self.output_directory, file_name)):
                mapping[apk.get_basename()] = file_name
            else:
                logger.warn("Unable to identify inlined version of apk %s", apk)

        return mapping

    def process(self, apks):
        """
        Inline the list of APKs. This process is done by calling DroidMate internally with "-inline" argument.
        Moreover, all original APKs are copied to the working directory, therefore preventing changes int he original
        :param apks: List of APKs to be inlined
        :return: Nothing
        """
        assert self.output_directory is not None

        # Copy APKs to temporary directory
        self.__copy_apks_to_tmp_folder(apks)

        # DroidMate's Inline command requires a directory
        self.__run_droidmate()

        # Copy inlined APKs to output folder
        self.__copy_inlined_apks_to_output_folder()