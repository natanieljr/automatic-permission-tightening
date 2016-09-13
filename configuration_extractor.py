import time
import logging
import os
from consts import ADB_EXPORT_COMMAND, ADB_INSTALL_COMMAND, ADB_PULL_COMMAND, ADB_UNINSTALL_COMMAND

logger = logging.getLogger()


class XPrivacyConfigurationExtractor(object):
    output_directory = None

    def __init__(self, wait_interval=90):
        self.wait_interval = wait_interval

    def __install_apk(self, apk):
        """
        Install the APK into the device
        :param apk: APK file
        """
        install_command = ADB_INSTALL_COMMAND % apk.filename
        logger.debug("ADB command: %s" % install_command)
        status = os.system(install_command)
        assert status == 0
        logger.debug("ADB command status: %d" % status)

    def __export_configuration(self, file_name):
        """
        Execute XPrivacy's export intent and extract the configuration file.
        :param file_name: Configuration file name
        """
        export_command = ADB_EXPORT_COMMAND % file_name
        logger.debug("ADB command: %s" % export_command)
        status = os.system(export_command)
        assert status == 0
        logger.debug("Waiting %d seconds for command completion" % self.wait_interval)
        time.sleep(self.wait_interval)
        logger.debug("ADB command status: %d" % status)

    def __pull_configuration_file(self, file_name):
        """
        Pull the configuration file to the output directory
        :param file_name: File to be pulled (without path)
        """
        pull_command = ADB_PULL_COMMAND % (file_name, self.output_directory, file_name)
        logger.debug("ADB command: %s" % pull_command)
        status = os.system(pull_command)
        assert status == 0
        logger.debug("ADB command status: %d" % status)

    def __uninstall_apk(self, apk):
        """
        Uninstall the APK from the device
        :param apk: APK to be uninstalled
        """
        uninstall_command = ADB_UNINSTALL_COMMAND % apk.package
        logger.debug("ADB command: %s" % uninstall_command)
        status = os.system(uninstall_command)
        assert status == 0
        logger.debug("ADB command status: %d" % status)

    def process(self, apks):
        logger.debug("Initializing XPrivacy's configuration extraction")
        logger.debug("Configuration files will be stored in %s", self.output_directory)
        for apk in apks:
            logger.info("Extracting configuration for APK %s", apk)
            file_name = os.path.basename(apk.filename)

            # Install APK into device
            self.__install_apk(apk)

            # Export XPrivacy configuration
            self.__export_configuration(file_name)

            # Pull the configuration file
            self.__pull_configuration_file(file_name)

            # Uninstall APK
            self.__uninstall_apk(apk)

        logger.debug("Configuration extracted for all APKs")
