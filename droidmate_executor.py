import logging
import time
import shutil
import os
import subprocess
from shutil import copyfile, move

from libs.apk_adapter import APKAdapter
from consts import *

logger = logging.getLogger()


class DroidmateExecutor(object):
    reboot_wait_interval = 60

    output_directory = None
    inlined_apk_directory = None
    tmp_directory = None
    error_directory = None

    def __init__(self, inlined_apk_directory, output_directory, tmp_directory):
        self.output_directory = output_directory
        self.inlined_apk_directory = inlined_apk_directory
        self.error_directory = os.path.join(output_directory, 'fail')
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

    def __copy_results_to_output(self, apk, scenario=None):
        """
        Copy exploration results to output directory
        :param apk: Explored APK
        """
        logger.debug('Copying %s to results directory (%s)', apk, self.output_directory)
        result_directory = os.path.join(self.output_directory, apk.get_apk_name_as_directory_name())

        if scenario is not None:
            if not os.path.exists(result_directory):
                os.mkdir(result_directory)
            result_directory = os.path.join(result_directory, os.path.basename(scenario))

        if os.path.exists(result_directory):
            shutil.rmtree(result_directory)

        src = 'output_device1'
        dst = result_directory
        move(src, dst)
        assert os.path.exists(result_directory)

        for f in os.listdir('.'):
            if f.startswith('action') or f.startswith('windowHierarchyDump'):
                src = f
                dst = os.path.join(result_directory, f)
                move(src, dst)

    def __copy_results_to_fail(self, apk, scenario=None):
        """
        Copy exploration results to output directory
        :param apk: Explored APK
        """
        logger.debug('Copying %s to error directory (%s)', apk, self.error_directory)
        if not os.path.exists(self.error_directory):
            os.mkdir(self.error_directory)
        assert os.path.exists(self.error_directory)

        fail_directory = os.path.join(self.error_directory, apk.get_apk_name_as_directory_name())

        if scenario is not None:
            if not os.path.exists(fail_directory):
                os.mkdir(fail_directory)
            fail_directory = os.path.join(fail_directory, os.path.basename(scenario))

        if os.path.exists(fail_directory):
            shutil.rmtree(fail_directory)

        src = 'output_device1'
        dst = fail_directory
        move(src, dst)
        assert os.path.exists(fail_directory)

    def __clear_execution_directories(self):
        if os.path.exists('output_device1'):
            shutil.rmtree('output_device1')

        if os.path.exists('temp_extracted_resources'):
            shutil.rmtree('temp_extracted_resources')

    def __run_droidmate(self, droidmate_command):
        """
        Execute DroidMate's exploration on target APK folder
        :param droidmate_command: Command to be executed
        """
        logging.debug("Restarting device, ADB command: %s", ADB_REBOOT_COMMAND)
        os.system(ADB_REBOOT_COMMAND)
        logging.debug("Waiting %d seconds for device to reboot", self.reboot_wait_interval)
        time.sleep(self.reboot_wait_interval)
        logging.debug("Unlocking device screen, ADB command: %s", ADB_UNLOCK_SCREEN_COMMAND)
        os.system(ADB_UNLOCK_SCREEN_COMMAND)

        command = droidmate_command[:]
        command[-1] = command[-1] % self.tmp_directory
        logging.debug("Executing DroidMate command: %s", command)
        signal = subprocess.call([command], shell=True)
        #assert signal == 0
        return signal

    def __initialize(self):
        assert self.output_directory is not None
        assert self.inlined_apk_directory is not None
        assert self.tmp_directory is not None
        assert os.path.exists(self.inlined_apk_directory)

        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)
        assert os.path.exists(self.output_directory)

    def __enable_disable_xprivacy(self, enable):

        logger.warn('XPrivacy enabler/disabler not working. Have to do it manually for now')

        return

        if enable:
            logger.info('Activating XPrivacy')
        else:
            logger.info('Deactivating XPrivacy')

        command = ADB_INSTALL_COMMAND % XPRIVACY_ENABLER_BASE
        logging.debug("Installing Enabler Base, ADB command: %s", command)
        os.system(command)
        command = ADB_INSTALL_COMMAND % XPRIVACY_ENABLER_TEST
        logging.debug("Installing Enabler Test, ADB command: %s", command)
        os.system(command)

        if enable:
            command = XPRIVACY_ENABLER_RUN % 'true'
            logging.debug("Enabling XPrivacy, ADB command: %s", command)
        else:
            command = XPRIVACY_ENABLER_RUN % 'false'
            logging.debug("Disabling XPrivacy, ADB command: %s", command)

        os.system(command)

        enabler_base = APKAdapter(XPRIVACY_ENABLER_BASE)
        enabler_test = APKAdapter(XPRIVACY_ENABLER_TEST)

        command = ADB_UNINSTALL_COMMAND % enabler_test.package
        logging.debug("Uninstalling Enabler Test, ADB command: %s", command)
        os.system(command)

        command = ADB_UNINSTALL_COMMAND % enabler_base.package
        logging.debug("Uninstalling Enabler Base, ADB command: %s", command)
        os.system(command)

        logging.debug("Restarting device, ADB command: %s", ADB_REBOOT_COMMAND)
        os.system(ADB_REBOOT_COMMAND)
        logging.debug("Waiting %d seconds for device to reboot", self.reboot_wait_interval)
        time.sleep(self.reboot_wait_interval)
        logging.debug("Unlocking device screen, ADB command: %s", ADB_UNLOCK_SCREEN_COMMAND)
        os.system(ADB_UNLOCK_SCREEN_COMMAND)

    def first_exploration(self, apks, apk_mapping):
        """
        Perform the first APK exploration using Droidmate. Each APK is copied and executed alone. It's results and
        execution logs are stored separatelly into different direcotires
        :param apks: List of APKs to be explored
        :param apk_mapping: List of mapped original/inlined APKs
        """
        self.__initialize()
        self.__enable_disable_xprivacy(False)

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
                logger.debug(DROIDMATE_FIRST_RUN[1])
                result = self.__run_droidmate(DROIDMATE_FIRST_RUN)

                # # If exploration was successful
                # if result == 0:
                # Copy exploration results to output directory
                self.__copy_results_to_output(apk)
                # else:
                #     logger.warn('Error while exploring %s process signal = %d, for details check the logs at %s',
                #                 apk, result, self.error_directory)
                #     self.__copy_results_to_fail(apk)

    def run_scenario(self, apk, apk_mapping, configuration_file):
        """
        Perform the first APK exploration using Droidmate. Each APK is copied and executed alone. It's results and
        execution logs are stored separatelly into different direcotires
        :param apk: APK to be explored
        :param apk_mapping: List of mapped original/inlined APKs
        """
        self.__initialize()
        self.__enable_disable_xprivacy(True)

        # If it has an inlined version
        if apk_mapping.has_key(apk.get_basename()):
            logger.debug('Exploring APK %s with scenario %s', apk, configuration_file)
            inlined_apk_name = apk_mapping[apk.get_basename()]

            # Copy APK to temporary folder
            self.__copy_apk_to_tmp(inlined_apk_name)

            # Remove previous Droidmate execution logs
            self.__clear_execution_directories()

            # Remove configuration file, just for precaution
            command = ADB_REMOVE_CONFIG
            logging.debug("Removing previous configuration file, ADB command: %s", command)
            os.system(command)

            # Run Droidmate's scenario
            command = DROIDMATE_RUN_WITH_XPRIVACY[:]
            command[1] = command[1] % ('%s', configuration_file)
            logger.debug(command)
            result = self.__run_droidmate(command)

            self.__copy_results_to_output(apk, scenario=configuration_file)
            '''# If exploration was successful
            if result == 0:
                # Copy exploration results to output directory
                self.__copy_results_to_output(apk, scenario=configuration_file)
            else:
                logger.warn('Error while exploring %s process signal = %d, for details check the logs at %s',
                            apk, result, self.error_directory)
                self.__copy_results_to_fail(apk, scenario=configuration_file)'''
        else:
            logger.warn('Inlined version of %s not found', apk)