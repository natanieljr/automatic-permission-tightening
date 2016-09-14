import logging
import shutil
import os
import subprocess
from shutil import copyfile, move

from consts import DROIDMATE_FIRST_RUN

logger = logging.getLogger()


class DroidmateExecutor(object):
    output_directory = None
    inlined_apk_directory = None
    tmp_directory = None

    def __init__(self, inlined_apk_directory, output_directory, tmp_directory):
        self.output_directory = output_directory
        self.inlined_apk_directory = inlined_apk_directory
        self.tmp_directory = tmp_directory

    def __copy_apk_to_tmp(self, inlined_apk_name):
        """
        Copy inlined version of the APK to the temporary
        :param inlined_apk_name: Name of the inlined APK file
        """
        logger.debug('Copying %s to temporary directory (%s)', inlined_apk_name, self.tmp_directory)
        if os.path.exists(self.tmp_directory):
            shutil.rmtree(self.tmp_directory)
        os.mkdir(self.tmp_directory)
        assert os.path.exists(self.tmp_directory)

        src = os.path.join(self.inlined_apk_directory, inlined_apk_name)
        dst = os.path.join(self.tmp_directory, inlined_apk_name)
        copyfile(src, dst)

    def __copy_results_to_output(self, apk):
        """
        Copy exploration results to output directory
        :param apk: Explored APK
        """
        logger.debug('Copying %s to results directory (%s)', apk, self.tmp_directory)
        result_directory = os.path.join(self.output_directory, apk.get_apk_name_as_directory_name())

        if os.path.exists(result_directory):
            shutil.rmtree(result_directory)

        src = 'output_device1'
        dst = result_directory
        move(src, dst)
        assert os.path.exists(result_directory)

    def __clear_execution_directories(self):
        if os.path.exists('output_device1'):
            shutil.rmtree('output_device1')

        if os.path.exists('temp_extracted_resources'):
            shutil.rmtree('temp_extracted_resources')

    def __run_droidmate(self, droidmate_command):
        """
        Execute DroidMate's exploration on target APK folder
        :param directory: Directory containing the original APKs
        """
        command = droidmate_command[:]
        command[-1] = command[-1] % self.tmp_directory
        logging.debug("Executing DroidMate command: %s", command)
        signal = subprocess.call([command], shell=True)
        assert signal == 0

    def first_exploration(self, apks, apk_mapping):
        """
        Perform the first APK exploration using Droidmate. Each APK is copied and executed alone. It's results and
        execution logs are stored separatelly into different direcotires
        :param apks: List of APKs to be inlined
        :param apk_mapping: List of mapped original/inlined APKs
        """
        assert self.output_directory is not None
        assert self.inlined_apk_directory is not None
        assert self.tmp_directory is not None
        assert os.path.exists(self.inlined_apk_directory)

        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)
        assert os.path.exists(self.output_directory)

        # Foreach APK
        for apk in apks:
            # If it has an inlined version
            if apk_mapping.has_key(apk.get_basename()):
                logger.debug('Exploring APK %s', apk)
                inlined_apk_name = apk_mapping[apk.get_basename()]

                # Copy APK to temporary folder
                self.__copy_apk_to_tmp(inlined_apk_name)

                # Remove previous Droidmate execution logs
                self.__clear_execution_directories()

                # Run Droidmate's first explorarion
                logger.debug(DROIDMATE_FIRST_RUN)
                self.__run_droidmate(DROIDMATE_FIRST_RUN)

                # Copy exploration results to output directory
                self.__copy_results_to_output(apk)
